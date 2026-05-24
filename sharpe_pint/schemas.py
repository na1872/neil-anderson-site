from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class Source(BaseModel):
    title: str = Field(default="", description="Source title or page name.")
    publisher: str = Field(default="", description="Publisher / organisation name.")
    url: str = Field(default="", description="Source URL.")
    published_date: str = Field(default="", description="Published date if known.")
    note: str = Field(default="", description="Why this source supports the section.")


class ContentBlock(BaseModel):
    type: str = Field(description="One of: heading, paragraph, bullets, quote, code.")
    text: str = Field(default="", description="Text for heading, paragraph, quote, or code blocks.")
    items: List[str] = Field(default_factory=list, description="Bullet items for bullets blocks.")


class SectionDraft(BaseModel):
    section_id: str = Field(description="Stable section id, e.g. daily_news or markets.")
    title: str = Field(description="Human-readable section title.")
    content: List[ContentBlock] = Field(description="Full section draft as structured content blocks.")
    key_points: List[str] = Field(default_factory=list, description="Main points in this section.")
    ideas_covered: List[str] = Field(default_factory=list, description="Concepts/topics covered, used to avoid repetition later.")
    sources: List[Source] = Field(default_factory=list, description="Sources used in this section.")
    caveats: List[str] = Field(default_factory=list, description="Uncertainties, weak data, or caveats.")


class BriefingSection(BaseModel):
    id: str = Field(description="Stable section id.")
    title: str = Field(description="Section title.")
    content: List[ContentBlock] = Field(description="Final section content as structured content blocks.")
    sources: List[Source] = Field(default_factory=list, description="Sources used in the section.")


class BriefingMetadata(BaseModel):
    generated_at: str = Field(description="ISO timestamp of generation.")
    section_model: str = Field(description="Model used for section drafts.")
    editor_model: str = Field(description="Model used for final editing.")
    source_count: int = Field(description="Total number of source entries across the briefing.")


class FinalBriefing(BaseModel):
    title: str = Field(default="The Sharpe Pint")
    date: str = Field(description="Briefing date, YYYY-MM-DD.")
    opening_mood: List[ContentBlock] = Field(description="Opening mood as structured content blocks.")
    sections: List[BriefingSection] = Field(description="Final ordered sections.")
    stuff_worth_remembering: List[str] = Field(description="Five short bullets to remember today.")
    metadata: Optional[BriefingMetadata] = None
