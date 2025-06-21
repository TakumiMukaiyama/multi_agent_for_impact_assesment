"""
Gemini API integration using LangChain.
"""

from typing import List

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings


class GeminiClient:
    """
    Gemini API client using LangChain.
    """

    def __init__(
        self,
        api_key: str,
        chat_model: str,
        embedding_model: str,
    ):
        """
        Initialize Gemini API client.

        Args:
            api_key: Gemini API key
            chat_model: Model name for chat
            embedding_model: Model name for embeddings
        """
        self.api_key = api_key

        if not self.api_key:
            raise ValueError("Gemini API key not provided. Please check your settings.")

        # Initialize embeddings client
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=embedding_model,
            google_api_key=self.api_key,
        )

        # Initialize chat client
        self.llm = ChatGoogleGenerativeAI(
            model=chat_model,
            google_api_key=self.api_key,
            temperature=0,
            top_p=0.95,
            top_k=40,
            max_output_tokens=16384,
        )

    def initialize_chat(self) -> ChatGoogleGenerativeAI:
        """
        Initialize chat model.

        Returns:
            ChatGoogleGenerativeAI instance
        """
        return self.llm

    def initialize_embedding(self) -> GoogleGenerativeAIEmbeddings:
        """
        Initialize embedding model.

        Returns:
            GoogleGenerativeAIEmbeddings instance
        """
        return self.embeddings

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for texts.

        Args:
            texts: List of texts to get embeddings for

        Returns:
            List of embeddings
        """
        return self.embeddings.embed_documents(texts)
