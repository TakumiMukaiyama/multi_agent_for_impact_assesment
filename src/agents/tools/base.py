"""Base classes and utilities for agent tools."""

import asyncio
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel

from src.agents.schemas.tools.base import ToolInput, ToolOutput
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Define generic types for tool input/output
TInput = TypeVar("TInput", bound=BaseModel)
TOutput = TypeVar("TOutput", bound=BaseModel)

# Export classes for external use
__all__ = ["BaseAgentTool", "ToolInput", "ToolOutput", "TInput", "TOutput"]


class BaseAgentTool(Generic[TInput, TOutput], ABC):
    """Base class for all agent tools.

    This provides a standardized interface for tool implementation and usage.
    """

    def __init__(self, name: str, description: str):
        """Initialize the tool.

        Args:
            name: Name of the tool
            description: Description of what the tool does
        """
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, input_data: TInput) -> TOutput:
        """Execute the tool with the given input.

        Args:
            input_data: Input data for the tool

        Returns:
            Tool execution result
        """
        pass

    def to_langchain_tool(self) -> BaseTool:
        """Convert this tool to a LangChain tool.

        Returns:
            LangChain-compatible tool
        """

        def _wrapped_func(**kwargs):
            try:
                logger.info(f"Executing tool {self.name} with kwargs: {list(kwargs.keys())}")

                # Convert kwargs to the input type
                input_type = self._get_input_type()
                input_instance = input_type(**kwargs)

                # Execute the tool synchronously by running the async function
                loop = None
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # If there's already a running loop, we need to create a new thread
                        import concurrent.futures

                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(asyncio.run, self.execute(input_instance))
                            result = future.result()
                    else:
                        result = loop.run_until_complete(self.execute(input_instance))
                except RuntimeError:
                    # No event loop, create a new one
                    result = asyncio.run(self.execute(input_instance))

                # Return as dict for LangChain consumption
                result_dict = result.model_dump()
                logger.info(f"Tool {self.name} completed successfully")
                return result_dict

            except Exception as e:
                error_msg = f"Error in tool {self.name}: {str(e)}"
                logger.error(error_msg)

                # Return a basic error response
                return {"success": False, "message": error_msg, "error": str(e)}

        # Create and return the LangChain tool
        return StructuredTool(
            name=self.name,
            description=self.description,
            func=_wrapped_func,
            args_schema=self._get_input_type(),
        )

    def to_tool(self) -> BaseTool:
        """Alias for to_langchain_tool() for compatibility.

        Returns:
            LangChain-compatible tool
        """
        return self.to_langchain_tool()

    def _get_input_type(self) -> type:
        """Get the input type for this tool.

        Returns:
            Input type class
        """
        # Extract the input type from the generic parameters
        from typing import get_args, get_origin

        for base in self.__class__.__orig_bases__:  # type: ignore
            if get_origin(base) is BaseAgentTool:
                args = get_args(base)
                if args and len(args) >= 1:
                    return args[0]

        # Fallback to BaseModel if type extraction fails
        return BaseModel
