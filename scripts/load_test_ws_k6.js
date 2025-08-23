// Minimal k6 WS smoke (tokenless echo). Adjust WS_URL if needed.
import ws from 'k6/ws';
import { check, sleep } from 'k6';

export let options = { vus: 1, iterations: 1 };

export default function () {
  const url = __ENV.WS_URL || 'ws://localhost:8000/ws/audio';
  const params = {};
  const res = ws.connect(url, params, function (socket) {
    socket.on('open', function () {
      // send 100 fake 20ms frames (~2s)
      let frames = 0;
      let send = () => {
        if (frames++ < 100) {
          socket.sendBinary(new Uint8Array(320).buffer);
          setTimeout(send, 20);
        } else {
          socket.close();
        }
      };
      setTimeout(send, 100);
    });
  });
  check(res, { 'ws connected': r => r && r.status === 101 });
  sleep(1);
}
