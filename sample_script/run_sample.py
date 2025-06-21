#!/usr/bin/env python3
"""
Simple runner script for PydanticChain samples

Usage:
    python run_sample.py [provider]

    provider: azure_openai, gemini (optional)
"""

import os
import sys


def main():
    """Run PydanticChain sample with specified provider."""

    provider = sys.argv[1] if len(sys.argv) > 1 else None

    if provider:
        os.environ["SAMPLE_LLM_PROVIDER"] = provider
        print(f"Using provider: {provider}")

    # Import and run the main sample
    from pydantic_chain_sample import main as run_sample

    run_sample()


if __name__ == "__main__":
    main()
