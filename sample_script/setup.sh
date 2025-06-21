#!/bin/bash

# Setup script for PydanticChain samples

echo "Setting up PydanticChain sample scripts..."

# Make scripts executable
chmod +x pydantic_chain_sample.py
chmod +x run_sample.py

# Check if .env exists
if [ ! -f "../.env" ]; then
    echo "Warning: .env file not found in project root."
    echo "Please copy sample.env to .env and configure your API keys:"
    echo "  cp sample.env .env"
    echo "  # Then edit .env with your API keys"
else
    echo "✓ .env file found"
fi

# Check if uv is available
if command -v uv &> /dev/null; then
    echo "Found uv package manager"
    echo "Installing dependencies with uv..."
    cd ..
    uv sync
    cd sample_script
    echo "✓ Dependencies installed with uv"
else
    echo "Warning: uv package manager not found"
    echo "Please install dependencies manually:"
    echo "  pip install langchain-openai langchain-google-genai"
fi

# Check Python dependencies
echo "Checking Python dependencies..."
python3 -c "import sys; sys.path.append('../src'); from src.llm.chain.pydantic_chain import PydanticChain; print('✓ PydanticChain import successful')" 2>/dev/null || {
    echo "Warning: Could not import PydanticChain. Please ensure dependencies are installed."
    if command -v uv &> /dev/null; then
        echo "Try running: uv sync"
    else
        echo "Try running: pip install langchain-openai langchain-google-genai"
    fi
}

echo ""
echo "Setup complete! You can now run the samples:"
echo "  python pydantic_chain_sample.py"
echo "  python run_sample.py azure_openai"
echo "  python run_sample.py gemini"
echo ""
echo "For detailed usage instructions, see README.md" 