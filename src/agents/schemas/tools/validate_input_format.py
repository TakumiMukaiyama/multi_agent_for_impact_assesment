"""Schemas for validate_input_format tool."""
from typing import Dict, List, Any, Optional

from pydantic import BaseModel, Field

from src.agents.schemas.tools.base import ToolInput, ToolOutput


class ValidateInputFormatInput(ToolInput):
    """Input for validating ad payload format."""
    
    agent_id: str = Field(description="ID of the agent (prefecture)")
    ad_payload: Dict[str, Any] = Field(description="The ad payload to validate")
    schema_name: Optional[str] = Field(
        description="Optional name of schema to validate against",
        default=None
    )


class ValidationResult(BaseModel):
    """Result of validation."""
    
    valid: bool = Field(description="Whether the input is valid")
    errors: List[str] = Field(
        description="List of validation errors if invalid",
        default_factory=list
    )
    missing_fields: List[str] = Field(
        description="List of required fields that are missing",
        default_factory=list
    )
    invalid_fields: Dict[str, str] = Field(
        description="Dictionary of invalid fields with error messages",
        default_factory=dict
    )


class ValidateInputFormatOutput(ToolOutput):
    """Output from validating input format."""
    
    validation_result: ValidationResult = Field(description="Result of validation")