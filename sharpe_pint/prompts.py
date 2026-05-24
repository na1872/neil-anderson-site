from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class SectionSpec:
    section_id: str
    title: str
    task: str
    uses_previous_key: str | None = None
    use_search: bool = True


SECTION_SPECS: List[SectionSpec] = [
    SectionSpec(
        section_id="daily_news",
        title="Daily Finance / Business News Briefing",
        task="""
Your only job is to research and write Section 1: DAILY FINANCE / BUSINESS NEWS BRIEFING.

Find 5–7 genuinely important finance/business stories from the last 24 hours or the most recent trading day. The stories should be useful to someone in the City who cares about finance, asset management, investment banking, quant, AI/LLMs, markets, companies and interviews.

For each story include:
- a short clear headline
- what happened
- why it matters
- the City angle
- what someone could say about it at work or in an interview

Make the section decently long, useful and properly researched. Avoid a headline dump. If a story is small, leave it out.
""",
    ),
    SectionSpec(
        section_id="markets",
        title="Markets Briefing: What Moved and Why",
        task="""
Your only job is to research and write Section 2: MARKETS BRIEFING: WHAT MOVED AND WHY.

Explain the most recent trading session and overnight market mood. Cover equities, rates, FX, commodities, crypto and volatility/risk sentiment where relevant.

Do not just list numbers. Explain:
- what moved
- why it moved
- why it matters
- what the cross-asset read is
- what markets are really saying underneath the surface

Include specific moves/levels where useful and source them. Write like a proper markets chat, not a table of index moves.
""",
    ),
    SectionSpec(
        section_id="financial_idea",
        title="Financial Idea of the Day",
        task="""
Your only job is to write Section 3: FINANCIAL IDEA OF THE DAY.

Pick one genuinely useful finance or investing concept the reader should understand better. Choose the idea yourself based on usefulness for asset management, investing, markets, company analysis, interviews and commercial awareness.

Include:
- concept
- plain-English explanation
- simple example, with numbers if useful
- why it matters in asset management / finance
- common beginner mistake
- how it links to interviews
- what someone could say about it

Make it properly explained, slightly fun and practical. No textbook tone.
""",
        uses_previous_key="financial_ideas",
        use_search=True,
    ),
    SectionSpec(
        section_id="quant_ai_idea",
        title="Quant / AI Finance Idea of the Day",
        task="""
Your only job is to write Section 4: QUANT / AI FINANCE IDEA OF THE DAY.

Pick one useful quant, machine learning, AI or LLM idea relevant to finance. It must connect to real finance use cases, not generic AI hype. Research carefully and include at least one relevant paper, documentation page, serious blog, GitHub repo or credible source.

Include:
- idea
- simple explanation
- finance example
- mini technical example in short pseudocode or Python-style code
- paper/source angle
- interview/conversation angle
- risk/limitation

Keep it readable. The reader should feel sharper, not like they have been mugged by a machine learning textbook.
""",
        uses_previous_key="quant_ai_ideas",
        use_search=True,
    ),
    SectionSpec(
        section_id="article_or_paper",
        title="One Article or Paper Worth Reading",
        task="""
Your only job is to write Section 5: ONE ARTICLE OR PAPER WORTH READING.

Research recent articles, papers, reports, speeches or serious blogs. Pick one genuinely worthwhile item. Do not give a reading list.

Include:
- title/source/link
- why this one
- detailed summary
- key takeaways
- one or two short quotes if available and short enough
- what to skim
- how it connects to the reader
- what the reader could say about it
- your take

This should be one of the most valuable sections. Make it feel like a guided read from someone who knows why the piece matters.
""",
        use_search=True,
    ),
    SectionSpec(
        section_id="people_psychology",
        title="People / Business Psychology Idea",
        task="""
Your only job is to write Section 6: PEOPLE / BUSINESS PSYCHOLOGY IDEA.

Pick one idea about people, incentives, clients, bosses, organisations, sales, confidence, negotiation, office politics or decision-making. It should be useful for finance/business/work conversations.

Include:
- concept
- plain-English explanation
- finance/business example
- how the reader can use it
- one line to remember

Make it observational, useful and slightly fun. No self-help waffle.
""",
        uses_previous_key="people_psychology_ideas",
        use_search=True,
    ),
]


def build_section_prompt(
    *,
    master_style: str,
    spec: SectionSpec,
    today: str,
    previous_ideas: Dict[str, List[str]],
    target_firms: str = "",
) -> str:
    previous_block = ""
    if spec.uses_previous_key:
        used = previous_ideas.get(spec.uses_previous_key, [])
        previous_block = (
            f"\nPrevious ideas already covered for this section:\n{json.dumps(used, indent=2)}\n"
            "Do not repeat these unless you are deliberately building on them from a new angle.\n"
        )

    target_firms_block = f"\nTarget firms / recurring interests to keep in mind: {target_firms}\n" if target_firms else ""

    return f"""
{master_style}

Today’s date: {today}
{target_firms_block}
{previous_block}
You are writing exactly one section of The Sharpe Pint.

Section id: {spec.section_id}
Section title: {spec.title}

{spec.task}

Return JSON only using the requested schema. Put the full prose for this section in the content array as simple blocks:
- heading: use text
- paragraph: use text
- bullets: use items
- quote: use text
- code: use text

Use plain text inside each block. Include source URLs in the sources array. Include concepts/topics in ideas_covered so they can be remembered and not repeated later.
""".strip()


def build_final_editor_prompt(
    *,
    master_style: str,
    today: str,
    section_drafts_json: str,
) -> str:
    return f"""
{master_style}

Today’s date: {today}

You are the final editor of The Sharpe Pint.

You will receive six drafted sections:
1. Daily finance / business news
2. Markets briefing
3. Financial idea of the day
4. Quant / AI finance idea of the day
5. One article or paper worth reading
6. People / business psychology idea

Your job:
- combine them into one coherent edition
- write a short opening mood section
- preserve the substance and sources
- improve flow and tone
- remove repetition
- make the writing sound like The Sharpe Pint
- keep UK English
- keep it casual, sharp, useful and slightly fun
- keep a little London/City humour where it fits naturally
- avoid corporate waffle, LinkedIn cringe and robotic phrasing
- do not invent facts
- do not add unsupported claims
- keep source links attached to relevant claims
- return valid JSON only using the requested schema

The final JSON should include:
- title
- date
- opening_mood as content blocks
- sections in this exact order
- stuff_worth_remembering with exactly 5 bullets

Use the same content block structure as the drafts. Use plain text inside each block.

Here are the drafted sections as JSON:

{section_drafts_json}
""".strip()
