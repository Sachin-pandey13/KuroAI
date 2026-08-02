"""
Centralized exception hierarchy for KuroAI.

All custom exceptions across contracts, engine, runtime, capabilities, providers,
and agents derive from KuroAIError.
"""


class KuroAIError(Exception):
    """Base exception for all KuroAI platform errors."""

    pass


class RegistryError(KuroAIError):
    """Raised when an operation on a registry (Artifact, Task, Capability) fails."""

    pass


class AgentRuntimeError(KuroAIError):
    """Raised when an error occurs during agent runtime execution or state machine transition."""

    pass


class ProviderError(KuroAIError):
    """Raised when an LLM or media generation provider request fails."""

    pass


class SchedulerError(KuroAIError):
    """Raised when task scheduling, dependency resolution, or execution planning fails."""

    pass


class ContextError(KuroAIError):
    """Raised when context assembly, token budget allocation, or truncation fails."""

    pass


class AgentError(KuroAIError):
    """Raised when an individual agent fails to process its context or generate results."""

    pass


class ContractValidationError(KuroAIError):
    """Raised when contract schemas, invariants, or payload validation fails."""

    pass
