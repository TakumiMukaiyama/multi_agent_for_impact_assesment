# Multi-Agent Impact Assessment System

A graph-based multi-agent system for simulating and predicting advertising impact across different geographic regions of Japan. The system models each of Japan's 47 prefectures as individual LLM agents with distinct personas based on regional characteristics.

## Overview

This system combines graph theory with multi-agent LLM architecture to analyze and predict advertising effectiveness. Each prefecture agent evaluates advertisements based on local demographic data and can influence neighboring prefectures through a graph structure representing Japan's geographic adjacency.

Key features:
- 47 prefecture-based LLM agents with unique personas and characteristics
- Graph-based simulation of influence between neighboring regions
- Advertisement evaluation scoring based on liking and purchase intent
- FastAPI backend with MongoDB and PostgreSQL data storage

## Technical Stack

- **Framework**: FastAPI
- **Agent Framework**: LangChain
- **Graph Processing**: NetworkX
- **Parallelization**: Ray
- **Database**: MongoDB & PostgreSQL
- **Configuration**: Pydantic
- **LLM Integration**: Multiple provider support (OpenAI, Azure OpenAI, Google Gemini)

## Getting Started

### Prerequisites

- Python 3.12+
- MongoDB
- PostgreSQL

### Installation

1. Clone the repository
```bash
git clone https://github.com/TakumiMukaiyama/multi_agent_for_impact_assesment.git
cd multi_agent_for_impact_assesment
```

2. Set up a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies
```bash
uv sync
```

4. Create and configure .env file
```bash
cp sample.env .env
# Edit .env with your configuration details
```

5. Run the application
```bash
python main.py
```

The API will be available at http://localhost:8000


## API Endpoints

The API includes the following main endpoints:

- `/api/v1/agents` - Manage prefecture agents
- `/api/v1/ads` - Manage advertisements
- `/api/v1/graph` - Access graph structure
- `/health` - Check service health

## Agent System

Each prefecture agent is equipped with:
- Demographic profile (age distribution, preferences)
- Regional characteristics
- Tools for accessing local and neighboring data

Agents evaluate advertisements on:
- Liking (0.0-5.0 scale)
- Purchase intent (0.0-5.0 scale)
- Provided with commentary explaining the evaluation

## Database Design

The system uses both MongoDB and PostgreSQL:

### MongoDB
- Flexible JSON-based data
- Agent outputs, agent configurations, ad logs

### PostgreSQL
- Structured data for analysis
- Advertisement metadata, statistical data, user feedback

## Future Development

- Real data integration for improved agent accuracy
- Intra-region propagation models (SIR, GNN)
- Frontend visualization with map-based heatmaps
- Multimodal advertisement analysis (images, audio)

## License

[MIT]