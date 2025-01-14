# The Caerbannog Compiler, is the new much more advanced compiler for Flashcord.

It it a Python Program that forever searches for changes in Flashcord's code, to then minify, "compile" it and cause an automatic Quick CSS reload thanks to the accompanying Replugged Plugin. (Plugins for other clsient mods can be easily adapted, it is quite literally pure Javascript).


Caerbannog uses port 6701 for both the Server and the Client and its code is structured and formatted in the same style of SiriusBYT/Kosaka and has some code modified from the TSN Trinity Client/Server.

## Usage
- Caerbannog **MUST BE PLACED INSIDE THE SAME FOLDER CONTAINING YOUR CSS FILES**, a good example is the following folder structure:
```txt
Your Repository
│   config.css
│   License.md
│
├───Caerbannog
│       Caerbannog.json
│
└───Flashcord
        YourCSSFiles.css
```
- Run Caerbannog.py (the active folder MUST BE Caerbannog's folder, so don't run Caerbannog inside VSCode with the Python Debugger because it opens them in the root folder you've opened, annoying.)

### Caerbannog.json

| JSON Key | Description |
|----------|-------------|
| Folder   | The Folder Name that Caerbannog will watch changes for. |
| Config_CSS | The CSS file included in your development "main.css" file. |
| License_File | The Markdown file included at the top of both your CSS Files. |

### Config.css
Config.css effectively replaces your QuickCSS, it is ONLY included inside "main.css" and not "prod.css", as Caerbannog is intended to have your QuickCSS folder be sys-linked to whichever theme you are working on.