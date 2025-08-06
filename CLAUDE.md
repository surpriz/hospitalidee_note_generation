# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered rating system for Hospitalidée that automatically generates ratings for patient reviews using Mistral AI. The system analyzes sentiment in French healthcare reviews and calculates ratings on a 1-5 scale with validation and coherence checking.

## Key Commands

### Running the Application
```bash
# Launch main Streamlit interface
python hospitalidee_notation/run_streamlit.py

# Run specific Streamlit app directly
streamlit run hospitalidee_notation/streamlit_apps/besoin_1_notation_auto.py --server.port 8501

# Alternative with custom port
python hospitalidee_notation/run_streamlit.py --port 8502
```

### Development
```bash
# Install dependencies
pip install -r hospitalidee_notation/requirements.txt

# Run tests
pytest hospitalidee_notation/tests/ -v

# Run tests with coverage
pytest hospitalidee_notation/tests/ --cov=src --cov-report=html

# Run specific test modules
pytest hospitalidee_notation/tests/test_sentiment.py
pytest hospitalidee_notation/tests/test_rating.py

# Code formatting and linting
black hospitalidee_notation/
flake8 hospitalidee_notation/
mypy hospitalidee_notation/
```

## Architecture

### Core Components

**Configuration Layer** (`config/`):
- `settings.py`: Centralized configuration using environment variables with Pydantic validation
- `prompts.py`: Standardized Mistral AI prompts for different analysis tasks

**Core Services** (`src/`):
- `mistral_client.py`: Mistral AI client with retry logic, caching, and fallback modes
- `sentiment_analyzer.py`: Sentiment analysis wrapper with validation
- `rating_calculator.py`: Rating calculation with hybrid logic (sentiment + questionnaire)

**User Interface** (`streamlit_apps/`):
- `besoin_1_notation_auto.py`: Main 5-step rating interface
- Applications follow a structured workflow: input → analysis → rating → validation → export

### Key Design Patterns

**Error Handling**: All Mistral API calls include comprehensive error handling with degraded mode fallbacks. When API fails, the system switches to rule-based calculations.

**Caching**: LRU cache implemented for Mistral API calls to improve performance and reduce costs. Cache keys generated from prompt content and parameters.

**Hybrid Rating Calculation**: The system combines two approaches:
1. Sentiment analysis from free-text reviews
2. Structured questionnaire responses
Uses weighted averaging with coherence checking between sources.

**Configuration Management**: All settings centralized in `config/settings.py` with environment variable overrides. Critical settings include API timeouts (30s), required precision (85%), and coherence thresholds (90%).

## Environment Setup

Required environment variables in `.env`:
```bash
MISTRAL_API_KEY=your_mistral_api_key_here  # Mandatory
STREAMLIT_PORT=8501                        # Optional
LOG_LEVEL=INFO                            # Optional
MAX_RESPONSE_TIME=30.0                    # Optional
```

## Important Implementation Details

**French Language Processing**: All prompts and analysis are optimized for French healthcare terminology. The system handles medical vocabulary and French sentiment expressions.

**RGPD Compliance**: No patient data is permanently stored. All caches have TTL, and logs are sanitized to exclude personal information.

**Performance Requirements**: 
- API response time < 30 seconds
- Rating precision target: 85%
- Coherence detection target: 90%

**Mistral AI Configuration**: Uses `mistral-small-latest` model with temperature=0.3 for consistent analytical results. Includes retry logic for rate limiting and connection issues.

The system is designed for the French healthcare market and integrates with Hospitalidée's existing patient feedback platform.