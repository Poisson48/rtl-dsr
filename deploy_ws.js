const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');

const token = process.argv[2];
const action = process.argv[3] || 'deploy';

const ws = new WebSocket('ws://homeassistant.local:8123/api/websocket');

let messageId = 1;

function sendMessage(msg) {
  msg.id = messageId++;
  ws.send(JSON.stringify(msg));
  return msg.id;
}

ws.on('open', function open() {
  console.log('✅ WebSocket connecté');
  ws.send(JSON.stringify({
    type: 'auth',
    access_token: token
  }));
});

ws.on('message', function incoming(data) {
  const msg = JSON.parse(data);
  
  if (msg.type === 'auth_ok') {
    console.log('✅ Authentification réussie');
    
    if (action === 'deploy') {
      console.log('📦 Déploiement de l\'intégration RTL-SDR...');
      createDirectories();
    } else if (action === 'restart') {
      console.log('🔄 Redémarrage de Home Assistant...');
      sendMessage({
        type: 'call_service',
        domain: 'homeassistant',
        service: 'restart'
      });
      setTimeout(() => ws.close(), 2000);
    } else if (action === 'verify') {
      console.log('🔍 Vérification des fichiers...');
      sendMessage({
        type: 'execute_command',
        command: 'ls -la /config/custom_components/rtl_dsr/'
      });
    }
  } else if (msg.id && msg.result !== undefined) {
    console.log('✅ Réponse:', JSON.stringify(msg.result, null, 2));
    
    if (action === 'deploy') {
      handleDeployResponse(msg);
    } else {
      ws.close();
    }
  } else if (msg.id && msg.error) {
    console.error('❌ Erreur:', JSON.stringify(msg.error, null, 2));
    ws.close();
  }
});

ws.on('error', function error(err) {
  console.error('❌ WebSocket error:', err);
});

// Deployment functions
const filesToDeploy = [
  { local: 'custom_components/rtl_dsr/manifest.json', remote: '/config/custom_components/rtl_dsr/manifest.json' },
  { local: 'custom_components/rtl_dsr/const.py', remote: '/config/custom_components/rtl_dsr/const.py' },
  { local: 'custom_components/rtl_dsr/config_flow.py', remote: '/config/custom_components/rtl_dsr/config_flow.py' },
  { local: 'custom_components/rtl_dsr/coordinator.py', remote: '/config/custom_components/rtl_dsr/coordinator.py' },
  { local: 'custom_components/rtl_dsr/model.py', remote: '/config/custom_components/rtl_dsr/model.py' },
  { local: 'custom_components/rtl_dsr/entity.py', remote: '/config/custom_components/rtl_dsr/entity.py' },
  { local: 'custom_components/rtl_dsr/__init__.py', remote: '/config/custom_components/rtl_dsr/__init__.py' },
  { local: 'custom_components/rtl_dsr/sensor.py', remote: '/config/custom_components/rtl_dsr/sensor.py' },
  { local: 'custom_components/rtl_dsr/binary_sensor.py', remote: '/config/custom_components/rtl_dsr/binary_sensor.py' },
  { local: 'custom_components/rtl_dsr/number.py', remote: '/config/custom_components/rtl_dsr/number.py' },
  { local: 'custom_components/rtl_dsr/select.py', remote: '/config/custom_components/rtl_dsr/select.py' },
  { local: 'custom_components/rtl_dsr/switch.py', remote: '/config/custom_components/rtl_dsr/switch.py' },
  { local: 'custom_components/rtl_dsr/button.py', remote: '/config/custom_components/rtl_dsr/button.py' },
  { local: 'custom_components/rtl_dsr/text.py', remote: '/config/custom_components/rtl_dsr/text.py' },
  { local: 'custom_components/rtl_dsr/services.py', remote: '/config/custom_components/rtl_dsr/services.py' },
  { local: 'custom_components/rtl_dsr/services.yaml', remote: '/config/custom_components/rtl_dsr/services.yaml' },
  { local: 'custom_components/rtl_dsr/strings.json', remote: '/config/custom_components/rtl_dsr/strings.json' },
  { local: 'custom_components/rtl_dsr/websocket_api.py', remote: '/config/custom_components/rtl_dsr/websocket_api.py' },
  { local: 'custom_components/rtl_dsr/translations/fr.json', remote: '/config/custom_components/rtl_dsr/translations/fr.json' },
  { local: 'panel/sdrplusplus/card.js', remote: '/config/www/rtl_dsr/card.js' },
  { local: 'panel/sdrplusplus/sdr-plus-plus-card.js', remote: '/config/www/rtl_dsr/sdr-plus-plus-card.js' }
];

let currentFileIndex = 0;
let deployStep = 'mkdir';

function createDirectories() {
  console.log('📁 Création des dossiers...');
  sendMessage({
    type: 'execute_command',
    command: 'mkdir -p /config/custom_components/rtl_dsr/translations && mkdir -p /config/www/rtl_dsr && echo "OK"'
  });
}

function handleDeployResponse(msg) {
  if (deployStep === 'mkdir') {
    deployStep = 'files';
    deployNextFile();
  } else if (deployStep === 'files') {
    deployNextFile();
  }
}

function deployNextFile() {
  if (currentFileIndex >= filesToDeploy.length) {
    console.log('');
    console.log('✅✅✅ Tous les fichiers déployés avec succès ! ✅✅✅');
    console.log('');
    console.log('📋 Prochaines étapes :');
    console.log('   1. Redémarrez Home Assistant');
    console.log('   2. Ajoutez l\'intégration RTL-SDR (Paramètres → Appareils et services)');
    console.log('   3. Ajoutez la ressource Lovelace : /local/rtl_dsr/card.js');
    console.log('   4. Ajoutez une carte : type: custom:sdr-plus-plus-card');
    ws.close();
    return;
  }
  
  const file = filesToDeploy[currentFileIndex];
  const content = fs.readFileSync(file.local, 'utf8');
  const base64 = Buffer.from(content).toString('base64');
  
  const progress = `[${currentFileIndex + 1}/${filesToDeploy.length}]`;
  console.log(`${progress} 📄 ${path.basename(file.local)}`);
  
  sendMessage({
    type: 'execute_command',
    command: `echo '${base64}' | base64 -d > ${file.remote} && echo "OK"`
  });
  
  currentFileIndex++;
}

setTimeout(() => {
  console.log('⏱️ Timeout atteint');
  ws.close();
}, 120000);
