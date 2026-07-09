const express = require('express');
const http = require('http');
const path = require('path');
const { attachWebSocket } = require('./ws');

const app = express();
const root = path.join(__dirname, '..');

app.use('/client', express.static(path.join(root, 'client')));
app.use('/shared', express.static(path.join(root, 'shared')));
app.use('/course', express.static(path.join(root, '../homepage-mockup')));

app.get('/', (_req, res) => res.redirect('/client/host.html'));

const server = http.createServer(app);
attachWebSocket(server);

const PORT = process.env.PORT || 3001;
server.listen(PORT, '0.0.0.0', () => {
  console.log(`剧本杀服务: http://localhost:${PORT}`);
  console.log(`教师大屏: http://localhost:${PORT}/client/host.html`);
  console.log(`学生端:   http://localhost:${PORT}/client/role.html`);
});
