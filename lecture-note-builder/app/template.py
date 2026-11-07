"""Output template loaded from YAML (see templates/medical.yaml)."""
from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class SectionDef(BaseModel):
    key: str
    label: str


class FormatOptions(BaseModel):
    preserve_original_images: bool = True
    tables_for_comparisons: bool = True
    include_source_references: bool = True
    numbered_headings: bool = True
    font_korean: str = "맑은 고딕"
    font_size_pt: float = 10.5


class QualityOptions(BaseModel):
    preserve_all_key_concepts: bool = True
    flag_uncertain_facts: bool = True
    require_source_traceability: bool = True
    min_alignment_confidence: float = 0.15


class Template(BaseModel):
    template_name: str
    language: str = "ko"
    detail_level: str = "comprehensive"
    sections: list[SectionDef]
    format: FormatOptions = Field(default_factory=FormatOptions)
    quality: QualityOptions = Field(default_factory=QualityOptions)

    @property
    def keys(self) -> list[str]:
        return [s.key for s in self.sections]

    def label(self, key: str) -> str:
        return next((s.label for s in self.sections if s.key == key), key)


def load_template(path: str | Path) -> Template:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return Template.model_validate(raw)
