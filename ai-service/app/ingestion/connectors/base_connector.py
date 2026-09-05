from abc import ABC, abstractmethod
from typing import Generator, Dict, Any

class BaseConnector(ABC):
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the source."""
        pass
        
    @abstractmethod
    def fetch(self) -> Generator[Dict[str, Any], None, None]:
        """Yield raw records as dictionaries."""
        pass
