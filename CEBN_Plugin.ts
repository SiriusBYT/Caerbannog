import { Logger } from "replugged";

const logger = Logger.plugin("Caerbannog");

export async function start(): Promise<void> {
  await Caerbannog_Client();
};

async function Caerbannog_Client() {
  logger.log(`Attempting to connect to the local server...`);
  let Caerbannog_Server = new WebSocket("ws://localhost:6701");

  Caerbannog_Server.onopen = async function(event) {
    logger.log(`Connection established with Caerbannog Server.`);
  };
  Caerbannog_Server.onmessage = async function(event) {
    logger.log(`Message "${event.data}" received from the Caerbannog Server. Reloading QuickCSS!`);
    replugged.quickCSS.reload();
  };
  Caerbannog_Server.onclose = async function(event) {
    logger.log(`Failed to establish connection to the local Caerbannog Server, retrying in 10 seconds...`);
    await sleep(10000);
    await Caerbannog_Client();
  };
};

function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
};

export function stop(): void {
  logger.log(`Stopped Caerbannog.`);
};
