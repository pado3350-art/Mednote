"""lecture-note-builder. 세 섹션: app.write(① 스크립트 → 정리글) · app.design(② 정리글 + 이미지 → 문서) · app.pad(③ PAD).

호환: 섹션으로 나누기 전의 옛 경로(`app.exam`, `app.mom_compare`, `python -m app.cli` 아님)도 같은 모듈로 연결된다.
`import app.exam` == `import app.pad.exam` (같은 객체이므로 monkeypatch도 그대로 동작). 새 코드는 섹션 경로를 쓴다.
"""
import importlib
import importlib.abc
import importlib.util
import sys

_MOVED = {
    **dict.fromkeys("transcript material align_content outline storyline prepare offline_organizer generate_notes mixed "
                    "validate_notes feedback docx_diff".split(), "write"),
    **dict.fromkeys("extract_slides figures diagrams export_mom export_docx pdf_render mom_compare".split(), "design"),
    **dict.fromkeys("exam pad_match".split(), "pad"),
}


class _AliasLoader(importlib.abc.Loader):
    def __init__(self, target: str):
        self.target = target

    def create_module(self, spec):
        return importlib.import_module(self.target)

    def exec_module(self, module):  # already executed under its real name
        pass


class _OldPathFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path=None, target=None):
        parts = name.split(".")
        if len(parts) == 2 and parts[0] == "app" and parts[1] in _MOVED:
            real = f"app.{_MOVED[parts[1]]}.{parts[1]}"
            return importlib.util.spec_from_loader(name, _AliasLoader(real))
        return None


if not any(isinstance(f, _OldPathFinder) for f in sys.meta_path):
    sys.meta_path.append(_OldPathFinder())
