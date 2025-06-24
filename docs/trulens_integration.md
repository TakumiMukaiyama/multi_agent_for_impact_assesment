# TruLens Integration Guide

## Overview

This project integrates TruLens for LLM monitoring and evaluation, providing comprehensive insights into the behavior and performance of our multi-agent impact assessment system.

## Features

### 1. LLM Monitoring
- Real-time tracking of LLM inputs and outputs
- Performance metrics collection
- Error tracking and debugging

### 2. Evaluation Framework
- **Relevance**: Measures how relevant responses are to inputs
- **Groundedness**: Evaluates factual accuracy
- **Context Relevance**: Assesses context appropriateness
- **Sentiment Analysis**: Analyzes emotional tone
- **Comprehensiveness**: Measures response completeness
- **Toxicity Detection**: Identifies harmful content
- **Bias Detection**: Detects stereotypes and bias

### 3. Visualization Dashboard
- Interactive web interface for data exploration
- Leaderboard for comparing different model versions
- Detailed evaluation records with feedback scores
- Application performance analytics

## Architecture

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   LLM Application   │───▶│   TruLens Wrapper   │───▶│   TruLens Database  │
│                     │    │                     │    │                     │
│ - PydanticChain     │    │ - Feedback Functions│    │ - SQLite/Custom DB  │
│ - Prefecture Agent  │    │ - Instrumentation   │    │ - Evaluation Records│
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
                                        │
                                        ▼
                           ┌─────────────────────┐
                           │  TruLens Dashboard  │
                           │                     │
                           │ - Web Interface     │
                           │ - Visualization     │
                           │ - Analytics         │
                           └─────────────────────┘
```

## Components

### 1. Core Monitoring Classes

#### TruLensSetup
Handles TruLens initialization and configuration.

```python
from src.llm.monitoring import TruLensSetup

setup = TruLensSetup(database_url="sqlite:///trulens.db")
session = setup.initialize()
setup.start_dashboard(port=8501)
```

#### FeedbackFunctions
Provides evaluation feedback functions for different LLM providers.

```python
from src.llm.monitoring import FeedbackFunctions
from src.core.constants import LLMProviderType

feedback = FeedbackFunctions(LLMProviderType.AZURE_OPENAI)
feedbacks = feedback.get_standard_feedbacks()
```

#### TruLensWrapper
Wraps LangChain applications with TruLens monitoring.

```python
from src.llm.monitoring import TruLensWrapper

wrapper = TruLensWrapper(trulens_setup, feedback_functions)
wrapped_chain = wrapper.wrap_chain(
    chain=your_chain,
    app_name="my_app",
    feedbacks=feedbacks
)
```

### 2. Enhanced Applications

#### TruLensPydanticChain
Enhanced version of PydanticChain with built-in TruLens monitoring.

```python
from src.llm.chain.pydantic_chain_with_trulens import TruLensPydanticChain

chain = TruLensPydanticChain(
    prompt_template=template,
    input_schema=InputSchema,
    output_schema=OutputSchema,
    llm_client=client,
    app_name="impact_assessment",
    enable_trulens=True
)

# Use normally, monitoring happens automatically
result = chain.invoke(input_data)

# Access TruLens features
leaderboard = chain.get_trulens_leaderboard()
records = chain.get_trulens_records()
chain.start_trulens_dashboard()
```

#### TruLensPrefectureAgent
Enhanced prefecture agent with TruLens monitoring.

```python
from src.agents.trulens_agent import TruLensPrefectureAgent

agent = TruLensPrefectureAgent(
    config=agent_config,
    tools=tools,
    enable_trulens=True
)

# Run with monitoring
result = await agent.run("Analyze this advertisement")

# Access monitoring data
leaderboard = agent.get_trulens_leaderboard()
records = agent.get_trulens_records()
```

## API Endpoints

### Dashboard Management
- `POST /api/v1/trulens/dashboard/start` - Start TruLens dashboard
- `POST /api/v1/trulens/dashboard/stop` - Stop TruLens dashboard

### Data Retrieval
- `GET /api/v1/trulens/status` - Get system status
- `GET /api/v1/trulens/leaderboard` - Get performance leaderboard
- `GET /api/v1/trulens/records` - Get evaluation records
- `GET /api/v1/trulens/apps` - Get monitored applications

### Utilities
- `GET /api/v1/trulens/feedback-functions` - List available feedback functions
- `DELETE /api/v1/trulens/reset` - Reset database (caution!)

## Usage Examples

### Basic Chain Monitoring

```python
from src.llm.chain.pydantic_chain_with_trulens import TruLensPydanticChain
from src.llm.client.azure_openai_client import AzureOpenAIClient

# Create client and chain
client = AzureOpenAIClient()
chain = TruLensPydanticChain(
    prompt_template=your_template,
    input_schema=YourInput,
    output_schema=YourOutput,
    llm_client=client,
    app_name="my_chain"
)

# Use the chain
result = chain.invoke(input_data)

# Start dashboard to view results
chain.start_trulens_dashboard()
```

### Agent Monitoring

```python
from src.agents.trulens_agent import TruLensPrefectureAgent

# Create agent with monitoring
agent = TruLensPrefectureAgent(
    config=config,
    tools=tools,
    enable_trulens=True
)

# Run and monitor
result = await agent.run("Your query here")

# View metrics
print(agent.get_agent_info())
```

### Custom Feedback Functions

```python
from trulens.core import Feedback
from src.llm.monitoring import TruLensWrapper, FeedbackFunctions

# Create custom feedback
def custom_feedback_fn(input_text: str, output_text: str) -> float:
    # Your custom evaluation logic
    return score

custom_feedback = Feedback(custom_feedback_fn).on_input_output()

# Use with wrapper
wrapper = TruLensWrapper(setup, feedback_functions)
wrapped_app = wrapper.wrap_chain(
    chain=your_chain,
    app_name="custom_app",
    feedbacks=[custom_feedback]
)
```

## Running the Demo

Execute the demo script to see TruLens in action:

```bash
cd sample_script
python trulens_demo.py
```

This will:
1. Demonstrate PydanticChain with TruLens monitoring
2. Show prefecture agent evaluation
3. Display monitoring data and metrics
4. Provide instructions for accessing the dashboard

## Dashboard Access

After running applications with TruLens monitoring:

1. Start the dashboard via API:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/trulens/dashboard/start" \
        -H "Content-Type: application/json" \
        -d '{"port": 8501, "force": true}'
   ```

2. Or programmatically:
   ```python
   chain.start_trulens_dashboard(port=8501)
   ```

3. Open http://localhost:8501 in your browser

## Configuration

### Environment Variables

Set the following environment variables for different LLM providers:

**Azure OpenAI:**
```bash
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_ID=your_deployment
AZURE_OPENAI_API_VERSION=2023-05-15
```

**Gemini:**
```bash
GEMINI_API_KEY=your_key_here
```

### Database Configuration

By default, TruLens uses SQLite. For production, configure a custom database:

```python
setup = TruLensSetup(database_url="postgresql://user:pass@localhost/trulens")
```

## Best Practices

1. **Selective Monitoring**: Enable TruLens only for critical applications to avoid overhead
2. **Feedback Selection**: Choose appropriate feedback functions for your use case
3. **Database Management**: Regularly clean old records to maintain performance
4. **Dashboard Security**: Secure dashboard access in production environments
5. **Error Handling**: Implement fallback behavior when TruLens fails

## Troubleshooting

### Common Issues

**Dashboard Won't Start:**
- Check if port 8501 is available
- Use `force=True` parameter
- Check firewall settings

**No Evaluation Data:**
- Ensure TruLens is enabled (`enable_trulens=True`)
- Verify LLM provider credentials
- Check feedback function configuration

**Performance Issues:**
- Reduce number of feedback functions
- Use database instead of SQLite for large datasets
- Consider async evaluation for better performance

### Debugging

Enable debug logging:

```python
import logging
logging.getLogger("trulens").setLevel(logging.DEBUG)
```

Check TruLens status:

```bash
curl http://localhost:8000/api/v1/trulens/status
```

## Integration with Existing Code

To add TruLens to existing applications:

1. Replace `PydanticChain` with `TruLensPydanticChain`
2. Replace `PrefectureAgent` with `TruLensPrefectureAgent`
3. Add TruLens API endpoints to your router
4. Configure feedback functions for your use case

## Future Enhancements

- Custom evaluation metrics for impact assessment
- Integration with MLflow for experiment tracking
- Advanced visualization for multi-agent interactions
- Automated model performance regression detection 