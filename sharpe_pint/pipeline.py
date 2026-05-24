from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from sharpe_pint.config import AppConfig
from sharpe_pint.gemini_client import GeminiJSONClient
from sharpe_pint.prompts import SECTION_SPECS, build_final_editor_prompt, build_section_prompt
from sharpe_pint.schemas import FinalBriefing, SectionDraft, BriefingMetadata


def run_pipeline(*, config: AppConfig, today: str, output_dir: Path) -> FinalBriefing:
    run_started_at = datetime.now(timezone.utc)
    issue_id = f"{today}_{datetime.now().strftime('%H-%M-%S')}"

    output_dir.mkdir(parents=True, exist_ok=True)
    drafts_dir = output_dir / "drafts" / issue_id
    drafts_dir.mkdir(parents=True, exist_ok=True)

    master_style = (config.project_root / "prompts" / "master_style.txt").read_text(encoding="utf-8")
    previous_ideas = _load_previous_ideas(config.project_root / "data" / "previous_ideas.json")

    gemini = GeminiJSONClient(api_key=config.gemini_api_key)

    drafts: list[SectionDraft] = []
    for spec in SECTION_SPECS:
        print(f"Generating section: {spec.title}")
        prompt = build_section_prompt(
            master_style=master_style,
            spec=spec,
            today=today,
            previous_ideas=previous_ideas,
            target_firms=config.target_firms,
        )
        draft = gemini.generate_json(
            model=config.section_model,
            prompt=prompt,
            schema_model=SectionDraft,
            use_search=spec.use_search,
            max_output_tokens=config.section_max_output_tokens,
            temperature=0.35,
        )
        drafts.append(draft)
        _write_json(drafts_dir / f"{spec.section_id}.json", draft.model_dump())

    drafts_json = json.dumps([d.model_dump() for d in drafts], ensure_ascii=False, indent=2)
    final_prompt = build_final_editor_prompt(
        master_style=master_style,
        today=today,
        section_drafts_json=drafts_json,
    )

    print("Generating final briefing JSON...")
    briefing = gemini.generate_json(
        model=config.editor_model,
        prompt=final_prompt,
        schema_model=FinalBriefing,
        use_search=False,
        max_output_tokens=config.editor_max_output_tokens,
        temperature=0.30,
    )

    # Add/overwrite metadata locally so it is always present and accurate.
    source_count = sum(len(section.sources) for section in briefing.sections)
    briefing.metadata = BriefingMetadata(
        generated_at=run_started_at.isoformat(),
        section_model=config.section_model,
        editor_model=config.editor_model,
        source_count=source_count,
    )

    json_path = output_dir / f"{issue_id}.json"
    latest_json_path = output_dir / "latest.json"
    site_data_dir = config.project_root / "public" / "sharpe-pint" / "data"
    site_latest_json_path = site_data_dir / "latest.json"
    site_issue_json_path = site_data_dir / f"{issue_id}.json"
    site_index_path = site_data_dir / "index.json"

    _write_json(json_path, briefing.model_dump())
    shutil.copyfile(json_path, latest_json_path)
    _write_json(site_issue_json_path, briefing.model_dump())
    shutil.copyfile(site_issue_json_path, site_latest_json_path)
    _update_site_index(
        site_index_path,
        {
            "id": issue_id,
            "file": f"{issue_id}.json",
            "title": briefing.title,
            "date": briefing.date,
            "generated_at": run_started_at.isoformat(),
            "source_count": source_count,
        },
    )

    _update_previous_ideas(config.project_root / "data" / "previous_ideas.json", previous_ideas, drafts)

    print(f"Saved: {json_path}")
    print(f"Saved: {latest_json_path}")
    print(f"Saved website data: {site_latest_json_path}")
    print(f"Saved website index: {site_index_path}")
    return briefing


def _load_previous_ideas(path: Path) -> Dict[str, List[str]]:
    if not path.exists():
        return {"financial_ideas": [], "quant_ai_ideas": [], "people_psychology_ideas": []}
    return json.loads(path.read_text(encoding="utf-8"))


def _update_previous_ideas(path: Path, previous: Dict[str, List[str]], drafts: list[SectionDraft]) -> None:
    mapping = {
        "financial_idea": "financial_ideas",
        "quant_ai_idea": "quant_ai_ideas",
        "people_psychology": "people_psychology_ideas",
    }
    for draft in drafts:
        key = mapping.get(draft.section_id)
        if not key:
            continue
        previous.setdefault(key, [])
        for idea in draft.ideas_covered:
            idea = idea.strip()
            if idea and idea not in previous[key]:
                previous[key].append(idea)
    _write_json(path, previous)


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _update_site_index(path: Path, entry: dict[str, object]) -> None:
    if path.exists():
        index = json.loads(path.read_text(encoding="utf-8"))
    else:
        index = {"latest": "", "issues": []}

    issues = [item for item in index.get("issues", []) if item.get("id") != entry["id"]]
    issues.insert(0, entry)

    _write_json(
        path,
        {
            "latest": entry["file"],
            "issues": issues,
        },
    )
