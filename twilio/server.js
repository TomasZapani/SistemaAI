const express = require('express');
const WebSocket = require('ws');
const fetch = require('node-fetch');
const Groq = require('groq-sdk');
const ffmpeg = require('fluent-ffmpeg');
const { Readable } = require('stream');
const fs = require('fs');
const path = require('path');
const os = require('os');

const app = express();
const PORT = 3000;
const PYTHON_API = process.env.PYTHON_API || 'http://localhost:8000';

const groq = new Groq({
  apiKey: ''
});

app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// ============================================
// ENDPOINT PRINCIPAL
// ============================================
app.post('/voice', async (req, res) => {
  const callSid = req.body.CallSid;
  console.log('📞 Llamada entrante:', callSid, 'desde:', req.body.From);

  try {
    const startRes = await fetch(`${PYTHON_API}/session/start?call_sid=${callSid}`, {
      method: 'POST'
    });

    if (!startRes.ok) {
      throw new Error(`Python API respondió ${startRes.status}`);
    }

    const startData = await startRes.json();
    const saludo = startData.response || 'Hola, ¿en qué puedo ayudarte?';
    console.log('🐍 Sesión iniciada, saludo:', saludo);

    const twiml = `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say language="es-AR">${saludo}</Say>
  <Connect>
    <Stream url="wss://${req.headers.host}/media-stream">
      <Parameter name="callSid" value="${callSid}" />
    </Stream>
  </Connect>
</Response>`;

    res.type('text/xml');
    res.send(twiml);

  } catch (err) {
    console.error('❌ Error iniciando sesión Python:', err.message);
    res.type('text/xml');
    res.send(`<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say language="es-AR">Lo siento, hubo un error al iniciar la sesión.</Say>
  <Hangup/>
</Response>`);
  }
});

// ============================================
// WEBSOCKET
// ============================================
const wss = new WebSocket.Server({ noServer: true });

wss.on('connection', (ws) => {
  console.log('🔌 WebSocket conectado');

  let streamSid = null;
  let callSid = null;
  let audioBuffer = [];
  let isProcessing = false;

  ws.on('message', async (message) => {
    try {
      const msg = JSON.parse(message);

      switch (msg.event) {
        case 'start':
          streamSid = msg.start.streamSid;
          callSid = msg.start.customParameters?.callSid;
          console.log('🎙️ Stream iniciado. callSid:', callSid);
          break;

        case 'media':
          audioBuffer.push(msg.media.payload);

          // ~2 segundos acumulados, sin procesar en paralelo
          if (audioBuffer.length >= 100 && !isProcessing) {
            isProcessing = true;
            const buffer = [...audioBuffer];
            audioBuffer = [];
            await processAudio(buffer, ws, streamSid, callSid);
            isProcessing = false;
          }
          break;

        case 'stop':
          console.log('🛑 Stream detenido');
          if (callSid) {
            await fetch(`${PYTHON_API}/session/end?call_sid=${callSid}`, {
              method: 'DELETE'
            }).catch(e => console.error('Error cerrando sesión:', e.message));
          }
          ws.close();
          break;
      }
    } catch (err) {
      console.error('❌ Error en WebSocket:', err);
    }
  });

  ws.on('close', () => console.log('🔌 WebSocket desconectado'));
});

// ============================================
// FLUJO PRINCIPAL
// ============================================
async function processAudio(audioChunks, ws, streamSid, callSid) {
  try {
    const userText = await speechToText(audioChunks);
    if (!userText || userText.trim().length === 0) {
      console.log('🔇 Silencio detectado, ignorando...');
      return;
    }
    console.log('👤 Usuario:', userText);

    // Llamar al agente Python
    const agentRes = await fetch(
      `${PYTHON_API}/session/send?call_sid=${callSid}&message=${encodeURIComponent(userText)}`,
      { method: 'POST' }
    );

    if (!agentRes.ok) {
      throw new Error(`Python API respondió ${agentRes.status}`);
    }

    const agentData = await agentRes.json();
    const responseText = agentData.response;
    console.log('🤖 Agente:', responseText);

    // TTS → audio mulaw base64
    const audioPayload = await textToSpeech(responseText);
    if (!audioPayload) return;

    // Enviar a Twilio
    ws.send(JSON.stringify({
      event: 'media',
      streamSid: streamSid,
      media: { payload: audioPayload }
    }));

  } catch (err) {
    console.error('❌ Error en processAudio:', err.message);
  }
}

// ============================================
// STT: mulaw base64 → WAV → Whisper
// ============================================
async function speechToText(audioChunks) {
  const tmpMulaw = path.join(os.tmpdir(), `twilio_${Date.now()}.ul`);
  const tmpWav = path.join(os.tmpdir(), `twilio_${Date.now()}.wav`);

  try {
    // 1. Guardar mulaw crudo
    const rawBuffer = Buffer.from(audioChunks.join(''), 'base64');
    fs.writeFileSync(tmpMulaw, rawBuffer);

    // 2. Convertir mulaw 8kHz → WAV 16kHz con ffmpeg
    await new Promise((resolve, reject) => {
      ffmpeg()
        .input(tmpMulaw)
        .inputOptions([
          '-f', 'mulaw',      // formato de entrada
          '-ar', '8000',      // sample rate de Twilio
          '-ac', '1'          // mono
        ])
        .outputOptions([
          '-ar', '16000',     // Whisper prefiere 16kHz
          '-ac', '1',
          '-f', 'wav'
        ])
        .output(tmpWav)
        .on('end', resolve)
        .on('error', reject)
        .run();
    });

    // 3. Enviar WAV a Groq Whisper
    const { toFile } = require('groq-sdk');
    const wavBuffer = fs.readFileSync(tmpWav);
    const audioFile = await toFile(wavBuffer, 'audio.wav', { type: 'audio/wav' });

    const transcription = await groq.audio.transcriptions.create({
      file: audioFile,
      model: 'whisper-large-v3',
      language: 'es'
    });

    return transcription.text;

  } catch (err) {
    console.error('❌ Error STT:', err.message);
    return '';
  } finally {
    // Limpiar archivos temporales
    [tmpMulaw, tmpWav].forEach(f => {
      try { fs.unlinkSync(f); } catch {}
    });
  }
}

// ============================================
// TTS: Texto → mulaw base64 (ElevenLabs)
// ============================================
async function textToSpeech(text) {
  const ELEVENLABS_API_KEY = process.env.ELEVENLABS_API_KEY;
  const VOICE_ID = process.env.ELEVENLABS_VOICE_ID || 'EXAVITQu4vr4xnSDxMaL'; // "Bella" por defecto

  if (!ELEVENLABS_API_KEY) {
    console.warn('⚠️  ELEVENLABS_API_KEY no configurada');
    return null;
  }

  const tmpMp3 = path.join(os.tmpdir(), `tts_${Date.now()}.mp3`);
  const tmpMulaw = path.join(os.tmpdir(), `tts_${Date.now()}.ul`);

  try {
    // 1. Obtener audio de ElevenLabs (mp3)
    const response = await fetch(
      `https://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID}`,
      {
        method: 'POST',
        headers: {
          'xi-api-key': ELEVENLABS_API_KEY,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text: text,
          model_id: 'eleven_multilingual_v2',
          voice_settings: {
            stability: 0.5,
            similarity_boost: 0.75
          }
        })
      }
    );

    if (!response.ok) {
      throw new Error(`ElevenLabs error: ${response.status}`);
    }

    // 2. Guardar mp3
    const audioBuffer = await response.buffer();
    fs.writeFileSync(tmpMp3, audioBuffer);

    // 3. Convertir mp3 → mulaw 8kHz (formato de Twilio)
    await new Promise((resolve, reject) => {
      ffmpeg()
        .input(tmpMp3)
        .outputOptions([
          '-ar', '8000',
          '-ac', '1',
          '-f', 'mulaw'
        ])
        .output(tmpMulaw)
        .on('end', resolve)
        .on('error', reject)
        .run();
    });

    // 4. Leer y devolver como base64
    const mulawBuffer = fs.readFileSync(tmpMulaw);
    return mulawBuffer.toString('base64');

  } catch (err) {
    console.error('❌ Error TTS:', err.message);
    return null;
  } finally {
    [tmpMp3, tmpMulaw].forEach(f => {
      try { fs.unlinkSync(f); } catch {}
    });
  }
}

// ============================================
// HTTP + WebSocket
// ============================================
const server = app.listen(PORT, () => {
  console.log(`🚀 Servidor en http://localhost:${PORT}`);
  console.log(`🐍 Python API en: ${PYTHON_API}`);
  console.log(`\n📋 Variables necesarias:`);
  console.log(`   ELEVENLABS_API_KEY=${process.env.ELEVENLABS_API_KEY ? '✅' : '❌ falta'}`);
  console.log(`   PYTHON_API=${PYTHON_API}\n`);
});

server.on('upgrade', (request, socket, head) => {
  if (request.url === '/media-stream') {
    wss.handleUpgrade(request, socket, head, (ws) => {
      wss.emit('connection', ws, request);
    });
  }
});