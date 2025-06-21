import time
from typing import Any, Type, Union

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

from src.llm.client.azure_openai_client import AzureOpenAIClient
from src.llm.client.gemini_client import GeminiClient
from src.llm.dependancy.base import BaseInput, BaseOutput


class PydanticChain:
    """Generic Pydantic-based chain for structured LLM interactions.

    This chain can work with any prompt template, input/output schema, and LLM client.
    """

    def __init__(
        self,
        prompt_template: PromptTemplate,
        input_schema: Type[BaseInput],
        output_schema: Type[BaseOutput],
        llm_client: Union[AzureOpenAIClient, GeminiClient],
    ):
        """Initialize the Pydantic chain.

        Args:
            prompt_template: LangChain prompt template to use
            input_schema: Pydantic schema for input validation
            output_schema: Pydantic schema for output parsing
            llm_client: LLM client instance (AzureOpenAI or Gemini)
        """
        self.prompt_template = prompt_template
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.llm_client = llm_client

        # Initialize chat model based on client type
        if isinstance(llm_client, AzureOpenAIClient):
            self.chat_llm = llm_client.initialize_chat()
        elif isinstance(llm_client, GeminiClient):
            self.chat_llm = llm_client.initialize_chat()
        else:
            raise ValueError(f"Unsupported LLM client type: {type(llm_client)}")

        # Set up output parser and chain
        self.parser = PydanticOutputParser(pydantic_object=self.output_schema)
        self.chain = self.prompt_template | self.chat_llm | self.parser

    def invoke_with_retry(self, inputs: BaseInput, max_retries: int = 10, **kwargs) -> Any:
        """Invoke the chain with retry logic for error handling.

        Args:
            inputs: Input data matching the input schema
            max_retries: Maximum number of retry attempts
            **kwargs: Additional arguments passed to chain invoke

        Returns:
            Parsed output matching the output schema

        Raises:
            Exception: If all retry attempts fail
        """
        try:
            return self.invoke(inputs, **kwargs)
        except Exception as e:
            error_msg = str(e).lower()

            # Handle API key issues
            if any(msg in error_msg for msg in ["invalid api key", "invalid authorization"]):
                # For Azure OpenAI, re-initialize the chat model
                if isinstance(self.llm_client, AzureOpenAIClient):
                    self.chat_llm = self.llm_client.initialize_chat()
                    self.chain = self.prompt_template | self.chat_llm | self.parser
                    return self.invoke(inputs, **kwargs)
                raise e

            # Handle rate limiting with exponential backoff
            elif any(msg in error_msg for msg in ["rate limit", "requests", "threshold"]):
                last_error = e
                for attempt in range(max_retries - 1):  # Excluding initial attempt
                    wait_time = min(60 * (2**attempt), 300)  # Exponential backoff, max 5 minutes
                    time.sleep(wait_time)
                    try:
                        return self.invoke(inputs, **kwargs)
                    except Exception as retry_e:
                        last_error = retry_e
                        continue
                raise last_error

            # Re-raise other errors
            raise e

    def invoke(self, inputs: BaseInput, **kwargs) -> Any:
        """Invoke the chain with input validation.

        Args:
            inputs: Input data matching the input schema
            **kwargs: Additional arguments passed to chain invoke

        Returns:
            Parsed output matching the output schema
        """
        # Validate input
        if not isinstance(inputs, self.input_schema):
            raise ValueError(f"Input must be instance of {self.input_schema.__name__}")

        # Convert input to dict
        input_dict = inputs.model_dump()

        # Special handling for neighbor_scores formatting
        if "neighbor_scores" in input_dict:
            neighbor_scores = input_dict["neighbor_scores"]
            if neighbor_scores is None:
                input_dict["neighbor_scores"] = "No neighboring prefecture evaluations available."
            elif isinstance(neighbor_scores, dict):
                # Format neighbor scores as string
                neighbor_lines = []
                for neighbor, scores in neighbor_scores.items():
                    if isinstance(scores, dict):
                        line = f"- {neighbor}: Liking: {scores.get('liking', 'N/A')}, Purchase Intent: {scores.get('purchase_intent', 'N/A')}"
                    else:
                        line = f"- {neighbor}: {scores}"
                    neighbor_lines.append(line)
                input_dict["neighbor_scores"] = (
                    "\n".join(neighbor_lines) if neighbor_lines else "No neighboring prefecture evaluations available."
                )

        # Invoke chain with validated input
        return self.chain.invoke(
            input_dict,
            **kwargs,
        )

    def update_llm_client(self, llm_client: Union[AzureOpenAIClient, GeminiClient]) -> None:
        """Update the LLM client and reinitialize the chain.

        Args:
            llm_client: New LLM client instance
        """
        self.llm_client = llm_client

        # Re-initialize chat model
        if isinstance(llm_client, AzureOpenAIClient):
            self.chat_llm = llm_client.initialize_chat()
        elif isinstance(llm_client, GeminiClient):
            self.chat_llm = llm_client.initialize_chat()
        else:
            raise ValueError(f"Unsupported LLM client type: {type(llm_client)}")

        # Rebuild chain
        self.chain = self.prompt_template | self.chat_llm | self.parser

    def update_prompt_template(self, prompt_template: PromptTemplate) -> None:
        """Update the prompt template and rebuild the chain.

        Args:
            prompt_template: New prompt template
        """
        self.prompt_template = prompt_template
        self.chain = self.prompt_template | self.chat_llm | self.parser

    def get_chain_info(self) -> dict:
        """Get information about the current chain configuration.

        Returns:
            Dictionary containing chain configuration details
        """
        return {
            "input_schema": self.input_schema.__name__,
            "output_schema": self.output_schema.__name__,
            "llm_client_type": type(self.llm_client).__name__,
            "chat_model_type": type(self.chat_llm).__name__,
            "prompt_variables": list(self.prompt_template.input_variables),
        }
