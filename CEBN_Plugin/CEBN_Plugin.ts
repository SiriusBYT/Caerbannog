import { Logger } from "replugged";

const logger = Logger.plugin("Caerbannog");
const WS_URL = "ws://localhost:6701";
const RECONNECT_DELAY = 10000;

class CaerbannogClient {
  private ws: WebSocket | null = null;
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private isShuttingDown = false;

  connect(): void {
    if (this.ws?.readyState === WebSocket.CONNECTING) return;
    
    this.ws = new WebSocket(WS_URL);
    
    this.ws.onopen = () => {
      logger.log("Connection established with Caerbannog Server");
    };

    this.ws.onmessage = (event) => {
      logger.log(`Message "${event.data}" received from the Caerbannog Server. Reloading QuickCSS!`);
      replugged.quickCSS.reload();
    };

    this.ws.onclose = () => {
      if (this.isShuttingDown) return;
      
      logger.log(`Connection lost. Retrying in ${RECONNECT_DELAY/1000} seconds...`);
      this.reconnectTimeout = setTimeout(() => this.connect(), RECONNECT_DELAY);
    };

    this.ws.onerror = (error) => {
      logger.error("WebSocket error:", error);
    };
  }

  disconnect(): void {
    this.isShuttingDown = true;
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

const client = new CaerbannogClient();

export function start(): void {
  client.connect();
}

export function stop(): void {
  client.disconnect();
  logger.log("Stopped Caerbannog");
}
