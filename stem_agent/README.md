# StemAgent

A self-specializing AI agent. Given a task class ("Deep Research"), it:

1. **Observes** — studies how that class of tasks is typically approached
2. **Architects** — designs its own system prompt, tool list, and decomposition strategy
3. **Validates** — scores itself using a judge model (0–1 across 5 criteria)
4. **Iterates** — patches its spec based on specific failure feedback
5. **Executes** — converged agent handles real queries

## Setup

```bash
pip install openai
export OPENAI_API_KEY=your_key_here
```

## Quick demo

```bash
python demo.py
```

## Full before/after experiment

```bash
python experiment.py
# Results saved to results/comparison_table.txt
```

## Project structure

```
stem_agent/
  core/
    stem_agent.py   ← StemAgent class (full lifecycle)
    baseline.py     ← Generic baseline for comparison
  experiment.py     ← Before/after benchmark runner
  demo.py           ← Interactive demo
  writeup.pdf       ← 3-page write-up (approach, experiments, Task #2)
```
