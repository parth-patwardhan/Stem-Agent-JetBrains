# StemAgent — Self-Specializing AI Research Agent

> Built as the JetBrains AI Engineering internship coding challenge submission (April 2026).

StemAgent is an autonomous deep research agent that **self-specializes at runtime** based on the domain of the incoming query. Rather than using a fixed reasoning strategy, it dynamically reconfigures its own architecture — choosing tools, reasoning depth, and validation criteria — before executing any task.

---

## How it works

```
User query
    ↓
OBSERVE     — parse intent, detect domain, assess complexity
    ↓
ARCHITECT   — select tool configuration and reasoning strategy for this specific query
    ↓
VALIDATE    — verify the plan before execution; catch bad strategies early
    ↓
ITERATE     — refine if validation fails or output quality is below threshold
    ↓
EXECUTE     — run the finalised strategy and deliver output
```

The key insight: most agentic systems use a fixed pipeline for every query. StemAgent decides **how to reason** before it reasons — making it significantly more reliable on out-of-distribution or complex queries.

---

## Architecture

| Component | Detail |
|---|---|
| **Model** | Claude Opus (Anthropic) |
| **Orchestration** | Python, Anthropic SDK |
| **Tool integration** | REST APIs, MCP (Model Context Protocol) |
| **Domain** | Deep Research / Knowledge Synthesis |
| **Lifecycle** | OBSERVE → ARCHITECT → VALIDATE → ITERATE → EXECUTE |

---

## Key design decisions

**Self-specializing architecture selection**  
The ARCHITECT step dynamically configures reasoning strategy, tool selection, and output format based on domain signals detected in OBSERVE. A query about a technical codebase gets a different strategy than a market research query.

**Built-in evaluation loop**  
VALIDATE catches low-quality plans before execution rather than after. This prevents wasted computation and hallucinatory outputs from propagating through the pipeline.

**Iterative refinement**  
ITERATE handles edge cases, ambiguous queries, and partial failures — the agent retries with a modified strategy rather than returning a degraded response.

---

## Running it

```bash
git clone https://github.com/parth-patwardhan/Stem-Agent-JetBrains.git
cd Stem-Agent-JetBrains
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key
python stem_agent.py --query "your research question here"
```

---

## Context

Built independently as a JetBrains AI Engineering challenge submission. The challenge required designing a novel agentic system demonstrating meaningful architectural contribution beyond standard ReAct-style agents.

---

*Part of the portfolio of [Parth Patwardhan](https://github.com/parth-patwardhan) — AI Engineer, Universität Stuttgart.*
