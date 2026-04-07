# 🤖 Twilio AI Agent con Claude

Agente de IA conversacional que atiende llamadas telefónicas usando Twilio y Claude.

## 📋 Requisitos previos

1. **Cuenta de Twilio** con un número de teléfono
2. **API Key de Anthropic** (Claude)
3. **Servicio de STT** (Speech-to-Text): Deepgram, AssemblyAI o Google Cloud
4. **Servicio de TTS** (Text-to-Speech): ElevenLabs, Google Cloud o Amazon Polly
5. **ngrok** para exponer tu servidor local

## 🚀 Instalación rápida

### 1. Instalar dependencias
```bash
npm install
```

### 2. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus API keys
```

### 3. Iniciar el servidor
```bash
npm start
```

### 4. Exponer con ngrok
```bash
ngrok http 3000
```

### 5. Configurar Twilio
1. Ir a tu [Twilio Console](https://console.twilio.com/)
2. Seleccionar tu número de teléfono
3. En "A call comes in" → Webhook → pegar: `https://TU-URL-NGROK.ngrok-free.app/voice`
4. Método: `POST`

## 🏗️ Arquitectura

```
┌─────────┐      ┌─────────┐      ┌──────────┐      ┌─────────┐
│ Llamada │─────▶│ Twilio  │◀────▶│  Server  │◀────▶│ Claude  │
│telefónica│      │(WebSocket)     │ Node.js  │      │   API   │
└─────────┘      └─────────┘      └──────────┘      └─────────┘
                                        │
                                   ┌────┴────┐
                                   │         │
                                 ┌─▼──┐   ┌─▼──┐
                                 │STT │   │TTS │
                                 └────┘   └────┘
```

**Flujo:**
1. Usuario llama → Twilio recibe llamada
2. Twilio abre WebSocket con tu servidor
3. Audio del usuario → STT → Texto
4. Texto → Claude API → Respuesta
5. Respuesta → TTS → Audio
6. Audio → Twilio → Usuario escucha

## 🔧 Servicios recomendados (menor latencia)

### Speech-to-Text (STT)
- **🥇 Deepgram** - Mejor latencia (~300ms)
- AssemblyAI - Buena calidad
- Google Cloud STT - Robusto pero más lento

### Text-to-Speech (TTS)
- **🥇 ElevenLabs** - Voz natural, baja latencia
- Google Cloud TTS - Buena calidad
- Amazon Polly - Económico

## 📝 Próximos pasos

El código base está listo, pero necesitás implementar las funciones de STT y TTS:

### Opción 1: Deepgram + ElevenLabs (Recomendado)
```bash
npm install @deepgram/sdk elevenlabs-node
```

### Opción 2: Google Cloud (todo en uno)
```bash
npm install @google-cloud/speech @google-cloud/text-to-speech
```

### Opción 3: AssemblyAI + Amazon Polly
```bash
npm install assemblyai aws-sdk
```

## 🐛 Troubleshooting

### Error 404 en Twilio
- Verificá que el servidor esté corriendo
- Verificá que la URL de ngrok esté actualizada en Twilio
- Revisá que la ruta sea exactamente `/voice`

### Sin audio en la llamada
- Verificá que los servicios STT/TTS estén configurados
- Revisá los logs de la consola
- Verificá que las API keys sean válidas

### Latencia alta
- Usá Deepgram para STT (es el más rápido)
- Usá ElevenLabs para TTS
- Reducí max_tokens en Claude (~150-300 para respuestas cortas)

## 📚 Recursos

- [Twilio Media Streams](https://www.twilio.com/docs/voice/twiml/stream)
- [Claude API Docs](https://docs.anthropic.com/)
- [Deepgram Docs](https://developers.deepgram.com/)
- [ElevenLabs Docs](https://docs.elevenlabs.io/)

## 💡 Mejoras futuras

- [ ] Implementar STT/TTS (elegir proveedores)
- [ ] Agregar detección de fin de frase
- [ ] Implementar interrupciones (usuario interrumpe al bot)
- [ ] Agregar logging y analytics
- [ ] Implementar rate limiting
- [ ] Agregar tests
- [ ] Deploy en producción (Railway, Fly.io, AWS)
