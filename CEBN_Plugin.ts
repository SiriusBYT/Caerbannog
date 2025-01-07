import { Logger } from "replugged";

const logger = Logger.plugin("Caerbannog");

export async function start(): Promise<void> {
  const Trinity = new WebSocket("wss://localhost:6701");
  while (true) {
    Trinity.onopen = function(e) {
      logger.log(`== SN-API == Connection established with Caerbernnog Compiler.`);
      Trinity.onmessage = function(event) {
        replugged.quickCSS.reload();
      };  
    };

    Trinity.onclose = function(event) {
      if (event.wasClean) {
        logger.log(`== SN-API == Connection closed. Code=${event.code} Reason=${event.reason}.`);
      } else {
        logger.log("== SN-API == Connection closed forcefully.");
      };
    };

    Trinity.onerror = function(error) {
      logger.log("== SN-API == Unknown error");
    };
  }
}

export function stop(): void {
  logger.log(`Stopped Caerbannog.`);
}