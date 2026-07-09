const WSClient = {
  ws: null,
  handlers: {},
  reconnectTimer: null,

  connect() {
    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    const url = `${proto}://${location.host}`;
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      this.emit('connected');
    };

    this.ws.onmessage = (e) => {
      let msg;
      try { msg = JSON.parse(e.data); } catch { return; }
      this.emit(msg.type, msg);
      this.emit('message', msg);
    };

    this.ws.onclose = () => {
      this.emit('disconnected');
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = setTimeout(() => this.connect(), 3000);
    };

    this.ws.onerror = () => {
      this.emit('error');
    };
  },

  send(type, payload = {}) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, ...payload }));
    }
  },

  on(type, fn) {
    if (!this.handlers[type]) this.handlers[type] = [];
    this.handlers[type].push(fn);
  },

  emit(type, data) {
    (this.handlers[type] || []).forEach((fn) => fn(data));
  },
};
