# The Caerbannog Compiler, is the new much more advanced compiler for Flashcord.

It it a Python Program that forever searches for changes in Flashcord's code, to then minify, "compile" it and cause an automatic Quick CSS reload thanks to the accompanying Replugged Plugin. (Plugins for other clsient mods can be easily adapted, it is quite literally pure Javascript).


Caerbannog uses port 6701 for both the Server and the Client and its code is structured and formatted in the same style of SiriusBYT/Kosaka and has some code modified from the TSN Trinity Client/Server.

## Usage
- Caerbannog **MUST BE PLACED INSIDE THE SAME FOLDER CONTAINING YOUR CSS FILES**, a good example is the following folder structure:
```txt
Your Repository
│   License.md
│
├───Caerbannog
│       Caerbannog.json
│
└───Flashcord
        YourCSSFiles.css
        Config.css
```
- Run Caerbannog.py (the active folder MUST BE Caerbannog's folder, so don't run Caerbannog inside VSCode with the Python Debugger because it opens them in the root folder you've opened, annoying.)

### Caerbannog.json

| JSON Key | Description |
|----------|-------------|
| Watchdog | Dictionary containing keys with the name of the folder you wanna watch for changes |
| Dev_CSS | The CSS file meant for development, leave it as "main.css" unless your client mod's Quick CSS File has a different name. |
| Prod_CSS | The CSS file meant for production. |
| Config_CSS | The CSS file included in your development CSS File. It MUST be inside the folder you are watching for changes. |
| License_File | The Markdown file included at the top of your CSS Files. |

#### Valid Configuration JSON
In this example, this JSON makes Caerbannog check for changes in Flashcord-cSID, Flashcord-cSTB and Flashcord-cLPM.  
They all have "Config.css" as their Config_CSS.  
All these folders in the end results in the files "Ceres_SID", "Ceres_STB" and "Ceres_LPM" being built.  
The latest change in any of the folder replaces which CSS file is being "debugged" (Modifying a file in cSID will compile and reload cSID, the moment a file in cSTB is edited, your client mod will load cSTB as main.css in this example will be overwritten with cSTB's code).
```JSON
{
    "License_File": "License.md",
    "Watchdog": {
        "Flashcord-cSID": {
            "Config_CSS": "Config.css",
            "Dev_CSS": "main.css",
            "Prod_CSS": "Ceres_SID.css"
        },
        "Flashcord-cSTB": {
            "Config_CSS": "Config.css",
            "Dev_CSS": "main.css",
            "Prod_CSS": "Ceres_STB.css"
        },
        "Flashcord-cLPM": {
            "Config_CSS": "Config.css",
            "Dev_CSS": "main.css",
            "Prod_CSS": "Ceres_LPM.css"
        }
    }
}
```

### Config.css
Config.css effectively replaces your QuickCSS, it is ONLY included inside "main.css" and not "prod.css", as Caerbannog is intended to have your QuickCSS folder be sys-linked to whichever theme you are working on.


#### [Caerbannog © 2025 by Ascellayn (alias SiriusBYT) is licensed under The Sirio Network License 1.0 - [D_Free, C_Closed]](https://dev.sirio-network.com/license/1.0)
