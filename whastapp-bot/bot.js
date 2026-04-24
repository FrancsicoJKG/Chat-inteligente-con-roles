const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');

const API_URL = 'http://localhost:8000/api';

const sesiones = {};
const ROLES = {
  '1': 'profesor',
  '2': 'programador',
  '3': 'psicologo',
  '4': 'negocios',
  '5': 'agente_empresa'
};

function getSesion(numero) {
  if (!sesiones[numero]) {
    sesiones[numero] = { rol: 'profesor', sesion_id: null, esperando_rol: false };
  }
  return sesiones[numero];
}

const client = new Client({
  authStrategy: new LocalAuth(),
  puppeteer: {
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  }
});

client.on('qr', (qr) => {
  console.clear();
  console.log('===========================================');
  console.log('  Escanea este QR con WhatsApp:');
  console.log('  WhatsApp > tres puntos > Dispositivos vinculados');
  console.log('===========================================\n');
  qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
  console.log('\n✅ WhatsApp Bot conectado y listo!');
  console.log('📱 Envía un mensaje al número vinculado para probar\n');
});

client.on('auth_failure', () => {
  console.log('❌ Error de autenticación. Borra la carpeta .wwebjs_auth y reintenta.');
});

client.on('message', async (msg) => {
  // Ignorar grupos y mensajes propios
  if (msg.from.includes('@g.us')) return;
  if (msg.fromMe) return;

  const numero = msg.from;
  const texto = msg.body.trim();
  const s = getSesion(numero);

  // /start o /ayuda
  if (texto === '/start' || texto === '/ayuda') {
    await msg.reply(
      `👋 *Bienvenido al Chat IA con Roles!*\n\n` +
      `🎭 Rol actual: *${s.rol}*\n\n` +
      `📌 *Comandos:*\n` +
      `/rol — Cambiar rol\n` +
      `/nuevo — Nueva conversación\n` +
      `/ayuda — Ver este menú\n\n` +
      `✍️ Escribe tu pregunta directamente!`
    );
    return;
  }

  // /rol
  if (texto === '/rol') {
    s.esperando_rol = true;
    await msg.reply(
      `🎭 *Elige un rol respondiendo con el número:*\n\n` +
      `1️⃣ Profesor — Explicaciones claras\n` +
      `2️⃣ Programador — Código y técnica\n` +
      `3️⃣ Psicólogo — Apoyo emocional\n` +
      `4️⃣ Negocios — Estrategia empresarial\n` +
      `5️⃣ Agente empresa — Atención al cliente`
    );
    return;
  }

  // Eligiendo rol
  if (s.esperando_rol && ROLES[texto]) {
    s.rol = ROLES[texto];
    s.sesion_id = null;
    s.esperando_rol = false;
    await msg.reply(`✅ Rol cambiado a: *${s.rol}*\nYa puedes hacer tu pregunta!`);
    return;
  }

  // /nuevo
  if (texto === '/nuevo') {
    s.sesion_id = null;
    await msg.reply('🔄 Nueva conversación iniciada.');
    return;
  }

  // Pregunta normal — enviar a FastAPI
  try {
    await client.sendMessage(numero, '⏳ _Procesando tu pregunta..._');

    const response = await axios.post(`${API_URL}/chat`, {
      pregunta: texto,
      rol_id: s.rol,
      modelo: 'llama3',
      sesion_id: s.sesion_id
    }, { timeout: 120000 });

    s.sesion_id = response.data.sesion_id;
    const respuesta = response.data.respuesta;

    // Dividir si es muy larga (límite WhatsApp: 4096 chars)
    if (respuesta.length > 4000) {
      for (let i = 0; i < respuesta.length; i += 4000) {
        await msg.reply(respuesta.slice(i, i + 4000));
      }
    } else {
      await msg.reply(respuesta);
    }

  } catch (error) {
    if (error.code === 'ECONNREFUSED') {
      await msg.reply('❌ El servidor no responde. Verifica que FastAPI esté corriendo.');
    } else {
      await msg.reply('❌ Error procesando tu pregunta. Intenta de nuevo.');
      console.error('Error:', error.message);
    }
  }
});

console.log('🚀 Iniciando WhatsApp Bot...');
client.initialize();
