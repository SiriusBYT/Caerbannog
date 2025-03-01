import { Logger } from "replugged";

const logger = Logger.plugin("Caerbannog");
const WS_URL = "ws://localhost:6701";
const RECONNECT_DELAY = 10000;

class CaerbannogClient {
  private ws: WebSocket | null = null;
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private isShuttingDown = false;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  connect(): void {
    if (this.ws?.readyState === WebSocket.CONNECTING) return;
    
    try {
      this.ws = new WebSocket(WS_URL);
      
      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
      this.ws.onerror = this.handleError.bind(this);
    } catch (error) {
      logger.error("Failed to create WebSocket connection:", error);
      this.scheduleReconnect();
    }
  }

  private handleOpen(): void {
    this.reconnectAttempts = 0;
    logger.log("Connection established with Caerbannog Server");
  }

  private handleMessage(event: MessageEvent): void {
    try {
      logger.log(`Message "${event.data}" received from the Caerbannog Server. Reloading QuickCSS!`);
      replugged.quickCSS.reload();
    } catch (error) {
      logger.error("Error handling message:", error);
    }
  }

  private handleClose(event: CloseEvent): void {
    if (this.isShuttingDown) return;
    
    logger.log(`Connection closed (${event.code}): ${event.reason || "No reason provided"}`);
    this.scheduleReconnect();
  }

  private handleError(error: Event): void {
    logger.error("WebSocket error:", error);
  }

  private scheduleReconnect(): void {
    if (this.isShuttingDown) return;
    
    this.reconnectAttempts++;
    
    if (this.reconnectAttempts > this.maxReconnectAttempts) {
      logger.error(`Failed to reconnect after ${this.maxReconnectAttempts} attempts. Giving up.`);
      return;
    }
    
    const delay = RECONNECT_DELAY * Math.min(this.reconnectAttempts, 3);
    logger.log(`Reconnecting (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}) in ${delay/1000} seconds...`);
    
    this.reconnectTimeout = setTimeout(() => this.connect(), delay);
  }

  disconnect(): void {
    this.isShuttingDown = true;
    
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    
    if (this.ws) {
      try {
        this.ws.close(1000, "Plugin stopped");
      } catch (error) {
        logger.error("Error closing WebSocket:", error);
      } finally {
        this.ws = null;
      }
    }
  }
}

const client = new CaerbannogClient();

export function start(): void {
  logger.log("Starting Caerbannog plugin");
  client.connect();
}

export function stop(): void {
  client.disconnect();
  logger.log("Stopped Caerbannog plugin");
}
