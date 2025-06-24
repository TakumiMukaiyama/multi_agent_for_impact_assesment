"""Tool for validating input format of advertisement data."""

from typing import Any, Dict, List

from src.agents.schemas.tools.validate_input_format import (
    ValidateInputFormatInput,
    ValidateInputFormatOutput,
    ValidationResult,
)
from src.agents.tools.base import BaseAgentTool
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ValidateInputFormat(BaseAgentTool[ValidateInputFormatInput, ValidateInputFormatOutput]):
    """Tool for validating input format of advertisement data."""

    def __init__(self):
        """Initialize the tool."""
        super().__init__(
            name="validate_input_format",
            description="Validate advertisement data format and structure. Requires agent_id and ad_data. Optional: validation_type.",
        )

        # Required fields for basic validation
        self.required_fields = ["ad_id", "ad_content", "category"]

        # Optional fields that are commonly expected
        self.optional_fields = ["title", "brand", "target_audience", "campaign_id", "created_date"]

        # Validation rules
        self.validation_rules = {
            "ad_id": {"type": str, "min_length": 1, "max_length": 100},
            "ad_content": {"type": str, "min_length": 10, "max_length": 5000},
            "category": {"type": str, "min_length": 1, "max_length": 50},
            "title": {"type": str, "min_length": 1, "max_length": 200},
            "brand": {"type": str, "min_length": 1, "max_length": 100},
            "target_audience": {"type": [str, list], "max_length": 200},
            "campaign_id": {"type": str, "min_length": 1, "max_length": 100},
        }

    async def execute(self, input_data: ValidateInputFormatInput) -> ValidateInputFormatOutput:
        """Execute the tool to validate input format.

        Args:
            input_data: Input containing ad data to validate

        Returns:
            Output containing validation results
        """
        agent_id = input_data.agent_id
        ad_data = input_data.ad_data
        validation_type = input_data.validation_type or "basic"

        try:
            logger.info(f"Validating ad data format for agent {agent_id} (type: {validation_type})")

            validation_results = []
            errors = []
            warnings = []

            # Check if ad_data is a dictionary
            if not isinstance(ad_data, dict):
                errors.append("ad_data must be a dictionary")
                return ValidateInputFormatOutput(
                    success=False,
                    is_valid=False,
                    validation_results=[],
                    errors=errors,
                    warnings=warnings,
                    summary="Validation failed: ad_data is not a dictionary",
                )

            # Basic validation: check required fields
            for field in self.required_fields:
                result = self._validate_field(field, ad_data, required=True)
                validation_results.append(result)
                if not result.is_valid:
                    errors.append(result.error_message)

            # Check optional fields if present
            for field in self.optional_fields:
                if field in ad_data:
                    result = self._validate_field(field, ad_data, required=False)
                    validation_results.append(result)
                    if not result.is_valid:
                        warnings.append(result.error_message)

            # Strict validation: additional checks
            if validation_type == "strict":
                errors.extend(self._perform_strict_validation(ad_data))

            # Content validation: check content quality
            elif validation_type == "content":
                warnings.extend(self._perform_content_validation(ad_data))

            # Determine overall validity
            is_valid = len(errors) == 0

            # Create summary
            if is_valid:
                summary = f"Validation successful. {len(validation_results)} fields checked."
                if warnings:
                    summary += f" {len(warnings)} warnings found."
            else:
                summary = f"Validation failed with {len(errors)} errors."
                if warnings:
                    summary += f" {len(warnings)} warnings also found."

            logger.info(f"Validation completed for agent {agent_id}: {'SUCCESS' if is_valid else 'FAILED'}")

            return ValidateInputFormatOutput(
                success=True,
                is_valid=is_valid,
                validation_results=validation_results,
                errors=errors,
                warnings=warnings,
                summary=summary,
            )

        except Exception as e:
            logger.error(f"Error during validation for agent {agent_id}: {e}")
            return ValidateInputFormatOutput(
                success=False,
                is_valid=False,
                validation_results=[],
                errors=[f"Validation error: {str(e)}"],
                warnings=[],
                summary=f"Validation failed due to an error: {str(e)}",
            )

    def _validate_field(self, field_name: str, ad_data: Dict[str, Any], required: bool = True) -> ValidationResult:
        """Validate a specific field.

        Args:
            field_name: Name of the field to validate
            ad_data: Advertisement data
            required: Whether the field is required

        Returns:
            Validation result for the field
        """
        # Check if field exists
        if field_name not in ad_data:
            if required:
                return ValidationResult(
                    field_name=field_name, is_valid=False, error_message=f"Required field '{field_name}' is missing"
                )
            else:
                return ValidationResult(field_name=field_name, is_valid=True, error_message=None)

        value = ad_data[field_name]
        rules = self.validation_rules.get(field_name, {})

        # Check type
        expected_types = rules.get("type", str)
        if not isinstance(expected_types, list):
            expected_types = [expected_types]

        if not any(isinstance(value, t) for t in expected_types):
            return ValidationResult(
                field_name=field_name,
                is_valid=False,
                error_message=f"Field '{field_name}' has invalid type. Expected: {expected_types}, got: {type(value)}",
            )

        # Check string length constraints
        if isinstance(value, str):
            min_length = rules.get("min_length", 0)
            max_length = rules.get("max_length", float("inf"))

            if len(value) < min_length:
                return ValidationResult(
                    field_name=field_name,
                    is_valid=False,
                    error_message=f"Field '{field_name}' is too short. Minimum length: {min_length}, got: {len(value)}",
                )

            if len(value) > max_length:
                return ValidationResult(
                    field_name=field_name,
                    is_valid=False,
                    error_message=f"Field '{field_name}' is too long. Maximum length: {max_length}, got: {len(value)}",
                )

        return ValidationResult(field_name=field_name, is_valid=True, error_message=None)

    def _perform_strict_validation(self, ad_data: Dict[str, Any]) -> List[str]:
        """Perform strict validation checks.

        Args:
            ad_data: Advertisement data to validate

        Returns:
            List of validation errors
        """
        errors = []

        # Check for empty strings
        for key, value in ad_data.items():
            if isinstance(value, str) and value.strip() == "":
                errors.append(f"Field '{key}' cannot be empty")

        # Check for suspicious content patterns
        ad_content = ad_data.get("ad_content", "")
        if isinstance(ad_content, str):
            if ad_content.count("!") > 5:
                errors.append("Ad content has too many exclamation marks")

            if len(ad_content.split()) < 5:
                errors.append("Ad content is too short for meaningful analysis")

        return errors

    def _perform_content_validation(self, ad_data: Dict[str, Any]) -> List[str]:
        """Perform content quality validation checks.

        Args:
            ad_data: Advertisement data to validate

        Returns:
            List of validation warnings
        """
        warnings = []

        ad_content = ad_data.get("ad_content", "")
        if isinstance(ad_content, str):
            # Check for uppercase content
            if ad_content.isupper():
                warnings.append("Ad content is all uppercase, which may appear aggressive")

            # Check for repeated words
            words = ad_content.lower().split()
            if len(words) != len(set(words)):
                warnings.append("Ad content contains repeated words")

            # Check for missing punctuation
            if not any(char in ad_content for char in ".!?"):
                warnings.append("Ad content lacks proper punctuation")

        return warnings
