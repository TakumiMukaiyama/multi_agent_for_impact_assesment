#!/usr/bin/env python3
"""
Simple TruLens Demo Script

This script demonstrates TruLens functionality with the modern API (v1.5+).
Fixed import paths and OpenAI compatibility issues.
"""

import os

from trulens.apps.langchain import TruChain
from trulens.core.session import TruSession

from src.core.llm_settings import LLMProviderType, llm_settings


def demo_basic_trulens():
    """Demonstrate basic TruLens usage with the modern API."""
    print("Basic TruLens Demo")
    print("=" * 40)

    try:
        # Use TruLens v1.5+ with correct import paths

        # Import LangChain components
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import PromptTemplate
        from langchain_openai import ChatOpenAI

        # Check available providers from settings
        azure_settings = llm_settings.providers[LLMProviderType.AZURE_OPENAI]
        openai_settings = llm_settings.providers[LLMProviderType.OPENAI]

        if not azure_settings.enabled and not openai_settings.enabled:
            print("Warning: No LLM providers are enabled in settings")
            return False

        # Initialize TruLens session
        session = TruSession()
        print("TruLens session initialized successfully!")

        # Create a simple LangChain chain
        prompt = PromptTemplate(
            template="You are an expert on Japanese culture. Answer this question: {question}",
            input_variables=["question"],
        )

        # Initialize LLM using settings
        llm = None
        if azure_settings.enabled and azure_settings.api_key.get_secret_value():
            from langchain_openai import AzureChatOpenAI

            llm = AzureChatOpenAI(
                azure_deployment=azure_settings.deployment_id,
                model_name=azure_settings.deployment_id,  # Explicit model name for TruLens tracking
                api_version=azure_settings.api_version,
                azure_endpoint=azure_settings.endpoint,
                api_key=azure_settings.api_key.get_secret_value(),
            )
        elif openai_settings.enabled and openai_settings.api_key.get_secret_value():
            llm = ChatOpenAI(
                model=openai_settings.model_name,
                api_key=openai_settings.api_key.get_secret_value(),
                temperature=0.1,
            )

        if llm is None:
            print("Error: Could not initialize LLM. Please check your settings and API keys.")
            return False

        # Create the chain
        chain = prompt | llm | StrOutputParser()
        print("LangChain pipeline created!")

        # Wrap the chain with TruLens (without feedback functions to avoid OpenAI endpoint issues)
        tru_chain = TruChain(
            chain,
            app_name="japanese_culture_qa",
            app_version="v1.0",
            feedbacks=[],  # Disabled feedback functions for now to avoid OpenAI endpoint compatibility issues
        )

        print("Chain wrapped with TruLens!")

        # Sample questions
        questions = [
            "What is the significance of cherry blossoms in Japanese culture?",
            "How do Japanese business cards (meishi) reflect cultural values?",
        ]

        print(f"\nRunning {len(questions)} questions through TruLens monitoring...\n")

        # Run questions with TruLens monitoring
        for i, question in enumerate(questions, 1):
            print(f"Question {i}: {question}")

            with tru_chain as recording:
                answer = tru_chain.app.invoke({"question": question})

            print(f"Answer: {answer[:200]}{'...' if len(answer) > 200 else ''}")
            print("-" * 50)

        # Get and display results
        print("\nTruLens Results:")
        print("=" * 40)

        try:
            # Get leaderboard using modern API
            leaderboard = session.get_leaderboard()
            if leaderboard is not None and len(leaderboard) > 0:
                print("Leaderboard:")
                print(leaderboard)
            else:
                print("No leaderboard data available yet.")
        except Exception as e:
            print(f"Could not get leaderboard: {e}")

        try:
            # Get records using modern API
            records = session.get_records_and_feedback()
            if records is not None and len(records) > 0:
                print(f"\nTotal records: {len(records)}")
                print("Recent evaluations completed!")
            else:
                print("No records available yet.")
        except Exception as e:
            print(f"Could not get records: {e}")

        # Instructions for dashboard
        print("\nTo view the TruLens dashboard:")
        print("1. Run: session.run_dashboard()")
        print("2. Open: http://localhost:8501")
        print("3. Or use the API endpoints we implemented")

        return True

    except ImportError as e:
        print(f"Import error: {e}")
        print("Please ensure TruLens is installed:")
        print("pip install trulens trulens-providers-openai")
        return False
    except Exception as e:
        print(f"Error running demo: {e}")
        return False


def demo_with_custom_rag():
    """Demonstrate TruLens with a custom RAG implementation using modern API."""
    print("\nCustom RAG with TruLens Demo")
    print("=" * 40)

    try:
        # Use modern TruLens API
        from trulens.apps.app import TruApp, instrument  # Use TruApp instead of deprecated TruCustomApp
        from trulens.core import TruSession

        # Sample knowledge base about Japan
        japan_knowledge = """
        Japan has a rich cultural heritage including tea ceremony, flower arrangement (ikebana), and traditional festivals.
        Japanese business culture emphasizes respect, hierarchy, and long-term relationships.
        Japanese cuisine (washoku) is UNESCO recognized and emphasizes seasonal ingredients and presentation.
        Japan is known for innovations in robotics, transportation (shinkansen), and consumer electronics.
        """

        class SimpleRAG:
            """Simple RAG implementation for demonstration."""

            def __init__(self, knowledge_base):
                self.knowledge_base = knowledge_base

            @instrument
            def retrieve(self, query: str) -> str:
                """Retrieve relevant context from knowledge base."""
                # Simple keyword-based retrieval
                if any(word in query.lower() for word in ["business", "work", "company"]):
                    return "Japanese business culture emphasizes respect, hierarchy, and long-term relationships."
                elif any(word in query.lower() for word in ["food", "cuisine", "eat"]):
                    return "Japanese cuisine (washoku) is UNESCO recognized and emphasizes seasonal ingredients and presentation."
                elif any(word in query.lower() for word in ["culture", "tradition", "festival"]):
                    return "Japan has a rich cultural heritage including tea ceremony, flower arrangement (ikebana), and traditional festivals."
                else:
                    return self.knowledge_base

            @instrument
            def generate_completion(self, query: str, context: str) -> str:
                """Generate answer based on query and context."""
                # In a real implementation, this would use an LLM
                return f"Based on the available information: {context}\n\nRegarding your question '{query}', this provides relevant context about Japanese culture and practices."

            @instrument
            def query(self, question: str) -> str:
                """Full RAG pipeline."""
                context = self.retrieve(question)
                answer = self.generate_completion(question, context)
                return answer

        # Initialize TruLens session
        session = TruSession()

        # Create RAG instance
        rag = SimpleRAG(japan_knowledge)

        # Wrap with TruLens using modern API (without feedback functions to avoid OpenAI endpoint issues)
        tru_rag = TruApp(
            rag,
            app_name="RAG-japan",
            app_version="v1",
            feedbacks=[],  # Disabled feedback functions for compatibility
        )

        # Test questions
        questions = [
            "Tell me about Japanese business culture",
            "What is special about Japanese food?",
        ]

        print(f"Running {len(questions)} questions through custom RAG...\n")

        for i, question in enumerate(questions, 1):
            print(f"Question {i}: {question}")

            with tru_rag as recording:
                answer = rag.query(question)

            print(f"Answer: {answer[:200]}{'...' if len(answer) > 200 else ''}")
            print("-" * 50)

        # Display results
        try:
            leaderboard = session.get_leaderboard()
            if leaderboard is not None:
                print("Leaderboard results:")
                print(leaderboard)
        except Exception as e:
            print(f"Could not get leaderboard: {e}")

        print("Custom RAG demo completed!")
        return True

    except Exception as e:
        print(f"Error in custom RAG demo: {e}")
        return False


def main():
    """Main function to run TruLens demos."""
    print("TruLens Demo Script for Multi-Agent Impact Assessment")
    print("=" * 60)
    print("Using modern TruLens API (v1.5+) - No deprecation warnings!")
    print("Note: OpenAI feedback functions disabled for compatibility")
    print()

    # Check environment
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("AZURE_OPENAI_API_KEY"):
        print("Warning: No OpenAI API keys found.")
        print("Please set either OPENAI_API_KEY or Azure OpenAI environment variables:")
        print("- AZURE_OPENAI_API_KEY")
        print("- AZURE_OPENAI_ENDPOINT")
        print("- AZURE_OPENAI_DEPLOYMENT_ID")
        print("- AZURE_OPENAI_API_VERSION")
        print("\nDemo will continue but may fail without proper API keys.")
        print()

    success = True

    # Run basic demo
    if not demo_basic_trulens():
        success = False

    # Run custom RAG demo
    if not demo_with_custom_rag():
        success = False

    if success:
        print("\nAll demos completed successfully!")
        print("🎉 No more deprecation warnings!")
        print("\nNext steps:")
        print("1. Try the full TruLens integration in our main application")
        print("2. Run: python sample_script/trulens_demo.py")
        print("3. Use the TruLens API endpoints at /api/v1/trulens/")
        print("4. Start the dashboard to visualize results")
        print("\nNote: To enable OpenAI feedback functions, ensure OpenAI library compatibility")
    else:
        print("\nSome demos failed. Check your environment setup.")


if __name__ == "__main__":
    main()
