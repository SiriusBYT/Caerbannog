""" General Imports """

# Standard Python Libraries
import datetime;
import logging;
import sys;
import os;

""" Miscellaneous Functions """
def Void() -> None: return;

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

def mkdir(Path: str) -> None: # Shitty code incomin'!
	if (Path[-1] == '/'):
		Path = Path[:-1];
	try: os.makedirs(Path, exist_ok=True);
	except: Void();
	return None;

def Safe_Index(Array: list, Index: int):
	try: return Array[Index];
	except: return None;