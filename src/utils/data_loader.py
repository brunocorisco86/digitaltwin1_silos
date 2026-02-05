import json
from pathlib import Path
from typing import Optional

from pydantic import ValidationError

from src.data_model import SiloData # Ambience import removed as it's not needed directly here

def load_silo_data(file_path: Path) -> Optional[SiloData]:
    """
    Loads and parses a JSON file containing silo data into a SiloData Pydantic model.

    Args:
        file_path: The path to the JSON file.

    Returns:
        A SiloData object if successful, None otherwise.
    """
    if not file_path.is_file():
        print(f"Error: File not found at {file_path}")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Explicitly handle the "no collectors" string for ambience
        if isinstance(data.get('ambience'), str) and \
           "no collectors" in data['ambience']:
            data['ambience'] = None # Set to None if it's the error string

        # Explicitly handle the "no collectors" string for consumption
        if isinstance(data.get('consumption'), str) and \
           "no collectors" in data['consumption']:
            data['consumption'] = None # Set to None if it's the error string

        return SiloData(**data)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path}: {e}")
        return None
    except ValidationError as e:
        print(f"Error validating data from {file_path} against schema: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while reading {file_path}: {e}")
        return None
