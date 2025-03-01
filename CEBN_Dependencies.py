"""
CEBN Dependencies Module
Contains utility functions for logging, file operations, and other common tasks.
"""

# Standard Python Libraries
import datetime
import logging
import json
import sys
import os
from typing import Any, List, Tuple, Optional, Dict, Union

"""Miscellaneous Functions"""

def void() -> None:
	"""Empty function that does nothing."""
	return None


def get_date_string() -> str:
	"""Returns the current UTC date and time as a formatted string."""
	return datetime.datetime.utcnow().strftime("%Y/%m/%d - %H:%M:%S")


def log(text: str, level: int = logging.INFO) -> None:
	"""
	Logs a message to both file and console.
	
	Args:
		text: The message to log
		level: The logging level (default: INFO)
	"""
	ensure_directory("logs")
	
	# Create logger
	logger = logging.getLogger()
	log_filename = os.path.join("logs", f"{datetime.datetime.utcnow().strftime('%Y-%m-%d')}.log")
	
	# Create handlers
	file_handler = logging.FileHandler(filename=log_filename)
	console_handler = logging.StreamHandler(stream=sys.stdout)
	
	# Clear existing handlers to prevent duplicate logging
	logger.handlers.clear()
	
	# Add handlers to logger
	logger.addHandler(file_handler)
	logger.addHandler(console_handler)
	logger.setLevel(logging.INFO)
	
	# Create formatter and add to handlers
	formatter = logging.Formatter(
		fmt="[%(asctime)s] - %(levelname)s: %(message)s",
		datefmt="%Y/%m/%d - %H:%M:%S"
	)
	file_handler.setFormatter(formatter)
	console_handler.setFormatter(formatter)
	
	# Log the message
	logger.log(level, text)


"""File Operations"""

def load_json(file_path: str) -> Dict[str, Any]:
	"""
	Loads a JSON file into a dictionary.
	Creates the file with an empty dict if it doesn't exist.
	
	Args:
		file_path: Path to the JSON file
		
	Returns:
		Dictionary containing the JSON data
	"""
	ensure_json_exists(file_path)  # Create file if it doesn't exist
	
	try:
		with open(file_path, "r", encoding="UTF-8") as json_file:
			return json.load(json_file)
	except json.JSONDecodeError:
		# Return empty dict if file is corrupted
		return {}


def write_json(file_path: str, data: Dict[str, Any]) -> None:
	"""
	Writes a dictionary to a JSON file.
	
	Args:
		file_path: Path to the JSON file
		data: Dictionary to write
	"""
	ensure_json_exists(file_path)
	
	with open(file_path, "w", encoding="UTF-8") as json_file:
		json.dump(data, json_file, indent=2)


def ensure_json_exists(file_path: str) -> bool:
	"""
	Ensures a JSON file exists, creating it with an empty dict if needed.
	Also creates any necessary parent directories.
	
	Args:
		file_path: Path to the JSON file
		
	Returns:
		True if file already existed, False if it was created
	"""
	if os.path.sep in file_path:
		directory = os.path.dirname(file_path)
		ensure_directory(directory)

	if not file_exists(file_path):
		with open(file_path, "w", encoding="UTF-8") as json_file:
			json.dump({}, json_file, indent=2)
		return False
	
	return True


def file_exists(path: str) -> bool:
	"""
	Checks if a file exists.
	
	Args:
		path: Path to the file
		
	Returns:
		True if the file exists, False otherwise
	"""
	return os.path.isfile(path)


def ensure_directory(path: str) -> None:
	"""
	Creates a directory if it doesn't exist.
	
	Args:
		path: Path to the directory
	"""
	try:
		os.makedirs(path, exist_ok=True)
	except Exception as e:
		logging.warning(f"Failed to create directory {path}: {str(e)}")


def list_directory(folder: str) -> Tuple[List[str], List[str]]:
	"""
	Lists all folders and files in a directory.
	
	Args:
		folder: Path to the directory
		
	Returns:
		Tuple containing (list of folders, list of files)
	"""
	try:
		folder_path = os.path.join(os.getcwd(), folder)
		folders = []
		files = []
		
		for entry in os.scandir(folder_path):
			if entry.is_dir():
				folders.append(entry.name)
			elif entry.is_file():
				files.append(entry.name)
				
		return folders, files
	except Exception as e:
		logging.warning(f"Failed to list directory {folder}: {str(e)}")
		return [], []


def safe_index(array: List[Any], index: int) -> Optional[Any]:
	"""
	Safely gets an element from a list without raising IndexError.
	
	Args:
		array: The list to index
		index: The index to access
		
	Returns:
		The element at the index, or None if index is out of bounds
	"""
	try:
		return array[index]
	except IndexError:
		return None