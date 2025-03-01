"""
# Caerbannog © 2025 by Ascellayn (alias SiriusBYT) is licensed under TSN License 1.0 [FD, NC]
The Sirio Network License 1.0 - Freely Derivable, Non-Commercial.  
*Origin: https://dev.sirio-network.com/license/1.0*
"""

import asyncio
import os
import re
import threading
import uuid
from pathlib import Path

import watchdog.events
import watchdog.observers
import websockets

from CEBN_Dependencies import *

# Global Constants
CAERBANNOG_VERSION = "Ceres MK.I Rev.2"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 6701

# Global State
configuration = {}
clients = []
reload_status = False
reload_completed = []
running = True


class WatchdogHandler(watchdog.events.FileSystemEventHandler):
    def __init__(self, folder_name, config_css, dev_css, prod_css):
        self.folder_name = folder_name
        self.config_css = config_css
        self.dev_css = dev_css
        self.prod_css = prod_css
        Log(f"[{folder_name}] Added watchdog with Config_CSS: {config_css}; Dev_CSS: {dev_css}; Prod_CSS: {prod_css}.")
    
    def on_any_event(self, event):
        global reload_status, reload_completed
        Log(f"New recorded event: {event}, triggering recompilation for {self.folder_name}!\n")

        Log(f"[{self.folder_name}] Fetching CSS...")
        css_files = fetch_css(self.folder_name, self.config_css)
        
        Log(f"[{self.folder_name}] Combining CSS...")
        combined = combine_css(css_files)
        
        Log(f"[{self.folder_name}] Compiling CSS...")
        compiled = compile_css(combined)
        
        Log(f"[{self.folder_name}] Finalizing CSS...")
        production, development = finalize_css(compiled, self.folder_name, self.config_css)
        
        Log(f"[{self.folder_name}] Writing CSS...")
        with open(self.dev_css, "w", encoding="UTF-8") as development_css:
            development_css.write(development)
        with open(self.prod_css, "w", encoding="UTF-8") as production_css:
            production_css.write(production)
            
        Log(f"{self.folder_name} has been recompiled.")
        
        # Reset reload status to avoid race condition
        reload_status = False
        reload_completed = []
        reload_status = True


async def reload_css(client):
    """Send reload signal to a connected client."""
    Log(f'[WS Server] Calling to reload QuickCSS...')
    try:
        await client.send("WAKE UP MOTHERFUCKER")
        Log(f'[WS Server] Successfully sent reload request.')
        return True
    except:
        Log(f'[WS Server] Error asking to reload QuickCSS.')
        return False


def fetch_css(folder_name, config_css):
    """Fetch all CSS files from a folder, excluding blacklisted files."""
    css_files = []
    blacklisted_files = [config_css]
    
    folder_path = Path(folder_name).absolute()
    original_dir = Path.cwd()
    os.chdir(folder_path)
    
    for root, _, files in os.walk('.'):
        relative_path = Path(root).relative_to('.')
        
        for file in files:
            if file in blacklisted_files:
                continue
                
            if file.endswith('.css'):
                if relative_path == Path('.'):
                    css_path = Path(folder_name) / file
                else:
                    css_path = Path(folder_name) / relative_path / file
                # Use Path objects for path manipulation and convert to string with forward slashes
                css_files.append(str(css_path).replace('\\', '/'))
                
    os.chdir(original_dir)
    return css_files


def combine_css(css_files):
    """Combine multiple CSS files into a single string."""
    combined = ""
    for file in css_files:
        with open(file, "r", encoding="UTF-8") as css:
            combined += "\n" + css.read()
    return combined


def compile_css(combined):
    """Compile CSS by removing whitespace, line breaks, and comments."""
    Log(f"Compiling CSS...")
    compiled = combined

    Log(f"Removing Whitespaces at the start of each line...")
    compiled = re.sub(r"(^[ \t]*)", "", string=compiled, flags=re.MULTILINE)
    
    Log(f"Removing ALL Line Breaks...")
    compiled = compiled.replace("\n", "")
    
    Log(f"Removing comments...")
    compiled = re.sub(r"/\*.*?\*/", "", string=compiled, flags=re.MULTILINE)

    return compiled


def root_options(options):
    """Generate CSS root variables from options list."""
    css = ":root{"
    for option in options:
        css += f"--{option[0]}:\"{option[1]}\";"
    css += "}"
    return css


def finalize_css(compiled, folder_name, config_css):
    """Finalize CSS by adding license and metadata."""
    Log(f"Finalizing Caerbannog Compilation...")

    with open(configuration["License_File"], "r", encoding="UTF-8") as lsc:
        license_text = lsc.read()
    with open(f"{folder_name}/{config_css}", "r", encoding="UTF-8") as cfg:
        cfg_css = cfg.read()

    compiler_notes = f"/* Compiled using Caerbannog {CAERBANNOG_VERSION}*/\n"

    root_footer = [
        ["Caerbannog-Version", CAERBANNOG_VERSION],
        ["Caerbannog-Compile_Date", Date_String()]
    ]
    root_footer = root_options(root_footer)
    compiler_notes += root_footer

    production = f"""/*
{license_text}
*/

{compiled}
{compiler_notes}"""

    development = f"""/* DEVELOPMENT BUILD */

/* {license_text} */

{compiled}

{cfg_css}

{compiler_notes}"""

    return production, development


async def websocket_handler(client):
    """Handle individual WebSocket client connections."""
    global clients, reload_completed, reload_status
    
    # Make the client connection readable
    address = client.remote_address
    client_address = f"{address[0]}:{address[1]}"
    clients.append(client)

    Log(f'[WS Server] Connection: Web://{client_address}.')
    
    try:
        while running:
            if reload_status and client not in reload_completed:
                reload_result = await reload_css(client)
                if reload_result:
                    reload_completed.append(client)
                else:
                    break
                
            if len(reload_completed) == len(clients) and reload_status:
                reload_status = False
                reload_completed = []
            
            await asyncio.sleep(0.1)
    except websockets.ConnectionClosed:
        Log(f'[Connection] CLOSED: Web://{client_address}.')
    finally:
        if client in clients:
            clients.remove(client)


async def websocket_listener():
    """Listen for WebSocket connections."""
    Log(f'[WS Server] Listening for WebSockets connections.')
    async with websockets.serve(websocket_handler, DEFAULT_HOST, DEFAULT_PORT) as server:
        await server.serve_forever()


def websocket_server():
    """Start the WebSocket server in a separate thread."""
    Log(f'[WS Server] Starting WebSockets Server...')
    asyncio.run(websocket_listener())


async def bootstrap():
    """Initialize and start all components of Caerbannog."""
    global configuration
    
    Log(f'[Bootstrap] Loading configuration...')
    config_path = Path(__file__).parent / "Caerbannog.json"
    configuration = JSON_Load(str(config_path))
    
    Log(f'[Bootstrap] Starting threads...')
    threading.Thread(target=websocket_server, daemon=True).start()
    
    Log(f'[Bootstrap] Changing Directories...')
    os.chdir(Path(__file__).parent.parent)  # Move up one directory from script location

    Log(f'[Bootstrap] Starting Watchdog...')
    observers = []
    for folder, folder_dict in configuration["Watchdog"].items():
        observer = watchdog.observers.Observer()
        handler = WatchdogHandler(
            folder,
            folder_dict["Config_CSS"],
            folder_dict["Dev_CSS"],
            folder_dict["Prod_CSS"]
        )
        # Use Path objects to ensure cross-platform compatibility
        watch_path = Path(folder).absolute()
        observer.schedule(handler, str(watch_path), recursive=True)
        observer.start()
        observers.append(observer)

    Log(f'[Bootstrap] Caerbannog is now ready.')
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        Log('[Bootstrap] Shutting down observers...')
        for observer in observers:
            observer.stop()
        for observer in observers:
            observer.join()
        shutdown()


def shutdown():
    """Gracefully shut down Caerbannog."""
    global running
    Log(f'Shutting down Caerbannog...')
    running = False
    quit()


# Entry point
if __name__ == '__main__':
    Log(f'[Spark] Starting Caerbannog...')
    asyncio.run(bootstrap())