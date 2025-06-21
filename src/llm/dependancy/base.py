from pydantic import BaseModel


class BaseInput(BaseModel):
    """Base class for all LLM input models."""
    pass


class BaseOutput(BaseModel):
    """Base class for all LLM output models."""
    pass