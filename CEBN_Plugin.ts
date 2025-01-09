import { Logger } from "replugged";

const logger = Logger.plugin("Caerbannog");

export async function start(): Promise<void> {
  while (true) {
    try {
      let Trinity = new WebSocket("wss://localhost:6701");
      AddEvents(Trinity);
    } catch {
      logger.log(`== SN-API == Failed to connect to the Caerbannog Server. Retrying in 1 second...`);
      sleep(1000);
    }
  };
};

function AddEvents(Socket: WebSocket) {
  Socket.addEventListener("open", (event) => {
    logger.log(`== SN-API == Connection established with Caerbannog Server.`);
  });
  Socket.addEventListener("message", (event) => {
    logger.log(`== SN-API == Message "${event.data}" received from the Caerbannog Server. Reloading QuickCSS!`);
    replugged.quickCSS.reload();
  });
  Socket.addEventListener("error", (event) => {
    logger.log(`== SN-API == Unknown error`);
  });

  Socket.addEventListener("close", (event) => {
    if (event.wasClean) {
      logger.log(`== SN-API == Connection closed. Code=${event.code} Reason=${event.reason}.`);
    } else {
      logger.log("== SN-API == Connection closed forcefully.");
    };
  });
}

function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export function stop(): void {
  logger.log(`Stopped Caerbannog.`);
}
