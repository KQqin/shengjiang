const express = require('express');
const http = require('http');
const path = require('path');
const fs = require('fs');
const { attachWebSocket } = require('./ws');

const app = express();
const root = path.join(__dirname, '..');
const frontendH5 = path.join(root, '../../frontend/dist/build/h5');

app.use('/shared', express.static(path.join(root, 'shared')));

// uni-app H5 构建产物（云部署优先）
if (fs.existsSync(path.join(frontendH5, 'index.html'))) {
  app.use(express.static(frontendH5));
  app.get(/^\/(?!shared).*/, (_req, res) => {
    res.sendFile(path.join(frontendH5, 'index.html'));
  });
} else {
  // 开发兼容：旧版静态页
  app.use('/client', express.static(path.join(root, 'client')));
  app.use('/course', express.static(path.join(root, '../homepage-mockup')));
  app.get('/', (_req, res) => res.redirect('/client/host.html'));
}

const server = http.createServer(app);
attachWebSocket(server);

const PORT = process.env.PORT || 3001;
server.listen(PORT, '0.0.0.0', () => {
  console.log(`剧本杀服务: http://localhost:${PORT}`);
  if (fs.existsSync(path.join(frontendH5, 'index.html'))) {
    console.log(`uni-app H5: http://localhost:${PORT}/`);
  } else {
    console.log(`教师大屏: http://localhost:${PORT}/client/host.html`);
    console.log(`学生端:   http://localhost:${PORT}/client/role.html`);
  }
});
