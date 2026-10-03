const WebSocket = require('ws');

const token = process.argv[2];
const ws = new WebSocket('ws://homeassistant.local:8123/api/websocket');

ws.on('open', function open() {
  console.log('✅ WebSocket connecté');
  
  // Auth
  ws.send(JSON.stringify({
    type: 'auth',
    access_token: token
  }));
});

ws.on('message', function incoming(data) {
  const msg = JSON.parse(data);
  
  if (msg.type === 'auth_ok') {
    console.log('✅ Authentification réussie');
    
    // Call hassio service to list addons
    ws.send(JSON.stringify({
      id: 1,
      type: 'call_service',
      domain: 'hassio',
      service: 'addon_list',
      return_response: true
    }));
  } else if (msg.id === 1) {
    console.log('📦 Addons disponibles:');
    console.log(JSON.stringify(msg, null, 2));
    ws.close();
  }
});

ws.on('error', function error(err) {
  console.error('❌ WebSocket error:', err);
});

setTimeout(() => {
  console.log('Timeout');
  ws.close();
}, 10000);
