import { Logger } from "replugged";

const logger = Logger.plugin("Caerbannog");

export async function start(): Promise<void> {
  let Trinity = undefined;

  while (typeof Trinity == "undefined") {
    try {
      Trinity = new WebSocket("wss://localhost:6701");
    } catch {
      logger.log(`== SN-API == Failed to connect to the Caerbannog Server. Retrying in 1 second...`);
      sleep(1000);
    }
  };

  Trinity.addEventListener("open", (event) => {
    logger.log(`== SN-API == Connection established with Caerbannog Server.`);
  });
  Trinity.addEventListener("message", (event) => {
    logger.log(`== SN-API == Message "${event.data}" received from the Caerbannog Server. Reloading QuickCSS!`);
    replugged.quickCSS.reload();
  });
  Trinity.addEventListener("error", (event) => {
    logger.log(`== SN-API == Unknown error`);
  });
  Trinity.addEventListener("close", (event) => {
    if (event.wasClean) {
      logger.log(`== SN-API == Connection closed. Code=${event.code} Reason=${event.reason}.`);
    } else {
      logger.log("== SN-API == Connection closed forcefully.");
    };
  });
};

function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export function stop(): void {
  logger.log(`Stopped Caerbannog.`);
}
