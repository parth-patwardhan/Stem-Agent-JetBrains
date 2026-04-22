"""
demo.py — Quick demo: grow a stem agent and run one query.

Usage:
    python demo.py
    python demo.py "Security"   # grow for a different task class
"""

import sys
from core.stem_agent import StemAgent

task_class = sys.argv[1] if len(sys.argv) > 1 else "Deep Research"

agent = StemAgent(task_class)
agent.grow()

print("\n" + "="*60)
print("  EXECUTING SPECIALIZED AGENT")
print("="*60)

query = input("\nEnter a query (or press Enter for default): ").strip()
if not query:
    query = "What are the main technical approaches to reducing hallucination in large language models?"

print(f"\nQuery: {query}\n")
print("-"*60)
response = agent.execute(query)
print(response)

print("\n" + "="*60)
print("  GROWTH REPORT")
print("="*60)
import json
report = agent.report()
for item in report["iterations"]:
    print(f"  Iteration {item['iteration']}: score={item['score']:.3f} | spec_hash={item['spec_hash']}")
print(f"  Converged: {report['converged']}")
