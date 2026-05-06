"""Polymath Agent, a small but complete Python agent implementation.

The package is intentionally split into readable subsystems:

- ``agent`` owns the OpenAI Responses API loop.
- ``tools`` owns tool schemas and execution.
- ``skills`` owns Agent Skills discovery.
- ``memory`` and ``heartbeat`` provide simple persistent state.
"""

__all__ = ["__version__"]

__version__ = "1.0.0"
