"""
StemAgent: A self-specializing agent that grows into a task-specific agent
from a minimal seed given only a task class description.

Lifecycle:
  SEED → OBSERVE → ARCHITECT → VALIDATE → ITERATE → EXECUTE

Author: Parth Patwardhan
"""

import json
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Optional
from openai import OpenAI

client = OpenAI()  # reads OPENAI_API_KEY from environment
BASE_MODEL = "gpt-4o"


@dataclass
class AgentSpec:
    task_class: str = ""
    role_description: str = ""
    system_prompt: str = ""
    tools: list[str] = field(default_factory=list)
    decomposition_strategy: str = ""
    quality_threshold: float = 0.70
    iteration: int = 0
    converged: bool = False


@dataclass
class EvalResult:
    query: str
    response: str
    score: float
    breakdown: dict


def complete(system: str, user: str, max_tokens: int = 1500) -> str:
    response = client.chat.completions.create(
        model=BASE_MODEL,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]
    )
    return response.choices[0].message.content.strip()


def parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    return json.loads(text)


def observe(task_class: str) -> dict:
    print(f"\n[OBSERVE] Studying '{task_class}'...")
    user = f"""A new agent is being bootstrapped for: "{task_class}".
Analyze how this task class is typically approached. Return JSON with keys:
{{"task_description":"...","typical_workflow":[],"key_skills":[],"useful_tools":[],
"common_failure_modes":[],"quality_criteria":[],"decomposition_strategy":"..."}}
Return ONLY JSON."""
    knowledge = parse_json(complete("You are an expert in AI agent design.", user, 1500))
    print(f"  → {len(knowledge['useful_tools'])} tools, {len(knowledge['typical_workflow'])} steps")
    return knowledge


def architect(task_class: str, knowledge: dict, previous_spec=None, eval_feedback=None):
    iter_label = f"iteration {previous_spec.iteration+1}" if previous_spec else "initial"
    print(f"\n[ARCHITECT] Designing spec ({iter_label})...")
    feedback_section = ""
    if previous_spec and eval_feedback:
        feedback_section = f"\nPrevious spec failed:\n{eval_feedback}\nImprove on these points.\n"
    user = f"""Design a specialized agent for: "{task_class}"
Knowledge: {json.dumps(knowledge, indent=2)}
{feedback_section}
Return JSON: {{"role_description":"...","system_prompt":"300-500 word specific prompt",
"tools":["web_search","document_retrieval","citation_checker","summarizer","fact_verifier",
"query_decomposer","source_ranker"],"decomposition_strategy":"...","quality_threshold":0.75}}
Return ONLY JSON."""
    spec_data = parse_json(complete("You are an expert AI agent architect.", user, 2000))
    iteration = (previous_spec.iteration + 1) if previous_spec else 0
    spec = AgentSpec(
        task_class=task_class,
        role_description=spec_data["role_description"],
        system_prompt=spec_data["system_prompt"],
        tools=spec_data["tools"],
        decomposition_strategy=spec_data["decomposition_strategy"],
        quality_threshold=spec_data.get("quality_threshold", 0.75),
        iteration=iteration,
        converged=False
    )
    print(f"  → {len(spec.tools)} tools | threshold={spec.quality_threshold}")
    print(f"  → Role: {spec.role_description}")
    return spec


EVAL_QUERIES = {
    "Deep Research": [
        "What are the main technical approaches to reducing hallucination in large language models?",
        "Compare transformer and state space model architectures for sequence modeling.",
        "What is the current state of AI safety research and what are the open problems?",
    ]
}

EVAL_RUBRIC = """Rate 0.0-1.0: coverage, depth, structure, accuracy, sourcing, overall.
Return JSON: {"coverage":0.x,"depth":0.x,"structure":0.x,"accuracy":0.x,"sourcing":0.x,"overall":0.x,"failure_notes":"..."}"""


def run_agent(spec: AgentSpec, query: str) -> str:
    tool_ctx = f"\n\nAvailable tools: {', '.join(spec.tools)}" if spec.tools else ""
    return complete(spec.system_prompt + tool_ctx, query, 2000)


def score_response(query: str, response: str) -> EvalResult:
    text = complete(
        "You are an expert evaluator of research quality.",
        f"Query: {query}\n\nResponse:\n{response}\n\n{EVAL_RUBRIC}", 500
    )
    scores = parse_json(text)
    return EvalResult(query=query, response=response, score=scores["overall"], breakdown=scores)


def validate(spec: AgentSpec, task_class: str) -> tuple[float, str]:
    print(f"\n[VALIDATE] Evaluating iteration {spec.iteration}...")
    queries = EVAL_QUERIES.get(task_class, EVAL_QUERIES["Deep Research"])
    results, failure_notes = [], []
    for q in queries:
        print(f"  → {q[:60]}...")
        result = score_response(q, run_agent(spec, q))
        results.append(result)
        print(f"     Score: {result.score:.2f} | coverage={result.breakdown.get('coverage',0):.2f} | depth={result.breakdown.get('depth',0):.2f} | sourcing={result.breakdown.get('sourcing',0):.2f}")
        if result.breakdown.get("failure_notes"):
            failure_notes.append(f"Q: {q[:50]}... → {result.breakdown['failure_notes']}")
    mean_score = sum(r.score for r in results) / len(results)
    print(f"  → Mean: {mean_score:.3f} (threshold: {spec.quality_threshold})")
    return mean_score, "\n".join(failure_notes) or "No major failures."


MAX_ITERATIONS = 3


class StemAgent:
    def __init__(self, task_class: str):
        self.task_class = task_class
        self.spec: Optional[AgentSpec] = None
        self.knowledge: Optional[dict] = None
        self.history: list[dict] = []

    def grow(self) -> AgentSpec:
        print(f"\n{'='*60}\n  StemAgent growing for: '{self.task_class}'\n{'='*60}")
        self.knowledge = observe(self.task_class)
        self.spec = architect(self.task_class, self.knowledge)
        for _ in range(MAX_ITERATIONS):
            score, feedback = validate(self.spec, self.task_class)
            self.history.append({
                "iteration": self.spec.iteration, "score": score, "feedback": feedback,
                "spec_hash": hashlib.md5(self.spec.system_prompt.encode()).hexdigest()[:8]
            })
            if score >= self.spec.quality_threshold or self.spec.iteration >= MAX_ITERATIONS:
                self.spec.converged = True
                print(f"\n[CONVERGED] Score {score:.3f} at iteration {self.spec.iteration}")
                break
            print(f"\n[ITERATE] Score {score:.3f} below threshold — rebuilding...")
            self.spec = architect(self.task_class, self.knowledge,
                                  previous_spec=self.spec, eval_feedback=feedback)
        return self.spec

    def execute(self, query: str) -> str:
        if not self.spec:
            raise RuntimeError("Call grow() first")
        return run_agent(self.spec, query)

    def report(self) -> dict:
        return {
            "task_class": self.task_class,
            "final_spec": asdict(self.spec) if self.spec else None,
            "knowledge": self.knowledge,
            "iterations": self.history,
            "converged": self.spec.converged if self.spec else False
        }
