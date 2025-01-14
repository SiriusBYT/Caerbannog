"""
The Caerbannog Compiler, is the new much more advanced compiler for Flashcord.

It it a Python Program that forever searches for changes in Flashcord's code, to then recompile it and cause an automatic Quick CSS reload thanks to the accompanying Replugged Plugin.
Some stuff is currently hard-coded for Flashcord, I can't be fucked making changes to make it easy to use for everyone else yet. If enough people use or 

Caerbannog uses port 6701 for both the Server and the Client.
Code is structured and formatted in the same style of SiriusBYT/Kosaka and has some code modified from the TSN Trinity Client/Server.
"""
import watchdog.events
import watchdog.observers
from CEBN_Dependencies import *;

import websockets;
import threading;
import watchdog;
import asyncio;
import os;
import re;

""" Global Variables """
Caerbannog_Version = "Ceres MK.I Rev.1";
Reload_Status = False;
Running = True;

Configuration = {};

Clients = [];
Reload_Completed = [];

""" Websocket Server """
def WebSocket_Server() -> None:
    Log(f'[wS Server] Starting WebSockets Server...');

    async def Websocket_Handler(Client) -> None:
        global Clients, Reload_Completed;
        # Make the client connection readable
        Address = Client.remote_address;
        Client_Address = str(Address[0])+":"+str(Address[1]);

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

def Fetch_CSS() -> list:
    CSS_Files = [];
    Blacklisted_Folders = [
        "Caerbannog",
        ".",
        "logs"
    ]
    Blacklisted_Files = [
        "main.css",
        "config.css",
        "prod.css"
    ]
    for (Root_Path, Folders, Files) in os.walk(os.getcwd()):
        Continue_Search = True;
        Allow_Append = True;
        Relative_Path = Root_Path.replace(os.getcwd(), "")[1:].replace("\\","/");
        for BF in Blacklisted_Folders:
            if (BF in Relative_Path):
                Continue_Search = False;
        if (Continue_Search):
            #Log(f"Relative_Path: {Relative_Path}\nFolders: {Folders}\nFiles: {Files};");
            for File in Files:
                for BF in Blacklisted_Files:
                    if (File == BF): Allow_Append = False;
                
                if ".css" in File and Allow_Append:
                    CSS_Files.append(f"{Relative_Path}/{File}");
        else: continue;
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

def Finalize_CSS(Compiled: str) -> str:
    Log(f"Finalizing Caerbannog Compilation...");

    with open(Configuration["License_File"], "r", encoding="UTF-8") as LSC:
        License = LSC.read();
    with open(Configuration["Config_CSS"], "r", encoding="UTF-8") as CFG:
        Config_CSS = CFG.read();

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
{Config_CSS}\n\n\
{Compiler_Notes}"

    return Production, Development;

class Watchdog_Handler(watchdog.events.FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        global Reload_Status;
        Log(f"New recorded event: {event}, triggering recompilation!\n");

        Log(f"Fetching CSS...")
        CSS_Files = Fetch_CSS();
        Log(f"Combining CSS..")
        Combined = Combine_CSS(CSS_Files);
        Log(f"Compiling CSS...")
        Compiled = Compile_CSS(Combined);
        Log(f"Finalizing CSS...")
        Production, Development = Finalize_CSS(Compiled);
        Log(f"Writing CSS...")
        with open("main.css", "w", encoding="UTF-8") as Development_CSS:
            Development_CSS.write(Development);
        with open("prod.css", "w", encoding="UTF-8") as Production_CSS:
            Production_CSS.write(Production);
        Log(f"Flashcord has been recompiled.")
        Reload_Status = True

async def Bootstrap() -> None:
    global Configuration;
    try:
        Log(f'[Bootstrap] Loading configuration...');
        Configuration = JSON_Load("Caerbannog.json");
        Log(f'[Bootstrap] Starting threads...');
        threading.Thread(target=WebSocket_Server).start();
        Log(f'[Bootstrap] Changing Directories...');
        os.chdir("..");

        Log(f'[Bootstrap] Starting Watchdog...');
        Observe_CSS = watchdog.observers.Observer();
        Observe_CSS.schedule(Watchdog_Handler(), Configuration["Folder"], recursive=True);
        Observe_CSS.start();
        Log(f'[Bootstrap] Caerbannog is now ready.');
    except KeyboardInterrupt:
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