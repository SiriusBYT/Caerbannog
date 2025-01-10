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
Caerbannog_Version = "Ceres MK.I";
ASK_RELOAD = False;

""" Websocket Server """
def WebSocket_Server() -> None:
    Log(f'[System] INFO: Starting WebSockets Server...');

    async def Websocket_Handler(Client) -> None:
        # Make the client connection readable
        Address = Client.remote_address;
        Client_Address = str(Address[0])+":"+str(Address[1]);

        Log(f'[Connection] OK: Web://{Client_Address}.');
        while (True):
            try:
                try:
                    if (ASK_RELOAD == True):
                        await Reload_CSS(Client);
                except websockets.ConnectionClosed:
                    Log(f'[Connection] CLOSED: Web://{Client_Address}.');
                    return;
            except KeyboardInterrupt:
                return;
            await asyncio.sleep(0);

    async def Websocket_Listener() -> None:
        Log(f'[WS Server] OK: WebSockets thread started.');
        async with websockets.serve(Websocket_Handler, "127.0.0.1", 6701) as cebn_server:
            await cebn_server.serve_forever();
    
    asyncio.run(Websocket_Listener());

"""" Watch Logic """
async def Reload_CSS(Client) -> None:
    global ASK_RELOAD;
    Log(f'[WS Server] Calling to reload QuickCSS...');
    try:
        await Client.send("WAKE UP MOTHERFUCKER");
        ASK_RELOAD = False;
        Log(f'[WS Server] Successfully sent reload request.');
    except:
        Log(f'[WS Server] Error asking to reload QuickCSS. Closing.');
        return;

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
    Log(f"Compiling Flashcord...");
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
    Log(f"Finalizing Flashcord Compilation...");

    with open(f"License.md", "r", encoding="UTF-8") as LSC:
        License = LSC.read();
    with open("config.css", "r", encoding="UTF-8") as CFG:
        Config_CSS = CFG.read();

    Compiler_Notes = f"/* Compiled using Caerbannog {Caerbannog_Version}*/\n"

    Root_Footer = [];
    Root_Footer.append(["Caerbannog-Version", Caerbannog_Version]);
    Root_Footer.append(["Caerbannog_Build", Date_String()]);
    Root_Footer = Root_Options(Root_Footer);

    Compiler_Notes += Root_Footer;

    Production = f"\
/*\n\
{License}\n\
*/\n\n\
{Compiled}\n\
{Compiler_Notes}"

    Development = f"\
/* DEVELOPMENT BUILD */\n\
{Config_CSS}\n\n\
/* {License} */\n\n\
{Compiled}\n\n\
{Compiler_Notes}"

    return Production, Development;

class Watchdog_Handler(watchdog.events.FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        global ASK_RELOAD;
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
        ASK_RELOAD = True

async def Bootstrap() -> None:
    try:
        try:
            os.system("clear");
        except:
            os.system("cls");
        threading.Thread(target=WebSocket_Server).start();
        Log(f'[Caerbannog] Server initialized.');
        os.chdir("..");

        
        Observe_CSS = watchdog.observers.Observer();
        Observe_CSS.schedule(Watchdog_Handler(), "Flashcord", recursive=True)
        Observe_CSS.start();
        #while True: await asyncio.sleep(1);
        """
        Old_Combined = "";
        while True:
            await asyncio.sleep(1);
            Combined = Combine_CSS(Fetch_CSS());
            if (Combined != Old_Combined):
                Old_Combined = Combined;
                Log(f"Routine Compilation is different! ")
                Compiled = Compile_CSS(Combined);
                Production, Development = Finalize_CSS(Compiled);
                with open("main.css", "w", encoding="UTF-8") as Development_CSS:
                    Development_CSS.write(Development);
                with open("prod.css", "w", encoding="UTF-8") as Production_CSS:
                    Production_CSS.write(Production);
                Log(f"Flashcord has been recompiled.")
                ASK_RELOAD = True
            else:
                Log(f"ROUTINE: No changes detected.")
            """
    except KeyboardInterrupt:
        Shutdown();

def Shutdown() -> None:
    Log(f'[System] Shutting down Caerbannog...')
    quit();

# Spark
if __name__== '__main__': 
   asyncio.run(Bootstrap());