import { io, Socket } from 'socket.io-client';

class SocketService {
  private socket: Socket | null = null;
  private url: string = 'http://localhost:5000';

  connect() {
    if (!this.socket) {
      this.socket = io(this.url, {
        transports: ['websocket', 'polling'],
      });
    }
    return this.socket;
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
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
