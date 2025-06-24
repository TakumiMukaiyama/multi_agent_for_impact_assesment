"""Schemas for validate input format tool."""

from typing import Any, Dict, List, Optional

from pydantic import Field

from src.agents.schemas.tools.base import ToolInput, ToolOutput


class ValidationResult(ToolOutput):
    """Result of a validation check."""

    field_name: str = Field(description="Name of the field that was validated")
    is_valid: bool = Field(description="Whether the field is valid")
    error_message: Optional[str] = Field(description="Error message if validation failed", default=None)


class ValidateInputFormatInput(ToolInput):
    """Input for validating advertisement data format."""

    agent_id: str = Field(description="ID of the agent performing validation")
    ad_data: Dict[str, Any] = Field(description="Advertisement data to validate")
    validation_type: Optional[str] = Field(
        description="Type of validation to perform (e.g., 'basic', 'strict', 'content')", default="basic"
    )


class ValidateInputFormatOutput(ToolOutput):
    """Output containing validation results."""

    is_valid: bool = Field(description="Whether the overall input is valid")
    validation_results: List[ValidationResult] = Field(
        description="Detailed validation results for each field", default_factory=list
    )
    errors: List[str] = Field(description="List of validation errors", default_factory=list)
    warnings: List[str] = Field(description="List of validation warnings", default_factory=list)
    summary: str = Field(description="Summary of validation results")
