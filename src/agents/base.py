from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from langchain.agents import AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.tools import BaseTool
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from src.core import settings


class AgentConfig(BaseModel):
    """Configuration for an agent."""
    agent_id: str
    persona_config: Dict[str, Any]
    prompt_template: str
    use_memory: bool = Field(default=True)


class PrefectureAgent:
    """Base agent class representing a prefecture in Japan."""
    
    def __init__(self, config: AgentConfig, tools: List[BaseTool], llm: Optional[ChatOpenAI] = None):
        """Initialize a new prefecture agent.
        
        Args:
            config: Agent configuration.
            tools: List of tools available to the agent.
            llm: Language model to use (if None, default will be created based on app settings).
        """
        self.config = config
        self.tools = tools
        
        # Create LLM if not provided
        if llm is None:
            llm_provider = settings.llm.default_provider
            if llm_provider.value == "openai" and settings.llm.providers[llm_provider].enabled:
                llm = ChatOpenAI(
                    model=settings.llm.providers[llm_provider].model_name,
                    openai_api_key=settings.llm.providers[llm_provider].api_key.get_secret_value(),
                    temperature=0.1,
                )
            elif llm_provider.value == "azure_openai" and settings.llm.providers[llm_provider].enabled:
                azure_settings = settings.llm.providers[llm_provider]
                llm = ChatOpenAI(
                    azure_deployment=azure_settings.deployment_id,
                    openai_api_version=azure_settings.api_version,
                    openai_api_key=azure_settings.api_key.get_secret_value(),
                    azure_endpoint=azure_settings.endpoint,
                    temperature=0.1,
                )
            else:
                raise ValueError(f"LLM provider {llm_provider} is not available or not enabled")
        
        self.llm = llm
        
        # Initialize agent memory if enabled
        self.memory = None
        if config.use_memory:
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
            )
        
        # Create agent executor
        self.agent_executor = self._create_agent_executor()
    
    def _create_agent_executor(self) -> AgentExecutor:
        """Create an agent executor with the given tools and LLM."""
        # Format the system prompt with persona information
        system_prompt = self.config.prompt_template.format(
            agent_id=self.config.agent_id,
            persona=self.config.persona_config,
        )
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent executor
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=prompt,
            tools=self.tools,
            llm=self.llm,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
        )
        
        return agent_executor
    
    async def run(self, input_text: str) -> Dict[str, Any]:
        """Run the agent on the given input text."""
        result = await self.agent_executor.ainvoke({"input": input_text})
        return result