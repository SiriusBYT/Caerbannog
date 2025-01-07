"""
The Caerbannog Compiler, is the new much more advanced compiler for Flashcord.

It it a Python Program that forever searches for changes in Flashcord's code,
to then recompile it and cause an automatic Quick CSS reload thanks to the accompanying Replugged Plugin.

Uses port 6701 for the communication between the Caebannog Server and Client.

Code is structured and formatted in the same style of SiriusBYT/Kosaka.
Some code is modified from the Trinity Clients and Servers.
"""
from CEBN_Dependencies import *;
import websockets;

# Multi-threading modules
import asyncio;
import threading;

# Miscellaneous Modules
import os;
import sys;

""" Global Variables """
ASK_RELOAD = False;

""" Service Functions """
def WebSocket_Server():
    Log(f'[System] INFO: Starting WebSockets Server...');

    async def Websocket_Handler(Client):
        global ASK_RELOAD;
        # Make the client connection readable
        Address = Client.remote_address;
        Client_Address = str(Address[0])+":"+str(Address[1]);

        Log(f'[Connection] OK: Web://{Client_Address}.');
        
        while True:
            if (ASK_RELOAD == True):
                Log(f'[WS Server] Calling to reload QuickCSS...');
                try:
                    await Client.send("WAKE UP MOTHERFUCKER");
                    ASK_RELOAD = False;
                except:
                    Log(f'[WS Server] Error asking to reload QuickCSS.');

    async def Websocket_Listener():
        Log(f'[WS Server] OK: WebSockets thread started.');
        async with websockets.serve(Websocket_Handler, "127.0.0.1", 6701):
            await asyncio.Future();
    
    asyncio.run(Websocket_Listener());

def Bootstrap():
    global ASK_RELOAD;
    os.system("clear");
    threading.Thread(target=WebSocket_Server).start();
    Log(f'[Caerbannog] Server initialized.');
    try:
        while True: 
            asyncio.sleep(1);
    except KeyboardInterrupt:
        Shutdown()

# Spark
if __name__== '__main__': 
   Bootstrap();

def Shutdown():
    Log(f'[System] Shutting down Caerbannog...')
    try: sys.exit(130)
    except SystemExit: os._exit(130)
    