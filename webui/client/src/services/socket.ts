import { io, Socket } from 'socket.io-client';

class SocketService {
  private socket: Socket | null = null;
  private url: string = 'http://localhost:5000';
  private connecting: boolean = false;

  connect() {
    if (!this.socket || !this.connecting) {
      this.connecting = true;
      this.socket = io(this.url, {
        transports: ['polling', 'websocket'],
        reconnection: true,
        reconnectionDelay: 2000,
        reconnectionAttempts: 10,
        timeout: 10000,
      });

      this.socket.on('connect', () => {
        console.log('Socket connected:', this.socket?.id);
        this.connecting = false;
      });

      this.socket.on('disconnect', (reason) => {
        console.log('Socket disconnected:', reason);
        // 如果是服务端断开，不自动重连
        if (reason === 'io server disconnect') {
          this.connecting = false;
        }
      });

      this.socket.on('connect_error', (error) => {
        console.error('Socket connection error:', error.message);
        this.connecting = false;
      });
    }
    return this.socket;
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.connecting = false;
    }
  }

  getSocket() {
    return this.socket;
  }

  emit(event: string, data: unknown) {
    this.socket?.emit(event, data);
  }

  on(event: string, callback: (data: unknown) => void) {
    this.socket?.on(event, callback);
  }

  off(event: string) {
    this.socket?.off(event);
  }
}

export const socketService = new SocketService();
