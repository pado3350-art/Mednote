"""Output template loaded from YAML (see templates/medical.yaml)."""
from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class SectionDef(BaseModel):
    key: str
    label: str


class LegendItem(BaseModel):
    tag: str  # emphasis | key | minor | verify
    word: str  # coloured label, e.g. "빨강"
    meaning: str


class FormatOptions(BaseModel):
    preserve_original_images: bool = True
    tables_for_comparisons: bool = True
    include_source_references: bool = True
    numbered_headings: bool = True
    font_korean: str = "맑은 고딕"
    font_size_pt: float = 10.5
    layout: str = "plain"  # "plain" | "mom"
    page_break_per_topic: bool = False
    cover_style: str = "banner"  # "banner" (big colour title banner) | "box" (double-line title box, bordered comment box)
    heading_style: str = "banner"  # per-page header: "banner" (teal chapter banner) | "plain" (bold heading) | "marker" (yellow highlight)
    slide_table: bool = False  # slide input: one two-column row per slide (slide text | lecturer explanation)
    star_style: str = "star"  # sub-headings: "star" (★ title) | "band" (light-blue band)
    exam_section: bool = True  # build a standalone 기출(PAD) section (mom.yaml: false)
    roman_headings: bool = False
    heading_system: str = "plain"  # "plain": "1. 장" / "§ 1. 소절" | "mom": "Ⅰ. 장"(노란 표시) / "[1] 소절"(초록 표시), like the human MOM (L27)
    page_break: str = "topic"  # "topic" (every § on a new page) | "chapter" (new page per chapter) | "flow" (only after front pages)
    basics_box: bool = True  # draw the 기본정석 box when a topic has `basics`
    basics_label: str = "기본정석"  # label on that box (the explanatory / mixed templates use "핵심 답")
    basics_style: str = "box"  # "box" (red-ruled box, numbered lines) | "band" (one light line: 핵심 답 + text) | "inline" ("[1] 제목 : 핵심 한 줄", L29)
    checks_where: str = "topic"  # 개념 Check boxes: "topic" (under each §) | "chapter" (one box at the end of the chapter) | "off"
    chapter_page_break: bool = False  # page_break: flow only - every chapter starts on a new page
    mixed: bool = False  # mixed style (L10): every body § has style explain|list, checked by app/write/mixed.py
    topic_tips: bool = True  # draw the yellow 공부 팁 line when a topic has `tip`
    pad_tags: bool = False  # print a small [PAD 2021 Q1] / [Only PAD …] tag after statements that cite PAD units
    toc_level: str = "section"  # "section" (every §) | "chapter" (chapter titles only)
    minutes_per_page: float = 0.0  # page budget: lecture minutes per page (0 = no PAGE_BUDGET check)
    legend: list[LegendItem] = Field(default_factory=list)


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
