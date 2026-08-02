from abc import ABC, abstractmethod
from typing import List

from backend.contracts.capability import ToolRequest, ToolResponse


class BaseProvider(ABC):
    """
    Abstract base class for all capability providers.
    Every provider (ComfyUI, Replicate, LocalSD, etc.) implements this interface.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Unique provider identifier."""
        ...

    @property
    @abstractmethod
    def supported_models(self) -> List[str]:
        """List of model identifiers this provider supports."""
        ...

    @abstractmethod
    def execute(self, request: ToolRequest) -> ToolResponse:
        """Execute a tool request against this provider's backend."""
        ...

    @abstractmethod
    def health_check(self, live: bool = False) -> bool:
        """
        Verify provider availability.
        If live=False, do a fast static check (API keys, config).
        If live=True, perform an actual ping/request to the backend.
        """
        ...

    def cancel(self, request_id: str) -> bool:
        """
        Attempt to cancel an ongoing execution request.
        Returns True if cancellation was successfully dispatched, False otherwise.
        """
        return False
