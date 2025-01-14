""" General Imports """

# Standard Python Libraries
import datetime;
import logging;
import json;
import sys;
import os;

""" Miscellaneous Functions """
def Void() -> None: return;

def Date_String() -> str:
	return datetime.datetime.utcnow().strftime("%Y/%m/%d - %H:%M:%S");

def Log(Text: str, Level: int = 20) -> None:
	mkdir("logs");
	Logger = logging.getLogger();
	File_Handler = logging.FileHandler(filename=f"logs/{datetime.datetime.utcnow().strftime("%Y-%m_%d")}.log");
	Console_Handler = logging.StreamHandler(stream=sys.stdout);
	Handlers = [File_Handler, Console_Handler]
	logging.basicConfig(
		level = 20,
		format = "[%(asctime)s] - %(levelname)s: %(message)s",
		datefmt = "%Y/%m/%d - %H:%M:%S",
		handlers = Handlers
	);
	Logger.log(Level, Text);

""" General File Processing """
def JSON_Load(File: str) -> dict:
	JSON_Exists(File); # If shit hits the fan we should still get an empty dict
	with open(File, "r", encoding="UTF-8") as JSON:
		return json.load(JSON);
	
def JSON_Write(File: str, Dictionary: dict) -> None:
	JSON_Exists(File)
	with open(File, "w", encoding="UTF-8") as JSON:
		JSON.write(json.dumps(Dictionary, indent=2));
		return None;

def JSON_Exists(File: str) -> bool:
	if ('/' in File): # Creates the corresponding folder structure if it doesn't exist.
		Path_Array = File.split("/");
		Path = "";

		for Path_Index in range (len(Path_Array)):
			if (Path_Index >= (len(Path_Array) -1)): break;
			Path += f"{Path_Array[Path_Index]}/";
		mkdir(Path)

	if (File_Exists(File) == False):
		with open(File, "w", encoding="UTF-8") as JSON:
			JSON.write(json.dumps({}, indent=2));
			return False;
	else: return True;

def File_Exists(Path: str) -> bool:
	return os.path.isfile(Path);

def mkdir(Path: str) -> None: # Shitty code incomin'!
	if (Path[-1] == '/'):
		Path = Path[:-1];
	try: os.makedirs(Path, exist_ok=True);
	except: Void();
	return None;

def ls(Folder: str) -> list:
    try:
        Results = next(os.walk(f"{os.getcwd()}/{Folder}"));
        return [Results[1], Results[2]];
    except: return [[None], [None]];

def Safe_Index(Array: list, Index: int):
	try: return Array[Index];
	except: return None;