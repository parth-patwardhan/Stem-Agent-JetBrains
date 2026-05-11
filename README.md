# StemAgent — Self-Specializing Deep Research Agent

Built as part of the JetBrains AI Engineering internship coding assessment (April 2026).

## What it does
StemAgent is an autonomous deep research agent that self-specializes based on the domain of the query. It uses a full reasoning lifecycle to plan, validate, and execute research tasks without human intervention.

## Architecture
OBSERVE → ARCHITECT → VALIDATE → ITERATE → EXECUTE

- **Model:** claude-opus-4-5 (Anthropic)
- **Framework:** Python, Anthropic SDK
- **Domain:** Deep Research / Knowledge Synthesis

## Key design decisions
- Self-specializing: the agent adapts its toolset and reasoning strategy per domain
- Evaluation loop built-in: VALIDATE step catches low-quality outputs before delivery
- Iterative refinement: ITERATE handles edge cases and ambiguous queries

## Running it
```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key
python stem_agent.py --query "your research question"
```
