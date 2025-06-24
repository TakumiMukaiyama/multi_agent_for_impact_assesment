"""Base agent class for the multi-agent impact assessment system."""

from typing import Dict, List, Optional, Union

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import SystemMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.tools import BaseTool

from src.agents.schemas.agent.ad_evaluation import AdEvaluationOutput
from src.agents.schemas.agent.agent_profile import AgentProfile
from src.agents.tools.base import BaseAgentTool
from src.llm.client.azure_openai_client import AzureOpenAIClient
from src.llm.client.gemini_client import GeminiClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BaseAgent:
    """Base class for all prefectural agents in the system."""

    def __init__(
        self,
        agent_id: str,
        profile: AgentProfile,
        llm_client: Union[AzureOpenAIClient, GeminiClient],
        tools: Optional[Dict[str, BaseAgentTool]] = None,
    ):
        """Initialize a new agent.

        Args:
            agent_id: The identifier for this agent (e.g., "Tokyo")
            profile: Profile information about this agent
            llm_client: The LLM client to use for this agent
            tools: Optional dictionary of tools available to this agent
        """
        self.agent_id = agent_id
        self.profile = profile
        self.llm_client = llm_client
        self.tools_dict = tools or {}

        # Initialize LangChain components
        self.chat_llm = self._initialize_chat_llm()
        self.tools = self._initialize_tools()
        self.agent_executor = self._initialize_executor()

        logger.info(f"Initialized agent for {agent_id} with {len(self.tools)} tools")

    def _initialize_chat_llm(self):
        """Initialize the chat LLM from the client."""
        if hasattr(self.llm_client, "initialize_chat"):
            return self.llm_client.initialize_chat()
        elif hasattr(self.llm_client, "get_llm"):
            return self.llm_client.get_llm()
        else:
            # Fallback - use client directly if it's already a LangChain LLM
            return self.llm_client

    def _initialize_tools(self) -> List[BaseTool]:
        """Initialize LangChain tools from BaseAgentTools."""
        langchain_tools = []
        for tool_name, tool in self.tools_dict.items():
            try:
                langchain_tool = tool.to_tool()
                langchain_tools.append(langchain_tool)
                logger.info(f"Added tool {tool_name} to agent {self.agent_id}")
            except Exception as e:
                logger.error(f"Failed to convert tool {tool_name} for agent {self.agent_id}: {e}")

        return langchain_tools

    def _initialize_executor(self) -> AgentExecutor:
        """Initialize the agent executor."""
        # Create system prompt based on agent profile
        system_message = self._create_system_message()

        # Create prompt template
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=system_message),
                MessagesPlaceholder(variable_name="chat_history", optional=True),
                HumanMessagePromptTemplate.from_template("{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        # Create agent using OpenAI tools format
        agent = create_openai_tools_agent(
            llm=self.chat_llm,
            tools=self.tools,
            prompt=prompt,
        )

        return AgentExecutor(
            agent=agent, tools=self.tools, max_iterations=10, verbose=True, return_intermediate_steps=True
        )

    def _create_system_message(self) -> str:
        """Create system message based on agent profile."""
        profile_dict = self.profile.model_dump()

        system_message = f"""You are a regional advertisement evaluation agent representing {self.agent_id}.

Your Profile:
- Region: {profile_dict.get("region", "Unknown")}
- Population: {profile_dict.get("population", "N/A"):,}
- Cluster: {profile_dict.get("cluster", "N/A")}
- Preferences: {", ".join(profile_dict.get("preferences", []))}

Your Role:
You evaluate advertisements from the perspective of your regional characteristics and cultural preferences.
You have access to various tools to gather information and perform analysis.

Available Tools:
{self._get_tools_description()}

Evaluation Process:
When evaluating an advertisement, you MUST follow this systematic approach:

1. FIRST: Use 'access_local_statistics' to get demographic and economic data for your region
2. THEN: Use 'analyze_ad_content' to understand the advertisement's characteristics
3. NEXT: Use 'estimate_cultural_affinity' to assess cultural fit with your region
4. OPTIONALLY: Use other tools like 'fetch_previous_ads' or 'validate_input_format' if relevant
5. FINALLY: Use 'generate_commentary' to create detailed evaluation

Always use multiple tools to gather comprehensive information before making your final evaluation.
Provide structured results with liking score (0-5), purchase intent score (0-5), and detailed reasoning.
"""
        return system_message

    def _get_tools_description(self) -> str:
        """Get description of available tools."""
        if not self.tools:
            return "No tools available"

        descriptions = []
        for tool in self.tools:
            descriptions.append(f"- {tool.name}: {tool.description}")

        return "\n".join(descriptions)

    def evaluate_ad(
        self,
        ad_id: str,
        ad_content: str,
        neighbor_scores: Optional[Dict[str, Dict[str, float]]] = None,
        **kwargs,
    ) -> AdEvaluationOutput:
        """Evaluate an advertisement from this agent's perspective.

        Args:
            ad_id: Unique identifier for the advertisement
            ad_content: The content of the advertisement to evaluate
            neighbor_scores: Optional dictionary of scores from neighboring prefectures
            **kwargs: Additional keyword arguments

        Returns:
            Evaluation output with scores and commentary
        """
        logger.info(f"Agent {self.agent_id} evaluating ad {ad_id}")

        # Prepare input for the agent
        input_text = f"""
TASK: Evaluate the following advertisement from your regional perspective as {self.agent_id}.

Advertisement Details:
- ID: {ad_id}
- Content: {ad_content}

"""

        if neighbor_scores:
            input_text += "\nNeighbor Scores for Reference:\n"
            for neighbor, scores in neighbor_scores.items():
                liking = scores.get("liking", "N/A")
                purchase = scores.get("purchase_intent", "N/A")
                input_text += f"- {neighbor}: Liking={liking}, Purchase Intent={purchase}\n"

        input_text += f"""

REQUIRED EVALUATION PROCESS:
You must systematically use your available tools to gather comprehensive information:

Step 1: Use 'access_local_statistics' with agent_id='{self.agent_id}' to get demographic data
Step 2: Use 'analyze_ad_content' with agent_id='{self.agent_id}' and ad_content='{ad_content}' to analyze the ad
Step 3: Use 'estimate_cultural_affinity' with agent_id='{self.agent_id}' and ad_content='{ad_content}' to assess cultural fit
Step 4: Use 'generate_commentary' with agent_id='{self.agent_id}' and ad_content='{ad_content}' to create final evaluation

Additional tools available if needed:
- validate_input_format: Check data quality
- fetch_previous_ads: Get historical context
- calculate_aggregate_score: Combine multiple scores
- retrieve_neighbor_scores: Get neighbor data
- log_score_to_db: Record your evaluation

FINAL OUTPUT REQUIREMENTS:
After using the tools, provide your final evaluation in this format:

EVALUATION SUMMARY:
- Liking Score: [0-5 with one decimal place]
- Purchase Intent Score: [0-5 with one decimal place]
- Regional Fit: [Excellent/Good/Fair/Poor]
- Key Insights: [Brief summary of main findings]

DETAILED COMMENTARY:
[Comprehensive explanation of your reasoning based on tool outputs]

Use the tools systematically to provide a thorough, data-driven evaluation.
"""

        try:
            # Execute the agent
            result = self.agent_executor.invoke({"input": input_text})

            # Parse the output
            output_text = result.get("output", "")
            intermediate_steps = result.get("intermediate_steps", [])

            # Log intermediate steps for debugging
            logger.info(f"Agent {self.agent_id} used {len(intermediate_steps)} intermediate steps")
            for i, step in enumerate(intermediate_steps):
                if hasattr(step, "tool") and hasattr(step, "tool_input"):
                    logger.info(
                        f"Step {i + 1}: Used tool {step.tool} with input keys: {list(step.tool_input.keys()) if isinstance(step.tool_input, dict) else 'N/A'}"
                    )

            # Extract scores and commentary (simple parsing for now)
            evaluation_result = self._parse_evaluation_result(output_text, ad_id)

            logger.info(f"Agent {self.agent_id} completed evaluation for ad {ad_id}")
            return evaluation_result

        except Exception as e:
            logger.error(f"Error during evaluation by agent {self.agent_id}: {e}")
            # Return fallback result
            return AdEvaluationOutput(
                agent_id=self.agent_id,
                ad_id=ad_id,
                liking=2.5,  # Neutral score
                purchase_intent=2.5,  # Neutral score
                commentary=f"Error during evaluation: {str(e)}",
                confidence=0.1,
            )

    def _parse_evaluation_result(self, output_text: str, ad_id: str) -> AdEvaluationOutput:
        """Parse the agent's output to extract structured evaluation result.

        Args:
            output_text: Raw output from agent
            ad_id: Advertisement ID

        Returns:
            Structured evaluation output
        """
        # Simple regex-based parsing (could be improved with more sophisticated parsing)
        import re

        # Try to extract scores
        liking_match = re.search(r"liking.*?(?:score)?[:\s]*([0-5](?:\.[0-9]+)?)", output_text, re.IGNORECASE)
        purchase_match = re.search(
            r"purchase.*?intent.*?(?:score)?[:\s]*([0-5](?:\.[0-9]+)?)", output_text, re.IGNORECASE
        )

        liking = float(liking_match.group(1)) if liking_match else 2.5
        purchase_intent = float(purchase_match.group(1)) if purchase_match else 2.5

        # Ensure scores are within valid range
        liking = max(0.0, min(5.0, liking))
        purchase_intent = max(0.0, min(5.0, purchase_intent))

        return AdEvaluationOutput(
            agent_id=self.agent_id,
            ad_id=ad_id,
            liking=liking,
            purchase_intent=purchase_intent,
            commentary=output_text,
            confidence=0.8,  # High confidence when tools are used
        )

    def get_tool(self, tool_name: str) -> Optional[BaseAgentTool]:
        """Get a specific tool by name.

        Args:
            tool_name: Name of the tool to retrieve

        Returns:
            Tool instance if available, None otherwise
        """
        return self.tools_dict.get(tool_name)

    def add_tool(self, tool_name: str, tool: BaseAgentTool) -> None:
        """Add a tool to this agent.

        Args:
            tool_name: Name of the tool
            tool: Tool instance to add
        """
        self.tools_dict[tool_name] = tool
        # Reinitialize tools and executor
        self.tools = self._initialize_tools()
        self.agent_executor = self._initialize_executor()
        logger.info(f"Added tool {tool_name} to agent {self.agent_id}")

    def remove_tool(self, tool_name: str) -> None:
        """Remove a tool from this agent.

        Args:
            tool_name: Name of the tool to remove
        """
        if tool_name in self.tools_dict:
            del self.tools_dict[tool_name]
            # Reinitialize tools and executor
            self.tools = self._initialize_tools()
            self.agent_executor = self._initialize_executor()
            logger.info(f"Removed tool {tool_name} from agent {self.agent_id}")

    def get_available_tools(self) -> List[str]:
        """Get list of available tool names.

        Returns:
            List of tool names
        """
        return list(self.tools_dict.keys())

    def update_llm_client(self, new_client: Union[AzureOpenAIClient, GeminiClient]) -> None:
        """Update the LLM client used by this agent.

        Args:
            new_client: The new LLM client to use
        """
        self.llm_client = new_client
        self.chat_llm = self._initialize_chat_llm()

        # Update tools that use LLM client
        llm_tools = [
            "analyze_ad_content",
            "estimate_cultural_affinity",
            "generate_commentary",
            "calculate_aggregate_score",
        ]
        for tool_name in llm_tools:
            if tool_name in self.tools_dict:
                tool = self.tools_dict[tool_name]
                if hasattr(tool, "llm_client"):
                    tool.llm_client = new_client
                    logger.info(f"Updated LLM client for tool {tool_name} in agent {self.agent_id}")

        # Reinitialize executor
        self.agent_executor = self._initialize_executor()
        logger.info(f"Updated LLM client for agent {self.agent_id}")

    def get_agent_info(self) -> Dict:
        """Get information about this agent.

        Returns:
            Dictionary with agent information
        """
        return {
            "agent_id": self.agent_id,
            "profile": self.profile.model_dump(),
            "available_tools": list(self.tools_dict.keys()),
            "executor_info": {
                "max_iterations": self.agent_executor.max_iterations,
                "tool_count": len(self.tools),
                "verbose": self.agent_executor.verbose,
            },
        }
