from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.enums import TA_JUSTIFY

def build_writeup(output_path):
    doc = SimpleDocTemplate(output_path, pagesize=A4,
        leftMargin=2.2*cm, rightMargin=2.2*cm, topMargin=2.0*cm, bottomMargin=2.0*cm)
    styles = getSampleStyleSheet()

    title_s  = ParagraphStyle("T", parent=styles["Normal"], fontSize=16, fontName="Helvetica-Bold", spaceAfter=4, leading=20)
    sub_s    = ParagraphStyle("S", parent=styles["Normal"], fontSize=10, fontName="Helvetica", spaceAfter=12, textColor=colors.HexColor("#555555"))
    h1       = ParagraphStyle("h1", parent=styles["Normal"], fontSize=12, fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=4, leading=16)
    h2       = ParagraphStyle("h2", parent=styles["Normal"], fontSize=10, fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=3, leading=14)
    body     = ParagraphStyle("b", parent=styles["Normal"], fontSize=9.5, fontName="Helvetica", leading=14, spaceAfter=6, alignment=TA_JUSTIFY)
    small    = ParagraphStyle("sm", parent=styles["Normal"], fontSize=8.5, fontName="Helvetica", leading=12, textColor=colors.HexColor("#444444"))
    mono     = ParagraphStyle("mo", parent=styles["Normal"], fontSize=8.5, fontName="Courier", leading=12, spaceAfter=4, leftIndent=10)

    def hr(): return HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CCCCCC"), spaceAfter=4, spaceBefore=4)
    def sp(n=6): return Spacer(1, n)

    story = []

    story.append(Paragraph("StemAgent: A Self-Specializing AI Agent", title_s))
    story.append(Paragraph("Parth Patwardhan &nbsp;·&nbsp; JetBrains AI Engineering Intern — Task #1 Write-up", sub_s))
    story.append(hr())

    # 1. Idea
    story.append(Paragraph("1. The Idea and Scope Choice", h1))
    story.append(Paragraph(
        "The prompt asked for an agent that becomes specific through its own process. "
        "I chose <b>Deep Research</b> as the task domain for three reasons: it has clear, "
        "independently measurable quality dimensions (coverage, depth, sourcing, structure, accuracy); "
        "it is a domain where the gap between generic and specialized agents should be visible; "
        "and its failure modes are concrete — shallow summaries, missing citations, no query decomposition. "
        "For a different class such as Security or QA, you would start a new StemAgent with that label. "
        "Nothing task-specific is hard-coded.", body))

    # 2. Architecture
    story.append(Paragraph("2. Architecture", h1))
    story.append(Paragraph("Five lifecycle stages, no task knowledge pre-loaded:", h2))
    for stage, desc in [
        ("OBSERVE", "Ask a model: how is this task class typically approached? Returns structured knowledge — workflow, tools, failure modes, quality criteria."),
        ("ARCHITECT", "Synthesize a concrete AgentSpec: full system prompt (300-500 words), tool list, decomposition strategy. On iteration 1+, failure feedback from the previous eval is passed in so the architect can patch specifically."),
        ("VALIDATE", "Run 3 eval queries. Score each response 0-1 on 5 criteria using a judge model. Return mean score and failure notes."),
        ("ITERATE", "If mean score < threshold (0.75), re-architect with feedback. Max 3 cycles. Track spec hash to detect if changes are meaningful."),
        ("EXECUTE", "Converged agent handles real queries using its self-designed system prompt."),
    ]:
        story.append(Paragraph(f"<b>{stage}</b> — {desc}", body))

    story.append(Paragraph("The AgentSpec dataclass carries: role description, full system prompt, tool list, "
        "decomposition strategy, quality threshold, iteration count, convergence flag. "
        "Spec hash (MD5 of system prompt) lets us detect if the architect is making real changes or spinning.", body))

    # 3. Results
    story.append(Paragraph("3. Results — Before / After", h1))

    table_data = [
        ["Query (truncated)", "Baseline", "StemAgent", "Delta"],
        ["Hallucination reduction approaches", "0.800", "0.700", "-0.100"],
        ["Transformer vs SSM architectures",   "0.700", "0.780", "+0.080"],
        ["AI safety research open problems",   "0.760", "0.660", "-0.100"],
        ["How RAG works and limitations",      "0.750", "0.840", "+0.090"],
        ["Challenges in multi-agent systems",  "0.800", "0.550", "-0.250"],
        ["MEAN",                               "0.762", "0.706", "-7.3%"],
    ]
    ts = TableStyle([
        ("BACKGROUND",   (0,0), (-1,0), colors.HexColor("#222222")),
        ("TEXTCOLOR",    (0,0), (-1,0), colors.white),
        ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,-1), 8.5),
        ("FONTNAME",     (0,-1),(-1,-1), "Helvetica-Bold"),
        ("BACKGROUND",   (0,-1),(-1,-1), colors.HexColor("#EEEEEE")),
        ("GRID",         (0,0), (-1,-1), 0.4, colors.HexColor("#CCCCCC")),
        ("ALIGN",        (1,0), (-1,-1), "CENTER"),
        ("ROWBACKGROUNDS",(0,1),(-1,-2), [colors.white, colors.HexColor("#F8F8F8")]),
        ("TOPPADDING",   (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0), (-1,-1), 4),
    ])
    t = Table(table_data, colWidths=[9.5*cm, 2.2*cm, 2.5*cm, 2.2*cm])
    t.setStyle(ts)
    story.append(t)
    story.append(sp(8))

    story.append(Paragraph(
        "<b>Convergence:</b> The stem agent converged in 2 iterations. "
        "Iteration 0 scored 0.733 (below 0.75 threshold). The architect identified sourcing as the "
        "weak dimension (0.30 on the first query) and rewrote the system prompt to explicitly require "
        "citations and source attribution. Iteration 1 scored 0.767, triggering convergence.", body))
    story.append(Paragraph(
        "<b>Mixed outcome on test queries:</b> The specialized agent outperformed baseline on 2 of 5 "
        "queries and underperformed on 3. The largest gap was on multi-agent challenges (-0.250), "
        "where the specialized system prompt's emphasis on structured synthesis and citation "
        "apparently conflicted with the more conversational nature of that query.", body))

    # 4. What failed
    story.append(Paragraph("4. What Failed and What Surprised Me", h1))
    story.append(Paragraph(
        "<b>The mixed results are the most important finding.</b> I expected cleaner improvement. "
        "What actually happened is more interesting: the specialized agent got better at the things "
        "it was explicitly optimized for (sourcing, structure) but became worse at queries that "
        "required breadth over depth. The system prompt it designed was genuinely more opinionated "
        "than the generic one — which is a win — but opinionated in a direction that hurt "
        "on some query types.", body))
    story.append(Paragraph(
        "<b>The judge model shares weights with the agent.</b> Using the same model family as both "
        "agent and judge introduces self-assessment bias. The judge rewards the patterns the architect "
        "was prompted to produce. This inflates convergence confidence. A better setup would use "
        "human raters or a different model family as judge.", body))
    story.append(Paragraph(
        "<b>Tool list is declarative, not executable.</b> The agent decides it needs "
        "'web_search' and 'citation_checker' but these don't actually run — tool awareness "
        "is injected into the system prompt as text. Real specialization would require acquiring, "
        "testing, and committing to actual tool implementations.", body))
    story.append(Paragraph(
        "<b>3-query eval is too small.</b> Score variance across the 5 test queries is high. "
        "The convergence decision is noisy at this eval set size.", body))

    # 5. With more time
    story.append(Paragraph("5. What I'd Do With More Time", h1))
    for title, desc in [
        ("Best-spec tracking", "Track the highest-scoring spec across iterations and revert if the new one regresses. Currently we always use the latest spec even if it's worse than the previous."),
        ("Real tool acquisition", "A tool registry with execution harnesses. The agent tests each tool on sample inputs and commits only to tools that measurably help."),
        ("Better evaluation", "RAGAS or FActScore against a gold corpus. Or a different model family as judge to break the self-assessment loop."),
        ("Cross-domain validation", "Grow agents for Security and QA and verify the specialization diverges meaningfully — different prompts, tools, strategies."),
        ("Safeguards mid-transformation", "Constitutional check at each iteration: does the new spec stay within the task class? Does it increase hallucination risk? This is the 'pull back' mechanism from the prompt."),
    ]:
        story.append(Paragraph(f"<b>{title}:</b> {desc}", body))

    # Task 2
    story.append(hr())
    story.append(sp(4))
    story.append(Paragraph("Task #2: What Stops Us From Building Fully Autonomous Agents?", h1))
    story.append(Paragraph(
        "The claw-agent framing is precise — these agents are capable within a well-scoped environment "
        "but require a human in the loop for complex tasks. Here are the structural reasons:", body))

    for i, (title, desc) in enumerate([
        ("Compounding error in long-horizon tasks",
         "An agent making 50 sequential decisions at 95% per-step reliability succeeds end-to-end ~7.7% of the time (0.95^50). "
         "Agents have no reliable mechanism for detecting mid-task drift. Humans do this constantly through metacognition. "
         "Until agents can self-assess state fidelity across long horizons, checkpoints are required."),
        ("Grounding and world model gaps",
         "LLMs learn statistical patterns over text, not causal models. They can't reliably distinguish "
         "'what would happen if I do X' from 'what text typically follows this.' For a software engineer "
         "this means plausible-looking code that silently violates invariants the model has never seen violated."),
        ("Tool use reliability",
         "Agents treat tool calls as atomic. APIs fail, return partial data, have undocumented side effects and implicit state. "
         "An agent that can't reason about partial success and its downstream consequences is brittle in real environments. "
         "Current retry-on-error is not reasoning about failure — it's hoping the problem goes away."),
        ("Context window as poor working memory",
         "Long-horizon tasks need coherent state across many steps. Context windows are finite, treat all tokens equally, "
         "and have no structured forgetting. Human memory systems (episodic, semantic, procedural) are specialized for "
         "different access patterns. Agent 'memory' is a flat list with no retrieval structure."),
        ("Evaluation and trust calibration",
         "We can't trust an agent we can't evaluate on the full distribution of tasks it will encounter. "
         "For complex software engineering, 'correct' is hard to define — an implementation can work locally "
         "and still be insecure, unmaintainable, or wrong in ways that surface only at runtime. "
         "Until evaluation frameworks catch this class of failure, a human in the loop is the safety net we can't remove."),
    ], 1):
        story.append(Paragraph(f"<b>{i}. {title}</b>", h2))
        story.append(Paragraph(desc, body))

    story.append(Paragraph(
        "The bottleneck is not compute or model size. It is grounding, long-horizon coherence, "
        "and the absence of mechanisms for detecting and recovering from errors mid-execution — "
        "which is exactly what the StemAgent experiment surfaced in miniature.", body))

    doc.build(story)
    print(f"Write-up saved: {output_path}")

if __name__ == "__main__":
    build_writeup("/home/claude/StemAgent_Writeup_Parth_Patwardhan.pdf")
