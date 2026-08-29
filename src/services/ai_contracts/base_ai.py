from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAIService(ABC):
    """
    Abstract Base Class for all AI model services.
    Ensures backend decoupling from AI model implementation details.
    """

    @abstractmethod
    async def check_health(self) -> bool:
        """Returns True if the underlying AI model service is reachable."""
        pass
