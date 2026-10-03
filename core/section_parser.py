"""Hierarchical requirements section parser (leaf section → one test-case unit).

Supports:
- Numbered outlines: ``3. CRM``, ``3.1 …``
- Word/markdown headings without numbers: ``## СИСТЕМА 1``, ``### Калькулятор``
  (DOCX extract maps Heading 2/3/4 → ``##`` / ``###`` / ``####``)

Product rules:
- A section with its own body (and/or true leaves) is a generation unit.
- Numbered / bullet work items inside a section become Steps of one case.
- Tables and fenced code stay in the section where they appear.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, Sequence


# Numbered: "3. Title", "3.1 Title" — optional markdown hashes / "Раздел"
_NUMBERED_HEADING_RE = re.compile(
    r"^\s{0,3}"
    r"(?P<md>#{1,6}\s+)?"
    r"(?:(?P<label>раздел|section)\s+)?"
    r"(?P<number>\d+(?:\.\d+)*)\s*[.)]?\s+"
    r"(?P<title>\S.*\S|\S)\s*$",
    re.IGNORECASE,
)

# Markdown / Word-style heading without required number: "## СИСТЕМА 1"
_MD_HEADING_RE = re.compile(r"^\s{0,3}(?P<hashes>#{1,6})\s+(?P<title>\S.*\S|\S)\s*$")

# Work items: "1. …", "2) …"
_NUMBERED_ITEM_RE = re.compile(
    r"^\s*(?:[-*+]\s+)?"
    r"(?P<n>\d{1,3})\s*[.)．]\s+"
    r"(?P<text>\S.*\S|\S)\s*$"
)

# Bullets used in real specs: "• text", "- text", "* text", "– text"
_BULLET_ITEM_RE = re.compile(
    r"^\s*(?:[•●○▪◦‣·]|[-*+]|&bull;|–|—)\s+(?P<text>\S.*\S|\S)\s*$"
)

_FENCE_RE = re.compile(r"^\s*```")
_TABLE_LINE_RE = re.compile(r"^\s*\|")


@dataclass(frozen=True)
class ParseOptions:
    """Tunable filters — fill when you know which parts to drop from a real doc."""

    exclude_section_ids: frozenset[str] = frozenset()
    exclude_title_substrings: tuple[str, ...] = ()
    drop_empty_leaves: bool = True
    paragraph_items_if_no_bullets: bool = True
    """If a section has no numbered/bullet items, treat prose paragraphs as steps."""


@dataclass
class SectionNode:
    number: str
    title: str
    level: int
    body_lines: list[str] = field(default_factory=list)
    children: list[SectionNode] = field(default_factory=list)
    start_line: int = 0

    @property
    def path(self) -> str:
        return f"{self.number} {self.title}".strip()

    @property
    def body(self) -> str:
        return "\n".join(self.body_lines).strip()

    @property
    def is_leaf(self) -> bool:
        return not self.children


@dataclass(frozen=True)
class WorkItem:
    index: int
    text: str


@dataclass(frozen=True)
class LeafSection:
    """One primary test-case unit ready for prompt / AI."""

    number: str
    title: str
    path: str
    body: str
    items: tuple[WorkItem, ...]
    level: int
    start_line: int

    def to_debug_dict(self) -> dict:
        return {
            "number": self.number,
            "title": self.title,
            "path": self.path,
            "level": self.level,
            "start_line": self.start_line,
            "item_count": len(self.items),
            "items": [{"index": i.index, "text": i.text} for i in self.items],
            "body_preview": self.body[:500],
            "body_chars": len(self.body),
            "has_table": "|" in self.body or "<table" in self.body.lower(),
            "has_code_fence": "```" in self.body,
        }


@dataclass(frozen=True)
class ParsedDocument:
    preamble: str
    roots: tuple[SectionNode, ...]
    leaves: tuple[LeafSection, ...]

    def to_debug_dict(self) -> dict:
        return {
            "preamble_chars": len(self.preamble),
            "preamble_preview": self.preamble[:300],
            "root_count": len(self.roots),
            "leaf_count": len(self.leaves),
            "leaves": [leaf.to_debug_dict() for leaf in self.leaves],
            "tree": [_node_debug(n) for n in self.roots],
        }


def _node_debug(node: SectionNode) -> dict:
    return {
        "number": node.number,
        "title": node.title,
        "level": node.level,
        "body_chars": len(node.body),
        "child_count": len(node.children),
        "children": [_node_debug(c) for c in node.children],
    }


def parse_section_number(number: str) -> tuple[int, ...]:
    parts = [p for p in number.strip().split(".") if p != ""]
    return tuple(int(p) for p in parts)


def heading_level(number: str) -> int:
    return len(parse_section_number(number))


def is_ancestor(parent_number: str, child_number: str) -> bool:
    parent = parse_section_number(parent_number)
    child = parse_section_number(child_number)
    return len(child) > len(parent) and child[: len(parent)] == parent


@dataclass(frozen=True)
class _DetectedHeading:
    number: str | None
    title: str
    md_level: int | None  # 1..6 from # count; None if plain numbered line


def detect_heading_line(
    line: str, *, stack: Sequence[SectionNode] | None = None
) -> _DetectedHeading | None:
    """
    Detect a section heading from either:
    - Word/markdown styles: ``## СИСТЕМА 1``, ``### Калькулятор``
    - Explicit numbering (any style): ``3. CRM``, ``3.1 Каталог``, ``## 3.2 …``
    Both may appear in the same document.
    """
    md = _MD_HEADING_RE.match(line)
    numbered = _NUMBERED_HEADING_RE.match(line)

    # ``## 3.1 Catalog`` / ``### 3. CRM`` — number wins, md depth is a hint
    if numbered and numbered.group("md"):
        return _DetectedHeading(
            number=numbered.group("number"),
            title=numbered.group("title").strip(),
            md_level=len(numbered.group("md").strip()),
        )

    # ``## СИСТЕМА 1`` — unnumbered heading; title itself may still be ``3.1 Foo``
    if md and not numbered:
        title = md.group("title").strip()
        md_level = len(md.group("hashes"))
        embedded = _NUMBERED_HEADING_RE.match(title)
        if embedded and not embedded.group("md"):
            return _DetectedHeading(
                number=embedded.group("number"),
                title=embedded.group("title").strip(),
                md_level=md_level,
            )
        return _DetectedHeading(number=None, title=title, md_level=md_level)

    # Plain Normal-text numbering: ``3. CRM``, ``3.1.1 …``, ``Раздел 3 …``
    if numbered:
        number = numbered.group("number")
        title = numbered.group("title").strip()
        has_label = numbered.group("label") is not None
        if "." in number or has_label or not stack:
            return _DetectedHeading(number=number, title=title, md_level=None)
        # Bare ``1. / 2. / 3.`` inside an open section → usually a Step, not a chapter.
        try:
            n = int(number)
        except ValueError:
            return None
        try:
            current_top = parse_section_number(stack[0].number)[0]
        except (ValueError, IndexError):
            return _DetectedHeading(number=number, title=title, md_level=None)
        if n > current_top and not _looks_like_work_item_not_section(title):
            return _DetectedHeading(number=number, title=title, md_level=None)
        return None

    return None


def _pop_stack_for_heading(
    stack: list[SectionNode],
    *,
    number: str | None,
    md_level: int | None,
) -> None:
    """
    Pop until the new heading can attach.

    Prefer numeric ancestry when it matches the open tree; otherwise fall back
    to markdown/Word heading depth so ``### 3.1 …`` still nests under
    ``## СИСТЕМА 1`` even if synthetic parent ids differ from ``3``.
    """
    if number is not None:
        snapshot = list(stack)
        while stack and not is_ancestor(stack[-1].number, number):
            stack.pop()
        if stack or md_level is None:
            return
        stack.clear()
        stack.extend(snapshot)
    if md_level is None:
        return
    while stack and stack[-1].level >= md_level:
        stack.pop()


def _looks_like_work_item_not_section(title: str) -> bool:
    lowered = title.lower()
    task_prefixes = (
        "доработ",
        "внест",
        "измен",
        "добав",
        "удал",
        "исправ",
        "реализ",
        "провер",
        "настро",
        "обнов",
        "перенес",
        "сделать",
        "add ",
        "update ",
        "fix ",
        "change ",
        "implement ",
        "remove ",
    )
    if any(lowered.startswith(p) for p in task_prefixes):
        return True
    return len(title) > 80


def extract_work_items(
    body: str, *, paragraph_fallback: bool = True
) -> tuple[WorkItem, ...]:
    """Numbered + bullet items; optional paragraph fallback for prose-only sections."""
    items: list[WorkItem] = []
    in_fence = False
    for raw in (body or "").splitlines():
        if _FENCE_RE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence or _TABLE_LINE_RE.match(raw):
            continue
        m_num = _NUMBERED_ITEM_RE.match(raw)
        if m_num:
            items.append(
                WorkItem(index=int(m_num.group("n")), text=m_num.group("text").strip())
            )
            continue
        m_bull = _BULLET_ITEM_RE.match(raw)
        if m_bull:
            items.append(
                WorkItem(index=len(items) + 1, text=m_bull.group("text").strip())
            )

    if items or not paragraph_fallback:
        return tuple(items)

    # Prose paragraphs → steps (skip tiny labels / list-only leftovers)
    para_items: list[WorkItem] = []
    for raw in (body or "").splitlines():
        line = raw.strip()
        if not line or _TABLE_LINE_RE.match(line) or _FENCE_RE.match(line):
            continue
        if len(line) < 12:
            continue
        para_items.append(WorkItem(index=len(para_items) + 1, text=line))
    return tuple(para_items)


def _should_exclude(number: str, title: str, options: ParseOptions) -> bool:
    if number in options.exclude_section_ids:
        return True
    parts = parse_section_number(number)
    for depth in range(1, len(parts)):
        ancestor = ".".join(str(x) for x in parts[:depth])
        if ancestor in options.exclude_section_ids:
            return True
    title_l = title.lower()
    for fragment in options.exclude_title_substrings:
        if fragment.lower() in title_l:
            return True
    return False


def parse_requirements_document(
    text: str,
    options: ParseOptions | None = None,
) -> ParsedDocument:
    """Parse flat extracted text into a section tree and leaf units."""
    opts = options or ParseOptions()
    lines = (text or "").replace("\r\n", "\n").split("\n")

    preamble_lines: list[str] = []
    roots: list[SectionNode] = []
    stack: list[SectionNode] = []
    in_fence = False

    for idx, line in enumerate(lines, start=1):
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            _append_body(stack, preamble_lines, line)
            continue
        if in_fence:
            _append_body(stack, preamble_lines, line)
            continue

        detected = detect_heading_line(line, stack=stack)
        if detected is None:
            _append_body(stack, preamble_lines, line)
            continue

        # Nest first (sibling index for synthetic numbers), then assign id.
        _pop_stack_for_heading(
            stack, number=detected.number, md_level=detected.md_level
        )

        if detected.number:
            number = detected.number
            level = (
                detected.md_level
                if detected.md_level is not None
                else heading_level(number)
            )
        elif stack:
            number = f"{stack[-1].number}.{len(stack[-1].children) + 1}"
            level = detected.md_level or (stack[-1].level + 1)
        else:
            number = str(len(roots) + 1)
            level = detected.md_level or 1

        node = SectionNode(
            number=number,
            title=detected.title,
            level=level,
            start_line=idx,
        )
        if stack:
            stack[-1].children.append(node)
        else:
            roots.append(node)
        stack.append(node)

    roots = _prune_excluded(roots, opts)
    leaves = tuple(
        _collect_leaves(
            roots,
            opts,
            paragraph_fallback=opts.paragraph_items_if_no_bullets,
        )
    )
    preamble = "\n".join(preamble_lines).strip()
    return ParsedDocument(preamble=preamble, roots=tuple(roots), leaves=leaves)


def _append_body(
    stack: list[SectionNode], preamble_lines: list[str], line: str
) -> None:
    if stack:
        stack[-1].body_lines.append(line)
    else:
        preamble_lines.append(line)


def _prune_excluded(nodes: Sequence[SectionNode], opts: ParseOptions) -> list[SectionNode]:
    kept: list[SectionNode] = []
    for node in nodes:
        if _should_exclude(node.number, node.title, opts):
            continue
        node.children = _prune_excluded(node.children, opts)
        kept.append(node)
    return kept


def _collect_leaves(
    nodes: Iterable[SectionNode],
    opts: ParseOptions,
    *,
    paragraph_fallback: bool,
) -> list[LeafSection]:
    leaves: list[LeafSection] = []

    def maybe_emit(node: SectionNode, ancestors: list[SectionNode]) -> None:
        path_nodes = ancestors + [node]
        path = " > ".join(n.path for n in path_nodes)
        body = node.body
        items = extract_work_items(body, paragraph_fallback=paragraph_fallback)
        if opts.drop_empty_leaves and not body.strip() and not items:
            return
        leaves.append(
            LeafSection(
                number=node.number,
                title=node.title,
                path=path,
                body=body,
                items=items,
                level=node.level,
                start_line=node.start_line,
            )
        )

    def walk(node: SectionNode, ancestors: list[SectionNode]) -> None:
        if node.children:
            maybe_emit(node, ancestors)
            for child in node.children:
                walk(child, ancestors + [node])
            return
        maybe_emit(node, ancestors)

    for root in nodes:
        walk(root, [])
    return leaves


def build_section_path(leaf: LeafSection) -> str:
    return leaf.path


# Backward-compatible name used by earlier tests / callers
def parse_heading_line(
    line: str, *, stack: Sequence[SectionNode] | None = None
) -> tuple[str, str] | None:
    detected = detect_heading_line(line, stack=stack)
    if detected is None:
        return None
    if detected.number:
        return detected.number, detected.title
    # Synthetic number not available without outline state — expose title only via None
    return None
