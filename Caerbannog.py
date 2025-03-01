"""
# Caerbannog © 2025 by Ascellayn (alias SiriusBYT) is licensed under TSN License 1.0 [FD, NC]
The Sirio Network License 1.0 - Freely Derivable, Non-Commercial.  
*Origin: https://dev.sirio-network.com/license/1.0*
"""

import watchdog.events
import watchdog.observers
from CEBN_Dependencies import *;

import websockets;
import threading;
import watchdog;
import asyncio;
import uuid;
import os;
import re;
import os.path;

""" Global Variables """
Caerbannog_Version = "Ceres MK.I Rev.2";
Reload_Status = False;
Running = True;

Configuration = {};

Clients = [];
Reload_Completed = [];

""" Websocket Server """
def WebSocket_Server() -> None:
    Log(f'[wS Server] Starting WebSockets Server...');

    async def Websocket_Handler(Client) -> None:
        global Clients, Reload_Completed, Reload_Status;
        # Make the client connection readable
        Address = Client.remote_address;
        Client_Address = str(Address[0])+":"+str(Address[1]);
        Clients.append(Client);

        Log(f'[WS Server] Connection: Web://{Client_Address}.');
        while (True):
            if (Running):
                try:
                    if (Reload_Status == True and Client not in Reload_Completed):
                        Reload_Result = await Reload_CSS(Client);
                        if (Reload_Result):
                            Reload_Completed.append(Client);
                        else: return;
                    
                    if (len(Reload_Completed) == len(Clients)):
                        Reload_Status = False;
                        Reload_Completed = []; 
                
                    #Log(f"DEBUG: {Reload_Completed}({len(Reload_Completed)}) {Clients}({len(Clients)})")
                
                except websockets.ConnectionClosed:
                    Log(f'[Connection] CLOSED: Web://{Client_Address}.');
                    Clients.remove(Client);
                    return;
            else:
                Clients.remove(Client);
                return;
            await asyncio.sleep(0);

    async def Websocket_Listener() -> None:
        Log(f'[WS Server] Listening for WebSockets connections.');
        async with websockets.serve(Websocket_Handler, "127.0.0.1", 6701) as cebn_server:
            await cebn_server.serve_forever();
    
    asyncio.run(Websocket_Listener());

"""" Watch Logic """
async def Reload_CSS(Client) -> bool:
    Log(f'[WS Server] Calling to reload QuickCSS...');
    try:
        await Client.send("WAKE UP MOTHERFUCKER");
        Log(f'[WS Server] Successfully sent reload request.');
        return True;
    except:
        Log(f'[WS Server] Error asking to reload QuickCSS.');
        return False;

def Fetch_CSS(Folder_Name: str, Config_CSS: str) -> list:
    CSS_Files = [];
    Blacklisted_Files = [Config_CSS]
    
    # Use os.path for cross-platform compatibility
    folder_path = os.path.abspath(Folder_Name)
    os.chdir(folder_path)
    
    for root, _, files in os.walk(os.getcwd()):
        allow_append = True
        # Use os.path.relpath for cross-platform relative paths
        relative_path = os.path.relpath(root, os.getcwd())
        if relative_path == '.':
            relative_path = ''
            
        for file in files:
            if file in Blacklisted_Files:
                continue
                
            if file.endswith('.css'):
                # Use os.path.join for cross-platform path construction
                css_path = os.path.join(Folder_Name, relative_path, file)
                CSS_Files.append(os.path.normpath(css_path).replace('\\', '/'))
                
    os.chdir('..')
    return CSS_Files;


""" Compiler """

def Combine_CSS(CSS_Files: list) -> str:
    Combined = "";
    for File in CSS_Files:
        with open(File, "r", encoding="UTF-8") as CSS:
            Combined += "\n" + CSS.read();
    return Combined;

def Compile_CSS(Combined: str) -> str:
    # The Flashcord Compiler will need to be better than this pile of shit!
    Log(f"Compiling CSS...");
    Compiled = Combined;

    Log(f"Removing Whitespaces at the start of each line...")
    Compiled = re.sub("(^[  ]*)", "", string=Compiled, flags=re.MULTILINE);
    Log(f"Removing ALL Line Breaks...")
    Compiled = Compiled.replace("\n", "")
    Log(f"Removing comments...")
    Compiled = re.sub("/\\*.*?\\*/", "", string=Compiled, flags=re.MULTILINE);

    return Compiled;

def Root_Options(Options: list) -> str:
    CSS = ":root\x7b"
    for Option in Options:
        CSS += f"--{Option[0]}:\"{Option[1]}\";";
    CSS += "\x7d";
    return CSS;

def Finalize_CSS(Compiled: str, Folder_Name: str, Config_CSS: str) -> str:
    Log(f"Finalizing Caerbannog Compilation...");

    with open(Configuration["License_File"], "r", encoding="UTF-8") as LSC:
        License = LSC.read();
    with open(f"{Folder_Name}/{Config_CSS}", "r", encoding="UTF-8") as CFG:
        CFG_CSS = CFG.read();

    Compiler_Notes = f"/* Compiled using Caerbannog {Caerbannog_Version}*/\n"

    Root_Footer = [];
    Root_Footer.append(["Caerbannog-Version", Caerbannog_Version]);
    Root_Footer.append(["Caerbannog-Compile_Date", Date_String()]);
    Root_Footer = Root_Options(Root_Footer);

    Compiler_Notes += Root_Footer;

    Production = f"\
/*\n\
{License}\n\
*/\n\n\
{Compiled}\n\
{Compiler_Notes}"

    Development = f"\
/* DEVELOPMENT BUILD */\n\n\
/* {License} */\n\n\
{Compiled}\n\n\
{CFG_CSS}\n\n\
{Compiler_Notes}"

    return Production, Development;

class Watchdog_Handler(watchdog.events.FileSystemEventHandler):
    def __init__(self, Folder_Name: str, Config_CSS: str, Dev_CSS: str, Prod_CSS: str) -> None:
        self.Folder_Name = Folder_Name;
        self.Config_CSS = Config_CSS;
        self.Dev_CSS = Dev_CSS;
        self.Prod_CSS = Prod_CSS;
        Log(f"[{Folder_Name}] Added watchdog with Config_CSS: {Config_CSS}; Dev_CSS: {Dev_CSS}; Prod_CSS: {Prod_CSS}.");
    
    def on_any_event(self, event) -> None:
        global Reload_Status, Reload_Completed;
        Log(f"New recorded event: {event}, triggering recompilation for {self.Folder_Name}!\n");

        Log(f"[{self.Folder_Name}] Fetching CSS...")
        CSS_Files = Fetch_CSS(self.Folder_Name, self.Config_CSS);
        Log(f"[{self.Folder_Name}] Combining CSS..")
        Combined = Combine_CSS(CSS_Files);
        Log(f"[{self.Folder_Name}] Compiling CSS...")
        Compiled = Compile_CSS(Combined);
        Log(f"[{self.Folder_Name}] Finalizing CSS...")
        Production, Development = Finalize_CSS(Compiled, self.Folder_Name, self.Config_CSS);
        Log(f"[{self.Folder_Name}] Writing CSS...")
        with open(self.Dev_CSS, "w", encoding="UTF-8") as Development_CSS:
            Development_CSS.write(Development);
        with open(self.Prod_CSS, "w", encoding="UTF-8") as Production_CSS:
            Production_CSS.write(Production);
        Log(f"{self.Folder_Name} has been recompiled.")
        # This may look stupid but there's a fucking race condition here
        Reload_Status = False;
        Reload_Completed = [];
        Reload_Status = True;
        

async def Bootstrap() -> None:
    global Configuration;
    
    Log(f'[Bootstrap] Loading configuration...');
    # Use os.path.join for config file path
    config_path = os.path.join(os.path.dirname(__file__), "Caerbannog.json")
    Configuration = JSON_Load(config_path)
    
    Log(f'[Bootstrap] Starting threads...');
    threading.Thread(target=WebSocket_Server, daemon=True).start();
    
    Log(f'[Bootstrap] Changing Directories...');
    os.chdir(os.path.dirname(__file__))  # Change to script directory first
    os.chdir('..')

    Log(f'[Bootstrap] Starting Watchdog...');
    observers = [];
    for folder, folder_dict in Configuration["Watchdog"].items():
        observer = watchdog.observers.Observer();
        handler = Watchdog_Handler(
            folder,
            folder_dict["Config_CSS"],
            folder_dict["Dev_CSS"],
            folder_dict["Prod_CSS"]
        );
        observer.schedule(handler, folder, recursive=True);
        observer.start();
        observers.append(observer);

    """
    Observe_CSS = watchdog.observers.Observer();
    Observe_CSS.schedule(Watchdog_Handler(), Configuration["Folder"], recursive=True);
    Observe_CSS.start();
    """
    Log(f'[Bootstrap] Caerbannog is now ready.');
    try:
        while True:
            await asyncio.sleep(1);
    except KeyboardInterrupt:
        Log('[Bootstrap] Shutting down observers...');
        for observer in observers:
            observer.stop();
        for observer in observers:
            observer.join();
        Shutdown();

def Shutdown() -> None:
    global Running;
    Log(f'Shutting down Caerbannog...');
    Running = False;
    quit();

# Spark
if __name__== '__main__': 
   Log(f'[Spark] Starting Caerbannog...');
   asyncio.run(Bootstrap());