#!/usr/bin/env python3
"""
PydanticChain sample script

This script demonstrates how to use PydanticChain with different LLM providers.
"""

import os
import sys
from typing import List

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from pydantic import Field

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from src.core.constants import LLMProviderType
from src.core.llm_settings import llm_settings
from src.llm.chain.pydantic_chain import PydanticChain
from src.llm.client.azure_openai_client import AzureOpenAIClient
from src.llm.client.gemini_client import GeminiClient
from src.llm.dependancy.base import BaseInput, BaseOutput


# Define input and output schemas
class SummaryInput(BaseInput):
    """Input schema for text summarization."""

    text: str = Field(description="Text to summarize")
    max_words: int = Field(default=100, description="Maximum number of words in summary")


class SummaryOutput(BaseOutput):
    """Output schema for text summarization."""

    summary: str = Field(description="Summarized text")
    key_points: List[str] = Field(description="Key points from the text")
    sentiment: str = Field(description="Overall sentiment (positive, negative, neutral)")


class QuestionAnswerInput(BaseInput):
    """Input schema for question answering."""

    context: str = Field(description="Context text")
    question: str = Field(description="Question to answer")


class QuestionAnswerOutput(BaseOutput):
    """Output schema for question answering."""

    answer: str = Field(description="Answer to the question")
    confidence: float = Field(description="Confidence score (0.0 to 1.0)")
    evidence: List[str] = Field(description="Evidence from context supporting the answer")


def create_summary_prompt() -> PromptTemplate:
    """Create prompt template for text summarization."""

    template = """You are a professional text summarizer. Please analyze the following text and provide a summary.

Text to summarize:
{text}

Requirements:
- Maximum {max_words} words
- Extract key points as a list
- Determine overall sentiment (positive, negative, neutral)

Please respond in the following JSON format exactly:
{format_instructions}

Make sure to include ALL required fields: summary, key_points (as array), and sentiment.
"""

    return PromptTemplate(
        input_variables=["text", "max_words"],
        template=template,
        partial_variables={"format_instructions": "{format_instructions}"},
    )


def create_qa_prompt() -> PromptTemplate:
    """Create prompt template for question answering."""

    template = """You are a helpful assistant that answers questions based on provided context.

Context:
{context}

Question: {question}

Please provide a comprehensive answer based on the context and respond in the following JSON format exactly:
{format_instructions}

Make sure to include ALL required fields: answer, confidence (0.0-1.0), and evidence (as array).
"""

    return PromptTemplate(
        input_variables=["context", "question"],
        template=template,
        partial_variables={"format_instructions": "{format_instructions}"},
    )


def setup_azure_openai_client() -> AzureOpenAIClient:
    """Setup Azure OpenAI client."""

    print("Setting up Azure OpenAI client...")
    # Initialize with explicit embedding_model parameter to avoid attribute error
    settings = llm_settings.providers[LLMProviderType.AZURE_OPENAI]
    api_key = settings.api_key.get_secret_value()

    client = AzureOpenAIClient(
        base_url=settings.endpoint,
        api_version=settings.api_version,
        api_key=api_key,
        deployment_name=settings.deployment_id,
        embedding_model=settings.embedding_model,  # Default embedding model
    )
    print(f"✓ Azure OpenAI client initialized with deployment: {client.deployment_name}")
    return client


def setup_gemini_client() -> GeminiClient:
    """Setup Gemini client."""

    print("Setting up Gemini client...")
    api_key = llm_settings.providers[LLMProviderType.GEMINI].api_key.get_secret_value()
    if not api_key:
        raise ValueError("Gemini API key not found. Please set GEMINI_API_KEY in your environment.")

    client = GeminiClient(api_key=api_key, chat_model="gemini-pro", embedding_model="models/embedding-001")
    print("✓ Gemini client initialized")
    return client


def run_summary_example(chain: PydanticChain):
    """Run text summarization example."""

    print("\n" + "=" * 60)
    print("Running Text Summarization Example")
    print("=" * 60)

    sample_text = """
    Artificial Intelligence (AI) has transformed numerous industries over the past decade. 
    From healthcare to finance, AI applications are revolutionizing how we work and live. 
    Machine learning algorithms can now diagnose diseases with accuracy comparable to human experts, 
    while natural language processing enables chatbots to provide customer service around the clock. 
    However, the rapid advancement of AI also raises important questions about job displacement, 
    privacy concerns, and the need for ethical guidelines. Companies are investing billions in AI research, 
    and governments are developing policies to regulate its use. The future of AI looks promising, 
    but it requires careful consideration of its societal implications.
    """

    input_data = SummaryInput(text=sample_text.strip(), max_words=80)

    try:
        result = chain.invoke_with_retry(input_data)
        print(f"Summary: {result.summary}")
        print(f"Key Points: {', '.join(result.key_points)}")
        print(f"Sentiment: {result.sentiment}")

    except Exception as e:
        print(f"Error in summarization: {e}")


def run_qa_example(chain: PydanticChain):
    """Run question answering example."""

    print("\n" + "=" * 60)
    print("Running Question Answering Example")
    print("=" * 60)

    context = """
    The Python programming language was created by Guido van Rossum and first released in 1991. 
    Python is known for its simple and readable syntax, making it an excellent choice for beginners. 
    It supports multiple programming paradigms including procedural, object-oriented, and functional programming. 
    Python has a large standard library and an extensive ecosystem of third-party packages available through PyPI. 
    Popular applications of Python include web development, data science, artificial intelligence, and automation.
    """

    question = "Who created Python and when was it first released?"

    input_data = QuestionAnswerInput(context=context, question=question)

    try:
        result = chain.invoke_with_retry(input_data)
        print(f"Question: {question}")
        print(f"Answer: {result.answer}")
        print(f"Confidence: {result.confidence}")
        print(f"Evidence: {', '.join(result.evidence)}")

    except Exception as e:
        print(f"Error in question answering: {e}")


def main():
    """Main function to run PydanticChain examples."""

    # Load environment variables
    load_dotenv()

    print("PydanticChain Sample Script")
    print("=" * 40)

    # Check available providers
    available_providers = []
    if llm_settings.providers[LLMProviderType.AZURE_OPENAI].enabled:
        available_providers.append("azure_openai")
    if llm_settings.providers[LLMProviderType.GEMINI].enabled:
        available_providers.append("gemini")

    if not available_providers:
        print("No LLM providers are enabled. Please check your environment variables.")
        print("Available providers: azure_openai, gemini")
        return

    print(f"Available providers: {', '.join(available_providers)}")

    # Choose provider (default to first available)
    provider = os.getenv("SAMPLE_LLM_PROVIDER", available_providers[0])

    if provider not in available_providers:
        print(f"Provider '{provider}' is not available or enabled.")
        provider = available_providers[0]

    print(f"Using provider: {provider}")

    try:
        # Setup LLM client
        if provider == "azure_openai":
            llm_client = setup_azure_openai_client()
        elif provider == "gemini":
            llm_client = setup_gemini_client()
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        # Example 1: Text Summarization
        print("\n" + "=" * 60)
        print("Creating Summarization Chain")
        print("=" * 60)

        summary_prompt = create_summary_prompt()
        summary_chain = PydanticChain(
            prompt_template=summary_prompt,
            input_schema=SummaryInput,
            output_schema=SummaryOutput,
            llm_client=llm_client,
        )

        print("Chain Info:")
        for key, value in summary_chain.get_chain_info().items():
            print(f"  {key}: {value}")

        run_summary_example(summary_chain)

        # Example 2: Question Answering
        print("\n" + "=" * 60)
        print("Creating Question Answering Chain")
        print("=" * 60)

        qa_prompt = create_qa_prompt()
        qa_chain = PydanticChain(
            prompt_template=qa_prompt,
            input_schema=QuestionAnswerInput,
            output_schema=QuestionAnswerOutput,
            llm_client=llm_client,
        )

        print("Chain Info:")
        for key, value in qa_chain.get_chain_info().items():
            print(f"  {key}: {value}")

        run_qa_example(qa_chain)

        print("\n" + "=" * 60)
        print("Sample completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"Error: {e}")
        print("Please check your environment variables and API keys.")


if __name__ == "__main__":
    main()
