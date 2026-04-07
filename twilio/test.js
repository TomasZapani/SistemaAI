const fetch = require('node-fetch');

const PYTHON_API = 'http://localhost:8001';
const CALL_SID = 'test-123';

async function test() {
  // 1. Iniciar sesión
  console.log('--- Iniciando sesión ---');
  const start = await fetch(`${PYTHON_API}/session/start?call_sid=${CALL_SID}`, { method: 'POST' });
  const startData = await start.json();
  console.log('Saludo:', startData.response);

  // 2. Enviar mensajes
  const mensajes = [
    'Hola, quiero un turno para mañana a la 1 de la tarde a nombre de Juan Pérez para hacerme manicura clasica',
    'Mi numero es 3122121. Pago al salir despues de la manicura',
    'Gracias, hasta luego'
  ];

  for (const msg of mensajes) {
    console.log(`\n👤 Usuario: ${msg}`);
    const res = await fetch(
      `${PYTHON_API}/session/send?call_sid=${CALL_SID}&message=${encodeURIComponent(msg)}`,
      { method: 'POST' }
    );
    const data = await res.json();
    console.log(`🤖 Agente: ${data.response}`);
  }

  // 3. Cerrar sesión
  await fetch(`${PYTHON_API}/session/end?call_sid=${CALL_SID}`, { method: 'DELETE' });
  console.log('\n--- Sesión cerrada ---');
}

test().catch(console.error);