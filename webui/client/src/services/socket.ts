import { io, Socket } from 'socket.io-client';

class SocketService {
  private socket: Socket | null = null;
  private url: string = 'http://localhost:5000';
  private connecting: boolean = false;
  private reconnectCallback: (() => void) | null = null;
  private wasConnected: boolean = false;

  connect() {
    // 如果已经连接或正在连接，直接返回现有 socket
    if (this.socket && (this.socket.connected || this.connecting)) {
      console.log('[Socket] Already connected or connecting, reusing socket');
      return this.socket;
    }

    this.connecting = true;
    console.log('[Socket] Creating new connection...');
    this.socket = io(this.url, {
      transports: ['websocket', 'polling'], // 优先使用 WebSocket
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
      timeout: 10000,
    });

    this.socket.on('connect', () => {
      console.log('[Socket] Connected, id:', this.socket?.id);
      this.connecting = false;

      // 如果是重连（之前已经连接过），触发重连回调
      if (this.wasConnected && this.reconnectCallback) {
        console.log('[Socket] This is a reconnect, triggering callback');
        this.reconnectCallback();
      }
      this.wasConnected = true;
    });

    this.socket.on('disconnect', (reason) => {
      console.log('[Socket] Disconnected:', reason);
      if (reason === 'io server disconnect') {
        this.connecting = false;
        this.wasConnected = false;
      }
    });

    this.socket.on('connect_error', (error) => {
      console.error('[Socket] Connection error:', error.message);
      this.connecting = false;
    });

    return this.socket;
  }

  onReconnect(callback: () => void) {
    this.reconnectCallback = callback;
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.connecting = false;
      this.wasConnected = false;
      this.reconnectCallback = null;
    }
  }

  getSocket() {
    return this.socket;
  }

  emit(event: string, data: unknown) {
    this.socket?.emit(event, data);
  }

  on(event: string, callback: (data: unknown) => void) {
    console.log(`[Socket] Registering listener for event: ${event}`);
    this.socket?.on(event, (data) => {
      console.log(`[Socket] Received event: ${event}`, data);
      callback(data);
    });
  }

  off(event: string) {
    if (this.socket) {
      this.socket.removeAllListeners(event);
    }
  }
}

export const socketService = new SocketService();
