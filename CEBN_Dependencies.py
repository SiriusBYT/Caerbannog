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
	log_filename = os.path.join("logs", f"{datetime.datetime.utcnow().strftime('%Y-%m_%d')}.log");
	File_Handler = logging.FileHandler(filename=log_filename);
	Console_Handler = logging.StreamHandler(stream=sys.stdout);
	# Clear existing handlers to prevent duplicate logging
	Logger.handlers.clear();
	Logger.addHandler(File_Handler);
	Logger.addHandler(Console_Handler);
	Logger.setLevel(20);
	formatter = logging.Formatter(
		fmt="[%(asctime)s] - %(levelname)s: %(message)s",
		datefmt="%Y/%m/%d - %H:%M:%S"
	);
	File_Handler.setFormatter(formatter);
	Console_Handler.setFormatter(formatter);
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
	if os.path.sep in File:  # Use os.path.sep instead of hardcoded '/'
		Path = os.path.dirname(File);
		mkdir(Path);

	if not File_Exists(File):
		with open(File, "w", encoding="UTF-8") as JSON:
			json.dump({}, JSON, indent=2);
			return False;
	return True;

def File_Exists(Path: str) -> bool:
	return os.path.isfile(Path);

def mkdir(Path: str) -> None:
	try:
		os.makedirs(Path, exist_ok=True);
	except Exception as e:
		logging.warning(f"Failed to create directory {Path}: {str(e)}");
	return None;

def ls(Folder: str) -> list:
	try:
		folder_path = os.path.join(os.getcwd(), Folder);
		folders = [];
		files = [];
		for entry in os.scandir(folder_path):
			if entry.is_dir():
				folders.append(entry.name);
			elif entry.is_file():
				files.append(entry.name);
		return [folders, files];
	except Exception as e:
		logging.warning(f"Failed to list directory {Folder}: {str(e)}");
		return [[], []];

def Safe_Index(Array: list, Index: int):
	try: return Array[Index];
	except: return None;