#!/usr/bin/env python3
"""
Simple runner script for Multi-Agent Impact Assessment samples

Usage:
    python run_multi_agent.py [provider]

    provider: azure_openai, gemini (optional)
"""

import os
import sys


def main():
    """Run Multi-Agent Impact Assessment sample with specified provider."""

    provider = sys.argv[1] if len(sys.argv) > 1 else None

    if provider:
        os.environ["SAMPLE_LLM_PROVIDER"] = provider
        print(f"Using provider: {provider}")

    # Import and run the main sample
    from run_multi_agent_sample import main as run_sample

    run_sample()


if __name__ == "__main__":
    main()
