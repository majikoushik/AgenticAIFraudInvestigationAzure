class LLMConfigurationError(RuntimeError):
    """Raised when a requested LLM provider is not configured and fallback is disabled."""


class LLMResponseParseError(ValueError):
    """Raised when a model response cannot be parsed into the expected structured output."""
