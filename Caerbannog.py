"""
# Caerbannog © 2025 by Ascellayn (alias SiriusBYT) is licensed under TSN License 1.0 [FD, NC]
The Sirio Network License 1.0 - Freely Derivable, Non-Commercial.  
*Origin: https://dev.sirio-network.com/license/1.0*
"""
from TSN_Abstracter import *;

import watchdog.events;
import watchdog.observers;


import websockets;
import threading;
import watchdog;
import asyncio;
import os;
import re;

""" Global Variables """
Caerbannog_Version = "Ceres MK.I Rev.3";
Reload_Status = False;
Running = True;

Configuration = {};

Clients = [];
Reload_Completed = [];

""" Websocket Server """
def WebSocket_Server() -> None: # NOTE: This will be later replaced by the new Trinity code, eventually.
    async def Websocket_Handler(Client) -> None:
        global Clients, Reload_Completed, Reload_Status;

        # Make the client connection readable
        Address = Client.remote_address;
        Client_Address = str(Address[0])+":"+str(Address[1]);
        Clients.append(Client);

        Log.Info(f'Connection: Web://{Client_Address}.');
        await Reload_CSS(Client); # Reloads CSS on connection to be sure

        while (Running):
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
                Log.Info(f'CLOSED: Web://{Client_Address}.');
                Clients.remove(Client);
            await asyncio.sleep(0); # If this line of code isn't present, for some fucking reason it NEVER actually sends the reload message????

    async def Websocket_Listener() -> None:
        S_Web = Log.Info(f'Starting WebSockets Server...');
        async with websockets.serve(Websocket_Handler, "127.0.0.1", 6701) as cebn_server:
            S_Web.OK();
            await cebn_server.serve_forever() 

    asyncio.run(Websocket_Listener());

"""" Watch Logic """
async def Reload_CSS(Client) -> bool:
    S_Call = Log.Info(f'Calling to reload QuickCSS...');
    try:
        await Client.send("WAKE UP MOTHERFUCKER");
        S_Call.OK();
        return True;
    except Exception as Except:
        S_Call.ERROR(Except);
        return False;

def Fetch_CSS(Folder_Name: str, Config_CSS: str) -> list:
    CSS_Files = [];
    # This will later be added to Caerbannog.json instead of this terrific shit
    Blacklisted_Files = [
        Config_CSS
    ]
    os.chdir(Folder_Name);
    for (Root_Path, Folders, Files) in os.walk(os.getcwd()):
        Continue_Search = True;
        Allow_Append = True;
        Relative_Path = Root_Path.replace(os.getcwd(), "")[1:].replace("\\","/");
        if (Continue_Search):
            Log.Debug(f"Relative_Path: {Relative_Path}\nFolders: {Folders}\nFiles: {Files};");
            for File in Files:
                for BF in Blacklisted_Files:
                    if (File == BF): Allow_Append = False;
                
                if ".css" in File and Allow_Append:
                    CSS_Files.append(f"{Folder_Name}/{Relative_Path}/{File}");
        else: continue;
    os.chdir("..");
    return CSS_Files;


""" Compiler """

def Combine_CSS(CSS_Files: list) -> str:
    Combined = "";
    for CSS_File in CSS_Files:
        Combined += "\n" + File.Read(CSS_File);
    return Combined;

def Compile_CSS(Combined: str) -> str:
    # The Flashcord Compiler will need to be better than this pile of shit!
    S_Compile = Log.Info(f"Compiling CSS...");
    Compiled = Combined;

    S_RW = Log.Debug(f"Removing Whitespaces at the start of each line...");
    Compiled = re.sub("(^[  ]*)", "", string=Compiled, flags=re.MULTILINE);
    S_RW.OK();

    S_LN = Log.Debug(f"Removing ALL Line Breaks...");
    Compiled = Compiled.replace("\n", "");
    S_LN.OK();

    S_Comments = Log.Debug(f"Removing comments...")
    Compiled = re.sub("/\\*.*?\\*/", "", string=Compiled, flags=re.MULTILINE);
    S_Comments.OK();

    S_Compile.OK();
    return Compiled;

def Root_Options(Options: list) -> str:
    CSS = ":root\x7b"
    for Option in Options:
        CSS += f"--{Option[0]}:\"{Option[1]}\";";
    CSS += "\x7d";
    return CSS;

def Finalize_CSS(Compiled: str, Folder_Name: str, Config_CSS: str) -> str:
    S_Finalize = Log.Debug(f"Finalizing Caerbannog Compilation...");

    License = File.Read(Configuration["License_File"]);
    CFG_CSS = File.Read(f"{Folder_Name}/{Config_CSS}");

    Compiler_Notes = f"/* Compiled using Caerbannog {Caerbannog_Version}*/\n"

    Root_Footer = [];
    Root_Footer.append(["Caerbannog-Version", Caerbannog_Version]);
    Root_Footer.append(["Caerbannog-Compile_Date", Time.Get_DateStrings(Time.Get_Unix())]);
    Root_Footer = Root_Options(Root_Footer);

    Compiler_Notes += Root_Footer;

    # Making the License inclusion less retarded, only allow the first 3 lines of it.
    License_Array = License.split("\n");
    License = f"{License_Array[0]}\n{License_Array[1]}\n{License_Array[2]}"; # I'm lazy, fuck you.

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

    S_Finalize.OK();
    return Production, Development;

class Watchdog_Handler(watchdog.events.FileSystemEventHandler):
    def __init__(self, Folder_Name: str, Config_CSS: str, Dev_CSS: str, Prod_CSS: str) -> None:
        self.Folder_Name = Folder_Name;
        self.Config_CSS = Config_CSS;
        self.Dev_CSS = Dev_CSS;
        self.Prod_CSS = Prod_CSS;
        Log.Info(f"[{Folder_Name}] Added watchdog with Config_CSS: {Config_CSS}; Dev_CSS: {Dev_CSS}; Prod_CSS: {Prod_CSS}.");
    
    def on_any_event(self, event) -> None:
        global Reload_Status, Reload_Completed;
        Log.Info(f"Triggering recompilation for {self.Folder_Name}:\n\tEvent: {event}");

        S_Fetch = Log.Debug(f"[{self.Folder_Name}] Fetching CSS...");
        CSS_Files = Fetch_CSS(self.Folder_Name, self.Config_CSS);
        S_Fetch.OK()

        S_Combine = Log.Debug(f"[{self.Folder_Name}] Combining CSS...");
        Combined = Combine_CSS(CSS_Files);
        S_Combine.OK();

        S_Compile = Log.Debug(f"[{self.Folder_Name}] Compiling CSS...");
        Compiled = Compile_CSS(Combined);
        S_Compile.OK();

        S_Finalize = Log.Debug(f"[{self.Folder_Name}] Finalizing CSS...")
        Production, Development = Finalize_CSS(Compiled, self.Folder_Name, self.Config_CSS);
        S_Finalize.OK();

        S_Write = Log.Debug(f"[{self.Folder_Name}] Writing CSS...")
        try:
            File.Write(self.Dev_CSS, Development);
            File.Write(self.Prod_CSS, Production)
            S_Write.OK();
            Log.Info(f"{self.Folder_Name} has been recompiled.");
        except Exception as Except:
            S_Write.ERROR(Except);
        
        # This may look stupid but there's a fucking race condition here
        Reload_Status = False;
        Reload_Completed = [];
        Reload_Status = True;

async def Bootstrap(S_Start: Log.Awaited_Log) -> None:
    global Configuration;
    
    S_CFG = Log.Info(f'Loading configuration...');
    Configuration = File.JSON_Read("Caerbannog.json");
    Log.Debug(f"Loaded Configuration:\n{Configuration}");
    S_CFG.OK();

    WebSockets_Thread = threading.Thread(target=WebSocket_Server);
    WebSockets_Thread.daemon = True;
    WebSockets_Thread.start();

    S_Watch = Log.Info(f'Starting Watchdog...');
    os.chdir("..");
    Observers = [];
    Index = -1;
    for Folder in Configuration["Watchdog"].keys():
        Index += 1;
        Folder_Dict = Configuration["Watchdog"][Folder];
        Observers.append(watchdog.observers.Observer());
        Observers[Index].schedule(Watchdog_Handler(Folder, Folder_Dict["Config_CSS"], Folder_Dict["Dev_CSS"], Folder_Dict["Prod_CSS"]), Folder, recursive=True);
        Observers[Index].start();
    S_Watch.OK();

    S_Start.OK();
    while True:
        try:
            if (Reload_Status):
                Log.Carriage(f"{Caerbannog_Version} - Reloaded Clients: {len(Reload_Completed)}/{len(Clients)}");
            else:
                Log.Carriage(f"{Caerbannog_Version} - Connected Clients: {len(Clients)}");
            await asyncio.sleep(1);
        except:
            Shutdown();

def Shutdown() -> None:
    global Running;
    Log.Critical(f"=== Shutting down Caerbannog ===");
    Running = False;
    quit();


# Uncomment this for basically debug mode
"""Log.Delete();
Config.Logging["File"] = True;
Config.Logging["File_Level"] = 10;
Config.Logging["Print_Level"] = 10;"""

# Spark
if __name__ == '__main__': 
   asyncio.run(Bootstrap(Log.Info(f'Starting Caerbannog...')));