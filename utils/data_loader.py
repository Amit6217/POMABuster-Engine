import json
from typing import List, Dict
from core.models import Log

class DataLoader:
    """Utility class to load test JSON data."""
    
    @staticmethod
    def load_logs(file_path: str) -> List[Log]:
        with open(file_path, "r") as f:
            data = json.load(f)
        return [Log(**d) for d in data]

    @staticmethod
    def load_token_supplies(file_path: str) -> Dict[str, float]:
        with open(file_path, "r") as f:
            return json.load(f)
