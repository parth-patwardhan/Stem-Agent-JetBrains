"""
experiment.py — Run the full before/after comparison experiment.

Usage:
    python experiment.py

Outputs:
    - results/experiment_results.json  (raw scores)
    - results/comparison_table.txt     (human-readable)
"""

import json
import time
from pathlib import Path
from core.stem_agent import StemAgent, score_response
from core.baseline import run_baseline

TASK_CLASS = "Deep Research"

TEST_QUERIES = [
    "What are the main technical approaches to reducing hallucination in large language models?",
    "Compare transformer and state space model architectures for sequence modeling.",
    "What is the current state of AI safety research and what are the open problems?",
    "How do retrieval-augmented generation systems work and what are their limitations?",
    "What are the key challenges in building reliable multi-agent AI systems?",
]


def run_experiment():
    Path("results").mkdir(exist_ok=True)
    results = {
        "task_class": TASK_CLASS,
        "baseline": [],
        "stem_agent": [],
        "growth_report": None
    }

    # ── Phase 1: Baseline ────────────────────────────────────────────────────
    print("\n" + "="*60)
    print("  PHASE 1: Baseline (generic agent)")
    print("="*60)
    baseline_scores = []

    for q in TEST_QUERIES:
        print(f"\nQuery: {q[:70]}...")
        response = run_baseline(q)
        eval_result = score_response(q, response)
        baseline_scores.append(eval_result.score)
        results["baseline"].append({
            "query": q,
            "score": eval_result.score,
            "breakdown": eval_result.breakdown,
            "response_preview": response[:200] + "..."
        })
        print(f"  Score: {eval_result.score:.3f}")

    baseline_mean = sum(baseline_scores) / len(baseline_scores)
    print(f"\nBaseline mean score: {baseline_mean:.3f}")

    # ── Phase 2: Grow the stem agent ─────────────────────────────────────────
    print("\n" + "="*60)
    print("  PHASE 2: Growing stem agent")
    print("="*60)

    agent = StemAgent(TASK_CLASS)
    agent.grow()
    results["growth_report"] = agent.report()

    # ── Phase 3: Evaluate specialized agent ─────────────────────────────────
    print("\n" + "="*60)
    print("  PHASE 3: Evaluating specialized agent")
    print("="*60)
    stem_scores = []

    for q in TEST_QUERIES:
        print(f"\nQuery: {q[:70]}...")
        response = agent.execute(q)
        eval_result = score_response(q, response)
        stem_scores.append(eval_result.score)
        results["stem_agent"].append({
            "query": q,
            "score": eval_result.score,
            "breakdown": eval_result.breakdown,
            "response_preview": response[:200] + "..."
        })
        print(f"  Score: {eval_result.score:.3f}")

    stem_mean = sum(stem_scores) / len(stem_scores)
    improvement = ((stem_mean - baseline_mean) / baseline_mean) * 100
    results["summary"] = {
        "baseline_mean": round(baseline_mean, 4),
        "stem_agent_mean": round(stem_mean, 4),
        "improvement_pct": round(improvement, 2),
        "iterations_to_convergence": len(agent.history),
        "converged": agent.spec.converged if agent.spec else False
    }

    # ── Save results ─────────────────────────────────────────────────────────
    with open("results/experiment_results.json", "w") as f:
        json.dump(results, f, indent=2)

    # ── Print comparison table ───────────────────────────────────────────────
    table = build_comparison_table(results, baseline_scores, stem_scores)
    print(table)
    with open("results/comparison_table.txt", "w") as f:
        f.write(table)

    print("\nResults saved to results/")
    return results


def build_comparison_table(results: dict, baseline_scores: list, stem_scores: list) -> str:
    lines = []
    lines.append("\n" + "="*70)
    lines.append("  BEFORE / AFTER COMPARISON")
    lines.append("="*70)
    lines.append(f"  Task class: {results['task_class']}")
    lines.append("-"*70)
    lines.append(f"  {'Query':<50} {'Baseline':>8} {'StemAgent':>10} {'Delta':>7}")
    lines.append("-"*70)

    for i, (q, bs, ss) in enumerate(zip(
        [r["query"] for r in results["baseline"]],
        baseline_scores,
        stem_scores
    )):
        delta = ss - bs
        delta_str = f"{'+' if delta >= 0 else ''}{delta:.3f}"
        lines.append(f"  {q[:48]:<50} {bs:>8.3f} {ss:>10.3f} {delta_str:>7}")

    summary = results["summary"]
    lines.append("-"*70)
    lines.append(f"  {'MEAN':<50} {summary['baseline_mean']:>8.3f} "
                 f"{summary['stem_agent_mean']:>10.3f} "
                 f"  {'+' if summary['improvement_pct'] >= 0 else ''}"
                 f"{summary['improvement_pct']:.1f}%")
    lines.append("="*70)
    lines.append(f"  Iterations to convergence: {summary['iterations_to_convergence']}")
    lines.append(f"  Converged: {summary['converged']}")
    lines.append("="*70)
    return "\n".join(lines)


if __name__ == "__main__":
    run_experiment()
