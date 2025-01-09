""" General Imports """

# Standard Python Libraries
import datetime;
import logging;
import sys;

""" Miscellaneous Functions """
def Void() -> None: return;

def Log(Text: str, Level: int = 20) -> None:
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

def Safe_Index(Array: list, Index: int):
	try: return Array[Index];
	except: return None;