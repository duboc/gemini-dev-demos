#!/usr/bin/env python3
"""Verify that README.md matches this repository and follows mechanical style rules.

Run it from anywhere with no arguments:

    python3 check_readme.py

The script reads only files inside this repository. It never opens a network
connection and never needs Google Cloud credentials. It prints one line per
check and exits with a non-zero status if any check fails.
"""

from __future__ import annotations

import ast
import datetime
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
README_PATH = REPO / "README.md"

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Directories that are never part of the documented source tree. "repo" is the
# clone target of apps/repo-inspection.py: running that demo drops a whole
# third-party repository there, and .gitignore excludes it as /repo. Walking it
# made every environment variable of the cloned project look like an
# undocumented one.
SKIP_DIRS = {
    ".git",
    ".agents",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "repo",
}

# Extensionless filenames that are still treated as path references.
EXTENSIONLESS_PATHS = {"LICENSE", "Dockerfile", "Makefile", "CHANGELOG"}

PATH_SUFFIXES = {
    ".py", ".md", ".txt", ".toml", ".yaml", ".yml", ".sh",
    ".json", ".gif", ".png", ".jpg", ".svg", ".cfg",
}

# Proper nouns that are allowed to keep their capitals inside a sentence-case
# heading. Longest first so that multi-word names are removed before their
# single-word prefixes.
PROPER_NOUNS = [
    "Contributor License Agreement",
    "Identity-Aware Proxy",
    "Firebase Test Lab",
    "Artifact Registry",
    "Cloud Storage",
    "Google Cloud",
    "Apache License",
    "Cloud Build",
    "Cloud Run",
    "Vertex AI",
    "Dockerfile",
    "Streamlit",
    "Dataform",
    "Selenium",
    "Firebase",
    "Appium",
    "Docker",
    "GitHub",
    "Gemini",
    "Python",
    "COBOL",
    "Java",
    "Git",
]

BANNED_WORDS = [
    "simply",
    "easy",
    "easily",
    "just",
    "please note",
    "click here",
    "whitelist",
    "blacklist",
    "master/slave",
    "slave",
    "sanity check",
    "dummy",
    "crazy",
]

NON_DESCRIPTIVE_LINK_TEXT = {
    "here", "click here", "this", "this link", "link", "read more",
    "more", "see here", "this page", "documentation here",
}

PLACEHOLDER_PATTERNS = [
    "your-username",
    "your-project-id",
    "your-project",
    "your-region",
    "your-preferred-region",
    "YOUR_PROJECT_ID",
    "YOUR_REGION",
    "my-project",
    "path/to/your",
    "<your",
]
PLACEHOLDER_MARKERS = ("replace", "placeholder")
PLACEHOLDER_WINDOW = 5

EMOJI_RE = re.compile(
    "["
    "\U0001F000-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U00002190-\U000021FF"
    "\U00002B00-\U00002BFF"
    "\U0000FE0F"
    "\U00002049"
    "\U0000203C"
    "]"
)

INLINE_CODE_RE = re.compile(r"`([^`]+)`")
LINK_RE = re.compile(r"!?\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
LIST_ITEM_RE = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")

# A sentence that claims a file imports something.
IMPORT_VERB_RE = re.compile(r"\bimports?\b|\bimporting\b|\bimported\b", re.I)

# A sentence that claims something is absent from requirements.txt.
NOT_LISTED_RE = re.compile(
    r"\b(?:does not|doesn't|do not|don't|never)\s+(?:\w+\s+){0,2}"
    r"(?:list|lists|pin|pins|include|includes|contain|contains|declare|declares)\b",
    re.I,
)

# The same claim, but capturing the package it is about. NOT_LISTED_RE only
# says that a block disclaims something; this says what. Without it, a block
# that both disclaims and tells the reader to install something never has its
# disclaimer verified, because the block-wide token scan is skipped there.
NOT_LISTED_SUBJECT_RE = re.compile(
    r"\b(?:does not|doesn't|do not|don't|never)\s+(?:\w+\s+){0,2}"
    r"(?:list|lists|pin|pins|include|includes|contain|contains|declare|declares)"
    r"\s+`([^`]+)`",
    re.I,
)

# A sentence that tells the reader to install or add a package.
INSTALL_INSTRUCTION_RE = re.compile(
    r"\b(?:install|installs|installing|add|adds|adding)\s+`([^`]+)`", re.I
)

# A requirement specifier quoted in prose, such as `tqdm>=4.66.3`. Only the
# two-character operators count: a single `=` or `<` matches shell syntax and
# placeholder text that has nothing to do with requirements.txt.
REQUIREMENT_SPEC_RE = re.compile(
    r"([A-Za-z][A-Za-z0-9._-]*)\s*(==|>=|<=|~=|!=)\s*([0-9][0-9A-Za-z.*+!-]*)"
)

# Distribution name -> module name, for cases where they differ.
PACKAGE_ALIASES = {
    "gitpython": "git",
    "google_cloud_aiplatform": "google",
    "beautifulsoup4": "bs4",
    "faiss_cpu": "faiss",
    "youtube_transcript_api": "youtube_transcript_api",
}

# Google style: use present tense.
FUTURE_TENSE_RE = re.compile(r"(?<!\w)(will|won't|shall)(?!\w)", re.I)

# Past participles that, after a form of "to be", almost always signal passive
# voice in developer documentation. Deliberately a curated subset: a general
# passive detector produces too many false positives to gate a build on.
PASSIVE_PARTICIPLES = [
    "created", "generated", "provided", "performed", "required", "supported",
    "configured", "installed", "defined", "returned", "executed", "deployed",
    "stored", "enabled", "disabled", "called", "executed", "handled",
    "displayed", "rendered", "uploaded", "downloaded", "removed", "added",
]
PASSIVE_RE = re.compile(
    r"(?<!\w)(?:is|are|was|were|be|been|being)\s+(?:not\s+|also\s+)?"
    r"(?:" + "|".join(PASSIVE_PARTICIPLES) + r")(?!\w)",
    re.I,
)
PASSIVE_BY_RE = re.compile(
    r"(?<!\w)(?:is|are|was|were|be|been|being|gets|got)\s+(?:not\s+|also\s+)?"
    r"\w+(?:ed|en)\s+by(?!\w)",
    re.I,
)

# Common English function words, used as a cheap language signal.
ENGLISH_STOPWORDS = {
    "the", "and", "you", "to", "of", "in", "that", "for", "with", "your",
    "this", "from", "it", "as", "on", "or", "an", "is", "are", "not",
}

# Sections that the README must contain as level-2 headings.
#
# Every other check in this file validates a claim that the README makes, so
# none of them notices a claim that is gone. A README cut down to its title
# passes all of them. This list is the floor: the section must exist, sit at
# the right level, and hold something.
#
# The second element names the weakest evidence that the section still speaks:
#
#   "prose"     at least MIN_SECTION_PROSE_LINES non-blank, non-heading lines
#   "commands"  the same, plus at least one fenced code block
#   "table"     the same, plus at least one Markdown table
REQUIRED_SECTIONS = (
    ("Before you begin", "prose"),
    ("Set up your environment", "commands"),
    ("Run the demos locally", "commands"),
    ("Available demos", "table"),
    ("Repository layout", "table"),
    ("Run the demos in a container", "commands"),
    ("Deploy to Cloud Run", "commands"),
    ("Verify this README", "commands"),
    ("Troubleshooting", "prose"),
    ("Contribute", "prose"),
    ("Security", "prose"),
    ("License", "prose"),
)

# Subsections that must survive as well. The level is not fixed, because a
# writer can reasonably move one of these under a different parent.
#
# "Gemini model identifiers" is here for a specific reason: check_models only
# cross-checks the pinned models when the README names at least one of them,
# so deleting the section that names them takes the cross-check down with it.
# Requiring the section, and requiring its table, closes that circle.
REQUIRED_SUBSECTIONS = (
    ("Environment variables", "table"),
    ("Gemini model identifiers", "table"),
)

MIN_SECTION_PROSE_LINES = 2
MIN_INTRO_WORDS = 40


# ---------------------------------------------------------------------------
# Result plumbing
# ---------------------------------------------------------------------------


class Results:
    def __init__(self) -> None:
        self.checks: list[tuple[str, bool, str, list[str]]] = []

    def add(self, name: str, failures: list[str], detail: str) -> None:
        self.checks.append((name, not failures, detail, failures))

    @property
    def failed(self) -> int:
        return sum(1 for _, ok, _, _ in self.checks if not ok)

    @property
    def passed(self) -> int:
        return sum(1 for _, ok, _, _ in self.checks if ok)

    def report(self) -> int:
        width = max(len(name) for name, _, _, _ in self.checks)
        for name, ok, detail, failures in self.checks:
            status = "PASS" if ok else "FAIL"
            print(f"[{status}] {name.ljust(width)}  {detail}")
            for failure in failures:
                print(f"         - {failure}")
        print()
        print(f"Summary: {self.passed} passed, {self.failed} failed")
        return 1 if self.failed else 0


# ---------------------------------------------------------------------------
# README parsing helpers
# ---------------------------------------------------------------------------


class Readme:
    def __init__(self, text: str) -> None:
        self.text = text
        self.lines = text.split("\n")
        self.code_blocks: list[tuple[str, list[str], int]] = []
        self.prose: list[tuple[int, str]] = []
        self.unterminated_fence: int | None = None
        self._split()

    def _split(self) -> None:
        in_fence = False
        lang = ""
        buf: list[str] = []
        start = 0
        for number, line in enumerate(self.lines, 1):
            fence = re.match(r"^\s*```(.*)$", line)
            if fence:
                if in_fence:
                    self.code_blocks.append((lang, buf, start))
                    in_fence, lang, buf = False, "", []
                else:
                    in_fence, lang, buf, start = True, fence.group(1).strip(), [], number
                continue
            if in_fence:
                buf.append(line)
            else:
                self.prose.append((number, line))
        if in_fence:
            self.unterminated_fence = start
            self.code_blocks.append((lang, buf, start))

    @property
    def code_text(self) -> str:
        return "\n".join("\n".join(body) for _, body, _ in self.code_blocks)

    @property
    def prose_text(self) -> str:
        return "\n".join(line for _, line in self.prose)

    def headings(self) -> list[tuple[int, int, str]]:
        found = []
        for number, line in self.prose:
            match = HEADING_RE.match(line)
            if match:
                found.append((number, len(match.group(1)), match.group(2)))
        return found

    def section(self, title_substring: str) -> list[str]:
        """Return the lines of the section whose heading contains the substring.

        Only prose lines are scanned. A ``#`` comment inside a fenced code block
        therefore cannot be mistaken for a heading and hijack the section.
        """
        collected: list[str] = []
        level = None
        for _, line in self.prose:
            match = HEADING_RE.match(line)
            if match:
                if level is None:
                    if title_substring.lower() in match.group(2).lower():
                        level = len(match.group(1))
                    continue
                if len(match.group(1)) <= level:
                    break
                continue
            if level is not None:
                collected.append(line)
        return collected


def strip_inline_code(line: str) -> str:
    return INLINE_CODE_RE.sub(" ", line)


def strip_links(line: str) -> str:
    return LINK_RE.sub(lambda m: m.group(1), line)


def inline_code_tokens(line: str) -> list[str]:
    return [m.group(1) for m in INLINE_CODE_RE.finditer(line)]


def prose_blocks(readme: Readme) -> list[tuple[int, str]]:
    """Group prose into logical blocks: one list item, paragraph, or table row.

    Returns (first line number, flattened text). Fenced code blocks are already
    excluded from ``readme.prose``, so a claim that spans several wrapped lines
    arrives here as one string.
    """
    blocks: list[tuple[int, str]] = []
    current: list[str] = []
    start: int | None = None

    def flush() -> None:
        nonlocal current, start
        if current and start is not None:
            blocks.append((start, " ".join(current)))
        current, start = [], None

    for number, line in readme.prose:
        stripped = line.strip()
        if not stripped or HEADING_RE.match(line):
            flush()
            continue
        if LIST_ITEM_RE.match(line) or stripped.startswith("|"):
            flush()
        if start is None:
            start = number
        current.append(stripped)
    flush()
    return blocks


def markdown_lists(readme: Readme) -> list[list[tuple[int, str, bool]]]:
    """Group prose list items into lists.

    Each list is a sequence of (line number, flattened item text, interrupted).
    ``interrupted`` is True when a fenced code block sits inside the item, which
    means the item is a procedure step rather than a phrase.
    """
    lists: list[list[tuple[int, str, bool]]] = []
    current: list[tuple[int, str, bool]] = []
    marker_kind: str | None = None
    indent: int | None = None

    prose_numbers = {number for number, _ in readme.prose}
    item_lines: list[str] = []
    item_number = 0
    item_indent = 0
    interrupted = False
    seen_gap = False

    def flush_item() -> None:
        nonlocal item_lines, interrupted
        if item_lines:
            current.append((item_number, " ".join(item_lines), interrupted))
        item_lines, interrupted = [], False

    def flush_list() -> None:
        nonlocal current, marker_kind, indent
        flush_item()
        if len(current) > 1:
            lists.append(current)
        current, marker_kind, indent = [], None, None

    for number, line in enumerate(readme.lines, 1):
        if number not in prose_numbers:
            # A fenced code block line. If it falls inside an open item, the
            # item is a procedure step.
            if item_lines or current:
                interrupted = True
            continue
        match = LIST_ITEM_RE.match(line)
        stripped = line.strip()
        if match:
            kind = "ol" if match.group(2)[0].isdigit() else "ul"
            width = len(match.group(1))
            if marker_kind is not None and (kind != marker_kind or width != indent):
                flush_list()
            flush_item()
            marker_kind, indent = kind, width
            item_number, item_indent = number, width
            item_lines = [match.group(3).strip()]
            seen_gap = False
            continue
        if not stripped:
            seen_gap = True
            continue
        if current or item_lines:
            if len(line) - len(line.lstrip()) > item_indent:
                if seen_gap:
                    # An indented continuation paragraph still belongs to the
                    # item, but it means the item is not a simple phrase.
                    interrupted = True
                item_lines.append(stripped)
                seen_gap = False
                continue
            flush_list()
    flush_list()
    return lists



# ---------------------------------------------------------------------------
# Repository facts
# ---------------------------------------------------------------------------


def iter_repo_files() -> list[Path]:
    files = []
    for path in REPO.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file():
            files.append(path)
    return files


def app_files() -> set[str]:
    apps_dir = REPO / "apps"
    if not apps_dir.is_dir():
        return set()
    return {
        p.relative_to(REPO).as_posix()
        for p in apps_dir.rglob("*.py")
        if not any(part in SKIP_DIRS for part in p.parts)
    }


def requirements_packages() -> set[str]:
    path = REPO / "requirements.txt"
    if not path.exists():
        return set()
    names = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        name = re.split(r"[=<>!~\[ ]", line, maxsplit=1)[0].strip()
        if name:
            names.add(normalize_package(name))
    return names


def requirements_lines() -> list[str]:
    """Every dependency line in requirements.txt, blanks and comments removed.

    requirements_packages() returns a set, so it cannot answer "how many lines
    does this file hold": two lines naming the same package would count once.
    The README makes exactly that counted claim, so it needs a list.
    """
    path = REPO / "requirements.txt"
    if not path.exists():
        return []
    lines = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        lines.append(line)
    return lines


VERSION_CONSTRAINT_RE = re.compile(r"[=<>!~]")


def unconstrained_requirements() -> list[str]:
    """Dependency lines that name no version, so an install can drift."""
    return [
        line for line in requirements_lines()
        if not VERSION_CONSTRAINT_RE.search(line)
    ]


def normalize_package(name: str) -> str:
    return name.strip().lower().replace("-", "_")


def normalize_requirement(line: str) -> str:
    """A requirement line reduced to what a comparison should care about.

    `GitPython == 3.1.62` and `gitpython==3.1.62` declare the same thing, so a
    README that quotes one must not fail against a file that spells the other.
    """
    return re.sub(r"\s+", "", line).lower().replace("-", "_")


def source_env_vars() -> dict[str, str]:
    """Environment variables read by Python source, mapped to the file that reads them."""
    pattern = re.compile(
        r"""os\.(?:environ\.get|getenv)\(\s*['"]([A-Za-z_][A-Za-z0-9_]*)['"]"""
        r"""|os\.environ\[\s*['"]([A-Za-z_][A-Za-z0-9_]*)['"]\s*\]"""
    )
    found: dict[str, str] = {}
    for path in iter_repo_files():
        if path.suffix != ".py" or path == Path(__file__).resolve():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in pattern.finditer(text):
            name = match.group(1) or match.group(2)
            found.setdefault(name, path.relative_to(REPO).as_posix())
    return found


def env_var_definitions() -> dict[str, str]:
    """Environment variables the repository actually sets or reads.

    Unlike a substring search over every file, this looks only at real
    environment-variable syntax: ``os.environ``/``os.getenv`` in Python,
    ``ENV`` in a Dockerfile, ``export`` in shell, and the gcloud
    ``--set-env-vars``/``--update-env-vars`` flags. A name that appears only in
    a comment, a prompt template, or in this script does not count.
    """
    found = dict(source_env_vars())

    env_flag = re.compile(
        r"--(?:set|update)-env-vars[=\s]+[\"']?([^\"'\s]+)"
    )
    for path in iter_repo_files():
        if path == Path(__file__).resolve() or path == README_PATH:
            continue
        if path.name != "Dockerfile" and path.suffix not in {".sh", ".yaml", ".yml"}:
            continue
        rel = path.relative_to(REPO).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        if path.name == "Dockerfile":
            for match in re.finditer(r"^\s*ENV\s+([A-Za-z_][A-Za-z0-9_]*)[=\s]", text, re.M):
                found.setdefault(match.group(1), rel)
        for match in re.finditer(r"(?<!\w)export\s+([A-Za-z_][A-Za-z0-9_]*)=", text):
            found.setdefault(match.group(1), rel)
        for match in env_flag.finditer(text):
            for assignment in match.group(1).split(","):
                name = assignment.split("=", 1)[0].strip()
                if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
                    found.setdefault(name, rel)
    return found


def repo_module_imports() -> dict[str, set[str]]:
    """Top-level module names each repository Python file really imports.

    Uses ``ast`` rather than a text search, so an ``import`` line that only
    appears inside a docstring or a prompt template does not count.
    """
    imports: dict[str, set[str]] = {}
    for path in iter_repo_files():
        if path.suffix != ".py":
            continue
        rel = path.relative_to(REPO).as_posix()
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            imports[rel] = set()
            continue
        names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    names.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names.add(node.module.split(".")[0])
        imports[rel] = names
    return imports



def cloudbuild_substitutions() -> dict[str, str]:
    path = REPO / "cloudbuild.yaml"
    if not path.exists():
        return {}
    subs: dict[str, str] = {}
    inside = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if re.match(r"^substitutions:\s*$", line):
            inside = True
            continue
        if inside:
            match = re.match(r"^\s+(_[A-Z0-9_]+):\s*(\S+)\s*$", line)
            if match:
                subs[match.group(1)] = match.group(2)
            elif line.strip() and not line.startswith((" ", "\t")):
                break
    return subs


def git_origin_slug() -> str | None:
    config = REPO / ".git" / "config"
    if not config.exists():
        return None
    text = config.read_text(encoding="utf-8", errors="replace")
    match = re.search(r'\[remote "origin"\][^\[]*?url\s*=\s*(\S+)', text, re.S)
    if not match:
        return None
    return url_slug(match.group(1))


def url_slug(url: str) -> str | None:
    url = url.strip().rstrip("/")
    if url.endswith(".git"):
        url = url[:-4]
    match = re.search(r"[:/]([^/:]+)/([^/:]+)$", url)
    if not match:
        return None
    return f"{match.group(1).lower()}/{match.group(2).lower()}"


def declared_license() -> str | None:
    path = REPO / "LICENSE"
    if not path.exists():
        return None
    head = path.read_text(encoding="utf-8", errors="replace")[:4000]
    if "Apache License" in head and "Version 2.0" in head:
        return "Apache License 2.0"
    if "MIT License" in head:
        return "MIT License"
    if "GNU GENERAL PUBLIC LICENSE" in head.upper():
        return "GNU General Public License"
    if "BSD" in head:
        return "BSD License"
    return None


def source_env_reads_by_file() -> dict[str, set[str]]:
    """Environment variables each Python file reads, keyed by repository path."""
    pattern = re.compile(
        r"""os\.(?:environ\.get|getenv)\(\s*['"]([A-Za-z_][A-Za-z0-9_]*)['"]"""
        r"""|os\.environ\[\s*['"]([A-Za-z_][A-Za-z0-9_]*)['"]\s*\]"""
    )
    found: dict[str, set[str]] = {}
    for path in iter_repo_files():
        if path.suffix != ".py" or path == Path(__file__).resolve():
            continue
        rel = path.relative_to(REPO).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        found[rel] = {m.group(1) or m.group(2) for m in pattern.finditer(text)}
    return found


def top_level_app_files() -> set[str]:
    """Demo files directly under apps/, excluding support packages."""
    apps_dir = REPO / "apps"
    if not apps_dir.is_dir():
        return set()
    return {p.name for p in apps_dir.glob("*.py")}


def home_page_counts() -> tuple[int, int, int]:
    """(categories, sidebar entries, distinct demo paths) declared in home.py."""
    path = REPO / "home.py"
    if not path.exists():
        return (0, 0, 0)
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return (0, 0, 0)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Dict):
            continue
        if not any(isinstance(t, ast.Name) and t.id == "demo_pages" for t in node.targets):
            continue
        entries = 0
        paths: set[str] = set()
        for value in node.value.values:
            if not isinstance(value, ast.List):
                continue
            entries += len(value.elts)
            for element in value.elts:
                if not isinstance(element, ast.Dict):
                    continue
                for key, item in zip(element.keys, element.values):
                    if (
                        isinstance(key, ast.Constant)
                        and key.value == "path"
                        and isinstance(item, ast.Constant)
                    ):
                        paths.add(str(item.value))
        return len(node.value.keys), entries, len(paths)
    return (0, 0, 0)


def home_page_demos() -> dict[str, set[str]]:
    """Map each demo path in home.py to the sidebar labels that open it.

    A path maps to more than one label only when home.py lists the same demo
    under two names, so the value is a set rather than a single string.
    """
    path = REPO / "home.py"
    if not path.exists():
        return {}
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return {}
    demos: dict[str, set[str]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Dict):
            continue
        if not any(isinstance(t, ast.Name) and t.id == "demo_pages" for t in node.targets):
            continue
        for value in node.value.values:
            if not isinstance(value, ast.List):
                continue
            for element in value.elts:
                if not isinstance(element, ast.Dict):
                    continue
                fields = {
                    key.value: item.value
                    for key, item in zip(element.keys, element.values)
                    if isinstance(key, ast.Constant) and isinstance(item, ast.Constant)
                }
                if "path" in fields and "title" in fields:
                    demos.setdefault(str(fields["path"]), set()).add(str(fields["title"]))
        return demos
    return demos


def declared_gemini_models() -> set[str]:
    """Gemini model identifiers that utils_vertex.py names.

    The module used to build model objects, so the old version of this
    function looked for the calls that built them: ``GenerativeModel(...)`` and
    ``from_pretrained(...)``. google-genai takes a model as a string, so
    utils_vertex.py now holds the identifiers in module-level constants
    instead, and a scan for those calls finds nothing. Reading every quoted
    ``gemini-`` literal out of the file survives both shapes and does not care
    what a future constant is called.

    A comment that mentions an identifier without quoting it does not count,
    which is deliberate: the lifecycle note above MODEL_ID names the model it
    documents, and a note is not a declaration.
    """
    path = REPO / "utils_vertex.py"
    if not path.exists():
        return set()
    text = path.read_text(encoding="utf-8", errors="replace")
    return set(re.findall(r"[\"'](gemini-[\w.@-]+)[\"']", text))



def app_gemini_models() -> dict[str, set[str]]:
    """Gemini identifiers that files under apps/ hardcode, and where.

    utils_vertex.py is not the only place a model identifier hides: most demos
    build a picker out of literals of their own, and one pins a version that
    appears nowhere else. A README that documents utils_vertex.py alone sends
    the reader to edit one file and leaves the rest of the repository broken,
    so every identifier found here has to appear in the README.
    """
    found: dict[str, set[str]] = {}
    for path in sorted((REPO / "apps").rglob("*.py")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(r"[\"'](gemini-[\w.@-]+)[\"']", text):
            found.setdefault(match.group(1), set()).add(
                str(path.relative_to(REPO))
            )
    return found


def repo_source_text() -> str:
    """Every source, config, and build file, concatenated. Never the README."""
    parts = []
    for path in iter_repo_files():
        if path == README_PATH or path == Path(__file__).resolve():
            continue
        if path.suffix in {".py", ".yaml", ".yml", ".sh", ".toml", ".md", ".txt"} or (
            path.name in EXTENSIONLESS_PATHS
        ):
            parts.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


def repo_ports() -> set[str]:
    """Ports the repository actually configures."""
    ports: set[str] = set()
    config = REPO / ".streamlit" / "config.toml"
    if config.exists():
        match = re.search(r"^\s*port\s*=\s*(\d+)", config.read_text(encoding="utf-8"), re.M)
        if match:
            ports.add(match.group(1))
    dockerfile = REPO / "Dockerfile"
    if dockerfile.exists():
        text = dockerfile.read_text(encoding="utf-8")
        ports.update(re.findall(r"^\s*EXPOSE\s+(\d+)", text, re.M))
        ports.update(re.findall(r"--server\.port=(\d+)", text))
    return ports


def dockerfile_python_version() -> str | None:
    dockerfile = REPO / "Dockerfile"
    if not dockerfile.exists():
        return None
    match = re.search(r"^FROM\s+python:(\d+(?:\.\d+)*)", dockerfile.read_text(encoding="utf-8"), re.M)
    return match.group(1) if match else None


IGNORE_FILES = (".gitignore", ".dockerignore", ".gcloudignore")


def ignore_file_patterns() -> dict[str, set[str]]:
    patterns: dict[str, set[str]] = {}
    for name in IGNORE_FILES:
        path = REPO / name
        if not path.exists():
            continue
        patterns[name] = {
            line.strip()
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
    return patterns


def all_ignore_patterns() -> set[str]:
    merged: set[str] = set()
    for values in ignore_file_patterns().values():
        merged |= values
    return merged


def setup_script_apis() -> set[str]:
    path = REPO / "setup.sh"
    if not path.exists():
        return set()
    return set(re.findall(r"\b([a-z0-9-]+\.googleapis\.com)\b", path.read_text(encoding="utf-8")))


NUMBER_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20,
}
NUMBER_RE = r"(\d+|" + "|".join(NUMBER_WORDS) + r")"


def parse_number(token: str) -> int | None:
    token = token.strip().lower()
    if token.isdigit():
        return int(token)
    return NUMBER_WORDS.get(token)


BUILTIN_SUBSTITUTIONS = {
    "PROJECT_ID", "PROJECT_NUMBER", "BUILD_ID", "COMMIT_SHA", "SHORT_SHA",
    "REVISION_ID", "REPO_NAME", "REPO_FULL_NAME", "BRANCH_NAME", "TAG_NAME",
    "LOCATION", "TRIGGER_NAME", "SERVICE_ACCOUNT",
}

KNOWN_LICENSES = [
    "Apache License 2.0",
    "MIT License",
    "GNU General Public License",
    "BSD License",
    "Mozilla Public License",
]

MODEL_TOKEN_RE = re.compile(
    r"(?:gemini|imagegeneration|textembedding|multimodalembedding)[\w.@-]*"
)

# Naming a model the repository does not use is a defect when the README
# implies the code uses it, and is the whole point when the README says the
# model is gone or names what to move to. These cues, read from the prose
# around the identifier rather than from the identifier itself, separate the
# two. Without them a retirement notice cannot be written here at all.
MODEL_HISTORY_CUES = re.compile(
    r"\b(?:retire[sd]?|retiring|retirement|deprecat\w+|replace\w*|instead|"
    r"supersed\w+|upgrade\w*|migrat\w+|resolves?\s+to|no\s+longer|"
    r"successor)\b",
    re.I,
)

BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
UI_CONTEXT_WORDS = (
    "sidebar", "click", "button", "select", "menu", "list", "tab", "toolbar",
)

MONTH_NAMES = (
    "January|February|March|April|May|June|July|August|September|October|"
    "November|December"
)

# The one date format this README uses, and the two it must not: a numeric
# date is ambiguous across locales, and a month without a day cannot be lined
# up with a row of a source table that gives the day.
FULL_DATE_RE = re.compile(rf"\b(?:{MONTH_NAMES})\s+\d{{1,2}},\s+\d{{4}}\b")
DAYLESS_DATE_RE = re.compile(rf"\b(?:{MONTH_NAMES})\s+\d{{4}}\b")
NUMERIC_DATE_RE = re.compile(
    r"\b\d{4}-\d{1,2}-\d{1,2}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b"
)

# Wording that puts a retirement in the past. "retirement", which announces a
# future one, deliberately does not match.
PAST_RETIREMENT_RE = re.compile(
    r"\b(?:retired|shut\s+down|removed|withdrew|withdrawn)\b", re.I
)

# An identifier that names one immutable version: gemini-1.5-pro-001,
# textembedding-gecko-multilingual@001. An alias such as gemini-1.5-pro or
# gemini-2.5-flash does not qualify, because no row of a retirement table
# carries a date for an alias.
VERSIONED_MODEL_RE = re.compile(r"^[\w.-]+(?:@\d+|-\d{3})$")

# The lifecycle rows this README quotes, transcribed from
# https://cloud.google.com/vertex-ai/generative-ai/docs/learn/model-versioning
# on September 11, 2026. The retired rows sit in the "Retired models" section,
# inside the expander "The following table lists the retired models (click to
# expand)"; the rest come from the availability tables above it. Reading them
# out of the served HTML is the only way to see them: a text extraction that
# skips the expander loses the dates.
#
# Transcribing the source is what lets an offline script reject a date that no
# source states. The cost is that this table has to stay honest: every entry
# here has a row on that page, and a date that page does not carry belongs
# neither here nor in the README. Re-read the page before you edit either.
#
# The gemini-1.x and gemini-2.x strings below are reference data, not
# configuration. No file in this repository sends any of them to an API: they
# name the rows of Google's retirement table, which is what makes it possible
# to reject a retirement date the source does not give. A search for a stale
# model identifier should skip this table.
SOURCE_RETIREMENT_DATES = {
    "gemini-1.0-pro-001": "April 21, 2025",
    "gemini-1.0-pro-002": "April 21, 2025",
    "gemini-1.0-pro-vision-001": "April 21, 2025",
    "gemini-1.5-pro-001": "May 24, 2025",
    "gemini-1.5-flash-001": "May 24, 2025",
    "gemini-1.5-flash-002": "September 24, 2025",
    "textembedding-gecko-multilingual@001": "May 24, 2025",
    # Not retired: rows from the availability tables on the same page. The
    # page words the last two as "No sooner than" and "April 1, 2027".
    "gemini-2.5-flash": "October 20, 2026",
    "gemini-2.5-flash-lite": "October 20, 2026",
    "gemini-embedding-001": "May 20, 2028",
    "multimodalembedding@001": "April 1, 2027",
}

# The "Recommended upgrade" column of the retired-models table. A README that
# dates a retirement and then leaves out the upgrade the same row names has
# told the reader what broke and not what to do about it.
SOURCE_REPLACEMENTS = {
    "gemini-1.0-pro-001": "gemini-2.5-flash",
    "gemini-1.0-pro-002": "gemini-2.5-flash",
    "gemini-1.0-pro-vision-001": "gemini-2.5-flash",
    "gemini-1.5-pro-001": "gemini-2.5-flash",
    "gemini-1.5-flash-001": "gemini-2.5-flash-lite",
    "gemini-1.5-flash-002": "gemini-2.5-flash-lite",
    "textembedding-gecko-multilingual@001": "gemini-embedding-001",
}



# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def looks_like_path(token: str) -> bool:
    if not token or token != token.strip():
        return False
    if re.search(r"[\s:()\[\]{}<>*|\"'=$]", token):
        return False
    if token.startswith(("http://", "https://", "mailto:", "#")):
        return False
    if token in EXTENSIONLESS_PATHS:
        return True
    candidate = token.rstrip("/")
    suffix = Path(candidate).suffix
    if "/" in token and (suffix in PATH_SUFFIXES or token.endswith("/")):
        return True
    if suffix in PATH_SUFFIXES:
        return True
    if token.startswith(".") and "/" not in token and suffix == "":
        return True
    return False


def resolve(token: str) -> Path:
    return REPO / token.lstrip("./").rstrip("/") if token.startswith("./") else REPO / token.rstrip("/")


def check_paths(readme: Readme, results: Results) -> None:
    failures: list[str] = []
    checked: set[str] = set()
    # A name the README quotes because an ignore file lists it (for example
    # `.env`) is a pattern, not a claim that the path exists in the checkout.
    ignore_patterns = all_ignore_patterns()

    for number, line in readme.prose:
        for token in inline_code_tokens(line):
            if token in ignore_patterns:
                continue
            if looks_like_path(token):
                checked.add(token)
                if not resolve(token).exists():
                    failures.append(f"line {number}: `{token}` does not exist in the repository")

    for number, line in readme.prose:
        for match in LINK_RE.finditer(line):
            target = match.group(2)
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = target.split("#", 1)[0]
            if not target:
                continue
            checked.add(target)
            if not resolve(target).exists():
                failures.append(f"line {number}: link target `{target}` does not exist")

    code_token_re = re.compile(r"(?<![\w/.-])(\.?/?[\w./-]+\.(?:py|ya?ml|sh|txt|toml|md))\b")
    for _, body, start in readme.code_blocks:
        for offset, line in enumerate(body):
            for match in code_token_re.finditer(line):
                token = match.group(1)
                if ".venv" in token or token.startswith(("http", "-")):
                    continue
                checked.add(token)
                if not resolve(token).exists():
                    failures.append(
                        f"line {start + offset + 1}: command references `{token}`, which does not exist"
                    )

    results.add("paths", failures, f"{len(checked)} referenced paths checked")


def check_links(readme: Readme, results: Results) -> None:
    failures: list[str] = []
    total = 0
    for number, line in readme.prose:
        for match in LINK_RE.finditer(line):
            if match.group(0).startswith("!"):
                continue
            total += 1
            text = match.group(1).strip().lower().rstrip(".")
            if text in NON_DESCRIPTIVE_LINK_TEXT:
                failures.append(f"line {number}: link text \"{match.group(1)}\" is not descriptive")
            if not text:
                failures.append(f"line {number}: link has empty text")

    bare = 0
    for number, line in readme.prose:
        stripped = LINK_RE.sub(" ", strip_inline_code(line))
        for match in re.finditer(r"https?://\S+", stripped):
            bare += 1
            failures.append(f"line {number}: bare URL {match.group(0)}; use descriptive link text")

    results.add("links", failures, f"{total} links checked, {bare} bare URLs found")


def check_apps(readme: Readme, results: Results) -> None:
    failures: list[str] = []
    on_disk = app_files()
    mentioned = set(re.findall(r"apps/[\w./-]+\.py", readme.text))

    for path in sorted(on_disk - mentioned):
        failures.append(f"{path} exists under apps/ but the README never mentions it")
    for path in sorted(mentioned - on_disk):
        failures.append(f"the README mentions {path}, which does not exist")

    results.add(
        "apps",
        failures,
        f"{len(on_disk)} app files on disk, {len(mentioned)} referenced in the README",
    )


def documented_env_vars(readme: Readme) -> dict[str, str]:
    found: dict[str, str] = {}
    patterns = [
        re.compile(r"\bexport\s+([A-Z_][A-Z0-9_]*)="),
        re.compile(r"(?<!\w)-e\s+([A-Z_][A-Z0-9_]*)="),
        re.compile(r"--(?:set|update)-env-vars[=\s]+\"?([A-Z_][A-Z0-9_]*)="),
    ]
    for number, line in enumerate(readme.lines, 1):
        for pattern in patterns:
            for match in pattern.finditer(line):
                found.setdefault(match.group(1), f"line {number}")

    for line in readme.section("Environment variables"):
        match = re.match(r"^\|\s*`([A-Z_][A-Z0-9_]{2,})`\s*\|", line)
        if match:
            found.setdefault(match.group(1), "environment variables table")
    return found


def check_env_vars(readme: Readme, results: Results) -> None:
    failures: list[str] = []
    documented = documented_env_vars(readme)
    read_by_source = source_env_vars()
    defined = env_var_definitions()

    for name, where in sorted(documented.items()):
        if name not in defined:
            failures.append(
                f"{where}: the README documents {name}, but no Python, Dockerfile, "
                f"shell, or Cloud Build file in the repository sets or reads it"
            )

    for name, path in sorted(read_by_source.items()):
        if name not in documented:
            failures.append(f"{path} reads {name}, which the README does not document")

    # Negative claims: "<file> ... instead of reading `VAR`" or "does not read
    # `VAR`". A claim that a file ignores a variable is as checkable as a claim
    # that it reads one, and it is the kind of statement that quietly rots.
    per_file = source_env_reads_by_file()
    negative = re.compile(
        r"(?:instead of reading|rather than reading|does not read|never reads?)\s+`([A-Z_][A-Z0-9_]*)`",
        re.I,
    )
    negatives = 0
    for start, block in prose_blocks(readme):
        match = negative.search(block)
        if not match:
            continue
        name = match.group(1)
        for token in inline_code_tokens(block):
            if not token.endswith(".py") or not (REPO / token).is_file():
                continue
            negatives += 1
            if name in per_file.get(token, set()):
                failures.append(
                    f"line {start}: the README says {token} does not read {name}, "
                    f"but {token} calls os.environ for it"
                )

    results.add(
        "env_vars",
        failures,
        f"{len(documented)} documented, {len(read_by_source)} read by Python source, "
        f"{len(defined)} set or read anywhere in the repository, "
        f"{negatives} negative claims verified",
    )


def check_packages(readme: Readme, results: Results) -> None:
    failures: list[str] = []
    required = requirements_packages()
    named: dict[str, str] = {}

    for _, body, start in readme.code_blocks:
        for offset, line in enumerate(body):
            match = re.search(r"\bpip3?\s+install\s+(.*)", line)
            if not match:
                continue
            tokens = match.group(1).replace("\\", " ").split()
            skip_next = False
            for token in tokens:
                if skip_next:
                    skip_next = False
                    continue
                if token in ("-r", "--requirement", "-c", "--constraint"):
                    skip_next = True
                    continue
                if token.startswith("-"):
                    continue
                named.setdefault(normalize_package(token), f"line {start + offset + 1}")

    for line in readme.section("Key dependencies"):
        if line.lstrip().startswith(("-", "*")):
            for token in inline_code_tokens(line):
                named.setdefault(normalize_package(token), "key dependencies list")

    for name, where in sorted(named.items()):
        if name not in required:
            failures.append(f"{where}: `{name}` is not pinned in requirements.txt")

    # Prose that tells the reader to install or add a package. Naming a package
    # that requirements.txt does not list is allowed only when the same block
    # says so out loud, and only when that statement is true.
    prose_named = 0
    exempted = 0
    disclaimers = 0
    reported: set[str] = set()
    for start, block in prose_blocks(readme):
        disclaims = bool(NOT_LISTED_RE.search(block)) and "requirements.txt" in block
        instructions = INSTALL_INSTRUCTION_RE.findall(block)

        # Verify the claim against its own subject first. The block-wide token
        # scan below runs only when the block gives no install instruction, so
        # a block that says "requirements.txt does not list `x`. Add `x`."
        # would otherwise go unchecked on the first sentence.
        for raw in NOT_LISTED_SUBJECT_RE.findall(block):
            token = raw.strip()
            if " " in token or "/" in token or looks_like_path(token):
                continue
            name = normalize_package(token)
            if name in ("requirements.txt", "requirements_txt"):
                continue
            disclaimers += 1
            reported.add(name)
            if name in required:
                failures.append(
                    f"line {start}: the README says requirements.txt does not "
                    f"list `{token}`, but requirements.txt does list it"
                )

        if disclaims and not instructions:
            # A bare "requirements.txt does not pin `x`" is still a factual
            # claim about the repository. Verify it on its own.
            for token in inline_code_tokens(block):
                token = token.strip()
                if " " in token or "/" in token or looks_like_path(token):
                    continue
                name = normalize_package(token)
                if name in ("requirements.txt", "requirements_txt") or name in reported:
                    continue
                disclaimers += 1
                if name in required:
                    failures.append(
                        f"line {start}: the README says requirements.txt does not list "
                        f"`{token}`, but requirements.txt does list it"
                    )
            continue

        if not instructions:
            continue
        for raw in instructions:
            token = raw.strip()
            if " " in token or "/" in token or looks_like_path(token):
                continue
            name = normalize_package(token)
            if name in ("requirements.txt", "requirements_txt"):
                continue
            prose_named += 1
            if name in required:
                continue
            if not disclaims:
                failures.append(
                    f"line {start}: the README tells the reader to install `{token}`, "
                    f"which requirements.txt does not list, without saying so"
                )
                continue
            exempted += 1
        if disclaims:
            # The disclaimer itself is a factual claim. Verify it.
            for raw in instructions:
                name = normalize_package(raw.strip())
                disclaimers += 1
                if name in required:
                    failures.append(
                        f"line {start}: the README says requirements.txt does not list "
                        f"`{raw.strip()}`, but requirements.txt does list it"
                    )

    # The README states how many dependencies requirements.txt holds and how
    # many of them float. Both are facts about that file, and nothing above
    # checks them: the scans compare names, never counts. An edit to
    # requirements.txt therefore used to leave these numbers stale and still
    # pass, so verify them here.
    total = len(requirements_lines())
    unconstrained = len(unconstrained_requirements())
    counted = 0

    for start, block in prose_blocks(readme):
        text = strip_links(strip_inline_code(block))

        for match in re.finditer(rf"lists\s+{NUMBER_RE}\s+direct\s+dependenc", text, re.I):
            value = parse_number(match.group(1))
            if value is None:
                continue
            counted += 1
            if value != total:
                failures.append(
                    f'line {start}: "{match.group(0).strip()}", but requirements.txt '
                    f"holds {total} dependency lines"
                )

        pattern = (
            rf"{NUMBER_RE}\s+of\s+the\s+{NUMBER_RE}\s+lines\s+carry\s+"
            r"no\s+version\s+constraint"
        )
        for match in re.finditer(pattern, text, re.I):
            floating = parse_number(match.group(1))
            listed = parse_number(match.group(2))
            if floating is not None:
                counted += 1
                if floating != unconstrained:
                    failures.append(
                        f'line {start}: "{match.group(0).strip()}", but {unconstrained} '
                        f"lines in requirements.txt carry no version constraint"
                    )
            if listed is not None:
                counted += 1
                if listed != total:
                    failures.append(
                        f'line {start}: "{match.group(0).strip()}", but requirements.txt '
                        f"holds {total} dependency lines"
                    )

    # The README quotes some requirement lines verbatim, such as a floor that
    # holds a transitive dependency out of a vulnerable range. Names alone do
    # not catch an edited operator or version, so compare the quoted text
    # against the file.
    declared = {
        normalize_package(re.split(r"[=<>!~\[ ]", line, maxsplit=1)[0]): line
        for line in requirements_lines()
    }
    quoted = 0
    for start, block in prose_blocks(readme):
        for token in inline_code_tokens(block):
            token = token.strip()
            match = REQUIREMENT_SPEC_RE.fullmatch(token)
            if not match:
                continue
            quoted += 1
            name = normalize_package(match.group(1))
            if name not in declared:
                failures.append(
                    f"line {start}: the README quotes `{token}`, but "
                    f"requirements.txt does not list `{match.group(1)}`"
                )
            elif normalize_requirement(declared[name]) != normalize_requirement(token):
                failures.append(
                    f"line {start}: the README quotes `{token}`, but "
                    f"requirements.txt says `{declared[name]}`"
                )

    detail = (
        f"{len(named)} packages named in the README, {len(required)} in "
        f"requirements.txt, {prose_named} named in prose ({exempted} documented gaps, "
        f"{disclaimers} absence claims verified), {counted} counted claims and "
        f"{quoted} quoted constraints checked against requirements.txt"
    )
    results.add("packages", failures, detail)


def check_import_claims(readme: Readme, results: Results) -> None:
    """Verify every "file X imports Y" sentence against the parsed source.

    This is the check that a text search cannot do: `apps/appium-automation.py`
    contains the text ``from appium import webdriver``, but only inside a prompt
    template, so the file does not import ``appium``.
    """
    failures: list[str] = []
    imports = repo_module_imports()
    claims = 0

    for start, block in prose_blocks(readme):
        if not IMPORT_VERB_RE.search(block):
            continue
        tokens = inline_code_tokens(block)
        py_files = [t for t in tokens if t.endswith(".py") and (REPO / t).is_file()]
        if not py_files:
            continue
        actual: set[str] = set()
        for rel in py_files:
            actual |= {normalize_package(m) for m in imports.get(rel, set())}
        seen: set[str] = set()
        for token in tokens:
            if not re.fullmatch(r"[a-z_][a-z0-9_-]*", token) or token in seen:
                continue
            seen.add(token)
            name = normalize_package(token)
            claims += 1
            candidates = {name, PACKAGE_ALIASES.get(name, name)}
            if candidates & actual:
                continue
            failures.append(
                f"line {start}: the README says {' / '.join(py_files)} imports "
                f"`{token}`, but the parsed source of "
                f"{'that file' if len(py_files) == 1 else 'those files'} does not"
            )

    results.add(
        "import_claims",
        failures,
        f"{claims} module import claims checked against the parsed source",
    )


def check_clone_url(readme: Readme, results: Results) -> None:
    failures: list[str] = []
    origin = git_origin_slug()
    clones = re.findall(r"git clone\s+(\S+)", readme.code_text)
    detail = f"{len(clones)} clone commands; origin={origin or 'unknown'}"

    if not clones:
        failures.append("the README contains no `git clone` command")
    for url in clones:
        slug = url_slug(url)
        if slug is None:
            failures.append(f"cannot parse the clone URL {url}")
            continue
        if origin and slug != origin:
            failures.append(f"clone URL {url} does not match the git origin {origin}")
        directory = slug.split("/")[1]
        if origin is None and directory != REPO.name.lower():
            # No .git/config (for example, a tarball export). Fall back to the
            # checkout directory name so the check still has something real to
            # compare against.
            failures.append(
                f"clone URL {url} names the repository {directory}, but this "
                f"checkout is {REPO.name}"
            )
        if not re.search(rf"\bcd\s+{re.escape(directory)}\b", readme.code_text):
            failures.append(f"no `cd {directory}` follows the clone command")
    if origin is None:
        detail += f" (no .git/config; compared against the checkout name {REPO.name})"

    results.add("clone_url", failures, detail)


def check_cloudbuild(readme: Readme, results: Results) -> None:
    failures: list[str] = []
    subs = cloudbuild_substitutions()
    cloudbuild = REPO / "cloudbuild.yaml"
    cloudbuild_text = cloudbuild.read_text(encoding="utf-8") if cloudbuild.exists() else ""
    documented = set(re.findall(r"`(_[A-Z][A-Z0-9_]*)`", readme.text))

    for name in sorted(set(subs) - documented):
        failures.append(f"cloudbuild.yaml defines {name}, which the README does not document")
    for name in sorted(documented - set(subs)):
        failures.append(f"the README documents {name}, which cloudbuild.yaml does not define")

    # Every substitution needs a row in the defaults table, not just a passing
    # mention somewhere in the prose.
    tabulated: dict[str, str] = {}
    for line in readme.section("Deploy with Cloud Build"):
        row = re.match(r"^\|\s*`(_[A-Z0-9_]+)`\s*\|\s*`([^`]+)`\s*\|", line)
        if row:
            tabulated[row.group(1)] = row.group(2)
    for name in sorted(set(subs) - set(tabulated)):
        failures.append(
            f"cloudbuild.yaml defines {name}, which the README's substitutions table omits"
        )
    for name, value in sorted(tabulated.items()):
        if name in subs and subs[name] != value:
            failures.append(
                f"the README says {name} defaults to {value}, "
                f"but cloudbuild.yaml sets {subs[name]}"
            )

    # Validate the submit command against the pipeline itself, not against a
    # comment inside it: the config file has to exist, and every substitution
    # the command passes has to be one the pipeline can consume.
    submits = re.findall(r"^\s*(gcloud builds submit .*)$", readme.code_text, re.M)
    if not submits:
        failures.append("the README contains no `gcloud builds submit` command")
    for command in submits:
        config = re.search(r"--config[=\s]+(\S+)", command)
        if not config:
            failures.append(f"`{command.strip()}` passes no --config flag")
        elif not resolve(config.group(1)).is_file():
            failures.append(
                f"`{command.strip()}` points --config at {config.group(1)}, which does not exist"
            )
        elif resolve(config.group(1)).resolve() != cloudbuild.resolve():
            failures.append(
                f"`{command.strip()}` points --config at {config.group(1)}, not at cloudbuild.yaml"
            )
        passed = re.search(r"--substitutions[=\s]+(\S+)", command)
        if passed:
            for assignment in passed.group(1).split(","):
                key = assignment.split("=", 1)[0].strip()
                if not re.fullmatch(r"[A-Z_][A-Z0-9_]*", key):
                    failures.append(f"`{command.strip()}` passes the malformed substitution {key}")
                elif key in subs or key.startswith("_"):
                    continue
                elif key not in BUILTIN_SUBSTITUTIONS:
                    failures.append(
                        f"`{command.strip()}` passes {key}, which is neither a Cloud Build "
                        f"built-in nor a substitution cloudbuild.yaml defines"
                    )
                elif f"${{{key}}}" not in cloudbuild_text:
                    failures.append(
                        f"`{command.strip()}` passes {key}, which cloudbuild.yaml never references"
                    )

    for command in re.findall(r"^\s*(gcloud artifacts repositories create .*)$", readme.code_text, re.M):
        tokens = command.split()
        name = tokens[4] if len(tokens) > 4 else ""
        expected = subs.get("_ARTIFACT_REGISTRY_REPO")
        if expected and name != expected:
            failures.append(
                f"the README creates the Artifact Registry repository {name}, "
                f"but _ARTIFACT_REGISTRY_REPO defaults to {expected}"
            )
        location = re.search(r"--location=(\S+)", command)
        expected_location = subs.get("_REPO_LOCATION")
        if location and expected_location and location.group(1) != expected_location:
            failures.append(
                f"the README uses --location={location.group(1)}, "
                f"but _REPO_LOCATION defaults to {expected_location}"
            )

    results.add(
        "cloudbuild",
        failures,
        f"{len(subs)} substitutions defined, {len(tabulated)} tabulated, "
        f"{len(submits)} submit commands validated",
    )


def check_docker(readme: Readme, results: Results) -> None:
    failures: list[str] = []
    dockerfile = REPO / "Dockerfile"
    if not dockerfile.exists():
        results.add("docker", ["Dockerfile is missing"], "no Dockerfile")
        return
    text = dockerfile.read_text(encoding="utf-8")

    base = re.search(r"^FROM\s+(\S+)", text, re.M)
    if base and base.group(1) not in readme.text:
        failures.append(f"the README never mentions the base image {base.group(1)}")

    exposed = re.findall(r"^EXPOSE\s+(\d+)", text, re.M)
    for mapping in re.findall(r"docker run[^\n]*-p\s+(\d+):(\d+)", readme.code_text):
        if exposed and mapping[1] not in exposed:
            failures.append(
                f"`docker run -p {mapping[0]}:{mapping[1]}` targets a port the Dockerfile does not expose "
                f"(EXPOSE {', '.join(exposed)})"
            )

    cmd = re.search(r"^CMD\s+(.*)$", text, re.M)
    if cmd:
        entry = re.search(r'"([\w./-]+\.py)"', cmd.group(1))
        if entry and f"streamlit run {entry.group(1)}" not in readme.text:
            failures.append(
                f"the Dockerfile starts {entry.group(1)}, but the README never shows "
                f"`streamlit run {entry.group(1)}`"
            )

    # When the README quotes a value the Dockerfile bakes in, it has to quote the
    # whole literal. `ENV GCP_PROJECT=GCP_PROJECT=my-demo-project-400313` is
    # malformed, and a README that quotes only the tail hides the defect.
    literals = 0
    for name, value in re.findall(r"^\s*ENV\s+([A-Za-z_][A-Za-z0-9_]*)=(\S+)", text, re.M):
        tail = value.split("=", 1)[-1]
        if len(tail) < 8 or tail.lower() in {"true", "false"}:
            continue
        for start, block in prose_blocks(readme):
            if "Dockerfile" not in block or tail not in block:
                continue
            literals += 1
            if value not in block:
                failures.append(
                    f"line {start}: the README quotes {tail} as the Dockerfile value for "
                    f"{name}, but the Dockerfile sets it to {value}"
                )

    results.add(
        "docker",
        failures,
        f"base={base.group(1) if base else '?'}, exposed={','.join(exposed) or '?'}, "
        f"{literals} quoted ENV literals checked",
    )


def check_setup_script(readme: Readme, results: Results) -> None:
    failures: list[str] = []
    setup = REPO / "setup.sh"
    if not setup.exists():
        results.add("setup_sh", ["setup.sh is missing"], "no setup.sh")
        return
    text = setup.read_text(encoding="utf-8")

    documented_apis = set(re.findall(r"\b([a-z0-9-]+\.googleapis\.com)\b", readme.text))
    enabled_apis = setup_script_apis()
    for api in sorted(documented_apis - enabled_apis):
        failures.append(f"the README lists the API {api}, which setup.sh does not enable")
    for api in sorted(enabled_apis - documented_apis):
        failures.append(f"setup.sh enables the API {api}, which the README does not list")

    identifiers = 0
    for line in readme.section("setup.sh"):
        for token in inline_code_tokens(line):
            if looks_like_path(token) or " " in token:
                continue
            if not re.match(r"^[A-Za-z_][\w.-]*$", token):
                continue
            identifiers += 1
            if token not in text:
                failures.append(f"the setup.sh section mentions `{token}`, which setup.sh does not contain")

    results.add(
        "setup_sh",
        failures,
        f"{len(enabled_apis)} APIs and {identifiers} identifiers cross-checked against setup.sh",
    )


def check_placeholders(readme: Readme, results: Results) -> None:
    failures: list[str] = []
    occurrences = 0
    lowered = [line.lower() for line in readme.lines]
    for index, line in enumerate(readme.lines):
        for pattern in PLACEHOLDER_PATTERNS:
            if pattern.lower() not in line.lower():
                continue
            occurrences += 1
            window = lowered[max(0, index - PLACEHOLDER_WINDOW): index + PLACEHOLDER_WINDOW + 1]
            # The instruction has to name this placeholder. "Replace" on its own
            # nearby is not enough: it may be telling the reader to replace a
            # different token.
            marked = any(
                marker in text and pattern.lower() in text
                for text in window
                for marker in PLACEHOLDER_MARKERS
            )
            if not marked:
                failures.append(
                    f"line {index + 1}: placeholder \"{pattern}\" is not marked for the reader to replace"
                )
    detail = f"{occurrences} placeholder occurrences"
    if not failures:
        detail += ", all marked for the reader to replace"
    results.add("placeholders", failures, detail)


def check_license(readme: Readme, results: Results) -> None:
    failures: list[str] = []
    name = declared_license()
    if name is None:
        failures.append("cannot identify the license from the LICENSE file")
    else:
        if name not in readme.text:
            failures.append(f"the LICENSE file is {name}, which the README does not state")
        if not re.search(r"\]\(LICENSE\)", readme.text):
            failures.append("the README does not link to the LICENSE file")
        for other in KNOWN_LICENSES:
            if other == name:
                continue
            for number, line in readme.prose:
                if other in line:
                    failures.append(
                        f"line {number}: the README names the {other}, but the LICENSE file is the {name}"
                    )
    results.add("license", failures, f"LICENSE detected as {name or 'unknown'}")


def heading_violations(heading: str) -> list[str]:
    problems = []
    if EMOJI_RE.search(heading):
        problems.append("contains an emoji")

    text = INLINE_CODE_RE.sub(" ", heading)
    for noun in PROPER_NOUNS:
        text = text.replace(noun, " ")

    words = re.findall(r"[A-Za-z][A-Za-z0-9'\u2019-]*", text)
    for index, word in enumerate(words):
        if index == 0:
            continue
        if word.isupper() and len(word) <= 6:
            continue
        if word[0].isupper():
            problems.append(
                f'"{word}" is capitalized; use sentence case, or add the word to '
                f"PROPER_NOUNS in check_readme.py if it is a proper noun"
            )
    return problems


def check_headings(readme: Readme, results: Results) -> None:
    failures: list[str] = []
    headings = readme.headings()
    for number, _, heading in headings:
        for problem in heading_violations(heading):
            failures.append(f'line {number}: heading "{heading}" {problem}')
    results.add("headings", failures, f"{len(headings)} headings checked for sentence case and emoji")


def check_banned_words(readme: Readme, results: Results) -> None:
    failures: list[str] = []
    for number, line in readme.prose:
        text = strip_inline_code(line)
        for word in BANNED_WORDS:
            pattern = re.escape(word).replace(r"\ ", r"\s+")
            for match in re.finditer(rf"(?<!\w){pattern}(?!\w)", text, re.I):
                failures.append(f'line {number}: banned word "{match.group(0)}" (Google word list)')
    results.add("banned_words", failures, f"{len(BANNED_WORDS)} banned terms checked")


def check_voice(readme: Readme, results: Results) -> None:
    failures: list[str] = []
    patterns = [
        (re.compile(r"(?<!\w)(we|our|ours|we're|we've)(?!\w)", re.I), "first person plural; address the reader as \"you\""),
        (re.compile(r"(?<!\w)us(?![-\w])", re.I), "first person plural; address the reader as \"you\""),
        (re.compile(r"(?<!\w)let's(?!\w)", re.I), "first person plural; address the reader as \"you\""),
        (re.compile(r"(?<!\w)I(?!\w)"), "first person singular"),
        (re.compile(r"\bthe user (?:should|must|can|will|needs|has)\b", re.I), "third person; address the reader as \"you\""),
        (re.compile(r"\b(?:the developer|the reader) (?:should|must|can|will)\b", re.I), "third person; address the reader as \"you\""),
        (FUTURE_TENSE_RE, "future tense; use the present tense"),
        (PASSIVE_RE, "passive voice; name the actor and use an active verb"),
        (PASSIVE_BY_RE, "passive voice; name the actor and use an active verb"),
    ]
    for number, line in readme.prose:
        text = strip_inline_code(line)
        for pattern, reason in patterns:
            for match in pattern.finditer(text):
                failures.append(f'line {number}: "{match.group(0).strip()}" is {reason}')
    results.add(
        "voice",
        failures,
        "first person, third person, future tense, and passive constructions checked",
    )


def check_lists(readme: Readme, results: Results) -> None:
    """Check that the items in one list are punctuated consistently.

    Google style requires parallel list items. Terminal punctuation is the part
    of parallelism a script can judge without guessing at grammar: within a
    list, either every item is a sentence that ends with a period or none is.
    Procedure lists whose items wrap a code block are skipped, because their
    text ends with a colon by design.
    """
    failures: list[str] = []
    lists = markdown_lists(readme)
    checked = 0
    for items in lists:
        if any(interrupted for _, _, interrupted in items):
            continue
        checked += 1
        with_period = [n for n, text, _ in items if text.rstrip().endswith(".")]
        if with_period and len(with_period) != len(items):
            without = [n for n, text, _ in items if not text.rstrip().endswith(".")]
            failures.append(
                f"list starting at line {items[0][0]}: "
                f"{len(with_period)} of {len(items)} items end with a period "
                f"(items at lines {', '.join(str(n) for n in without)} do not); "
                f"punctuate list items consistently"
            )
    results.add("lists", failures, f"{checked} of {len(lists)} lists checked for parallel punctuation")


def check_code_fences(readme: Readme, results: Results) -> None:
    failures: list[str] = []
    if readme.unterminated_fence is not None:
        failures.append(f"line {readme.unterminated_fence}: fenced code block is never closed")
    for lang, _, start in readme.code_blocks:
        if not lang:
            failures.append(f"line {start}: fenced code block has no language tag")
    results.add("code_fences", failures, f"{len(readme.code_blocks)} fenced code blocks checked")


def check_language(readme: Readme, results: Results) -> None:
    """Check that the README is plain ASCII and reads as English.

    The ASCII half catches smart quotes and stray glyphs. The stopword half is a
    coarse language signal: English prose of this length always contains a high
    proportion of function words such as "the", "and", and "you". It detects a
    README written in another language; it does not certify grammar.
    """
    failures: list[str] = []
    non_ascii = {}
    allowed = set("\u2014\u2013\u2019\u201c\u201d\u00a0")
    for number, line in readme.prose:
        for char in line:
            if ord(char) > 127 and char not in allowed:
                non_ascii.setdefault(char, number)
    for char, number in non_ascii.items():
        failures.append(f"line {number}: unexpected non-ASCII character {char!r}")

    words = re.findall(r"[A-Za-z']+", strip_inline_code(readme.prose_text).lower())
    hits = [w for w in words if w in ENGLISH_STOPWORDS]
    distinct = len({w for w in hits})
    ratio = len(hits) / len(words) if words else 0.0
    if words:
        if distinct < 8:
            failures.append(
                f"only {distinct} of the {len(ENGLISH_STOPWORDS)} common English "
                f"function words appear; the README may not be in English"
            )
        if ratio < 0.10:
            failures.append(
                f"English function words are {ratio:.1%} of the text, below the 10% "
                f"floor for English prose; the README may not be in English"
            )
    results.add(
        "language",
        failures,
        f"{len(words)} words, {ratio:.1%} English function words, {distinct} distinct, ASCII checked",
    )


def check_models(readme: Readme, results: Results) -> None:
    """Cross-check model identifiers against utils_vertex.py, in both directions.

    A README that names a model the code does not use sends the reader to a
    model that never loads. A README that describes the pinned models but skips
    some of them hides the identifiers most likely to be retired.

    The first rule has one exception, and it is not a loophole: a README has to
    be able to say "Vertex AI retired this version" or "move to that one", and
    neither identifier is in the repository by definition. An identifier is
    therefore exempt only where the surrounding paragraph, list item, or table
    cell marks it as history or as a replacement, and only if every place that
    names it does so.
    """
    failures: list[str] = []
    declared = declared_gemini_models()
    source = repo_source_text()

    named: set[str] = set()
    unmarked: dict[str, int] = {}
    # Blocks, not lines: a wrapped sentence puts the identifier and the word
    # "retired" on different physical lines, and they belong to one claim.
    for number, block in prose_blocks(readme):
        marked = bool(MODEL_HISTORY_CUES.search(strip_inline_code(block)))
        for token in inline_code_tokens(block):
            if not MODEL_TOKEN_RE.fullmatch(token):
                continue
            named.add(token)
            if not marked:
                unmarked.setdefault(token, number)

    exempt = 0
    for token in sorted(named):
        if token in source:
            continue
        if token not in unmarked:
            exempt += 1
            continue
        failures.append(
            f"line {unmarked[token]}: the README names the model `{token}`, "
            f"which no file in the repository uses, in a block that does not "
            f"mark it as retired or as a replacement"
        )

    if declared and any(name in readme.text for name in declared):
        for name in sorted(declared - named):
            failures.append(
                f"utils_vertex.py pins the Gemini model {name}, which the README does not name"
            )

    # Naming a model in passing is not the same as giving the reader its
    # status. The status table is what a reader consults before editing
    # utils_vertex.py, so it needs a row per pinned model, the way the demo
    # table needs a row per demo.
    status_section = readme.section("Gemini model identifiers")
    if status_section:
        tabulated = set()
        for line in status_section:
            match = re.match(r"^\|\s*`([^`]+)`\s*\|", line)
            if match:
                tabulated.add(match.group(1))
        for name in sorted(declared - tabulated):
            failures.append(
                f'utils_vertex.py pins the Gemini model {name}, which the '
                f'status table under "Gemini model identifiers" does not list'
            )

    # A model identifier under apps/ is as real as one in utils_vertex.py.
    # Most demos ignore utils_vertex.py and build their own picker, so a
    # README that stops at utils_vertex.py leaves the reader editing one file
    # out of thirteen.
    app_models = app_gemini_models()
    for name in sorted(app_models):
        if name in named:
            continue
        where = sorted(app_models[name])
        failures.append(
            f"{where[0]} names the Gemini model {name}, which the README "
            f"does not name ({len(where)} file(s) name it)"
        )

    results.add(
        "models",
        failures,
        f"{len(named)} model identifiers in the README "
        f"({exempt} named only as retired or as replacements), "
        f"{len(declared)} Gemini models in utils_vertex.py, "
        f"{len(app_models)} hardcoded under apps/",
    )



def enclosing_section(
    spans: list[tuple[int, int, str, list[str]]], number: int
) -> tuple[int, int, str, list[str]] | None:
    """Return the innermost section of level 2 or deeper that holds a line.

    The level-1 title owns the whole document, so it is not an answer here: a
    link at the far end of the README must not count as the source for a claim
    made at the near end.
    """
    best = None
    for start, level, title, body in spans:
        if level < 2 or not start < number <= start + len(body):
            continue
        if best is None or (level, start) > (best[1], best[0]):
            best = (start, level, title, body)
    return best


def section_cites_a_source(body: list[str]) -> bool:
    """True when the section body carries at least one external link."""
    for line in body:
        for match in LINK_RE.finditer(line):
            if match.group(0).startswith("!"):
                continue
            if match.group(2).startswith(("http://", "https://")):
                return True
    return False


def check_dates(readme: Readme, results: Results) -> None:
    """Hold every dated claim to the source row it comes from.

    This script never opens a network connection, so it cannot re-read the
    lifecycle page. What it can do is compare each date against
    SOURCE_RETIREMENT_DATES, which transcribes the rows of that page, and
    refuse the shapes of a dated claim that a reader cannot confirm:

    - a date in a section that links to no source at all
    - a date that no transcribed row gives for any model the block names, so
      the number rests on nothing
    - a retirement date that names no specific model version, and so matches
      no row of any published retirement table
    - a retirement dated in the past tense whose row also names an upgrade,
      written without that upgrade
    - a date written in a format the source tables do not use
    - a retirement written in the past tense but dated in the future

    The second rule is the one that decides whether a date is a fact or a
    number somebody remembered. It also fixes the whole README to one source:
    a date can only enter this file by first entering the transcription, and
    the transcription carries the URL, the fetch date, and the expander the
    rows hide behind.
    """
    failures: list[str] = []
    spans = section_spans(readme)
    today = datetime.date.today()
    dates = 0
    sourced = 0

    for number, block in prose_blocks(readme):
        text = strip_links(block)

        for match in NUMERIC_DATE_RE.finditer(text):
            failures.append(
                f"line {number}: the date {match.group(0)} is numeric, so its "
                f"day and month order depends on the reader; write it as "
                f"Month D, YYYY"
            )
        for match in DAYLESS_DATE_RE.finditer(text):
            failures.append(
                f'line {number}: the date "{match.group(0)}" gives no day, so '
                f"it matches no row of a source table; write it as Month D, YYYY"
            )

        found = FULL_DATE_RE.findall(text)
        if not found:
            continue
        dates += len(found)

        section = enclosing_section(spans, number)
        if section is None:
            failures.append(
                f"line {number}: the date {found[0]} sits under no section of "
                f"level 2 or deeper, so it can carry no source"
            )
        elif not section_cites_a_source(section[3]):
            failures.append(
                f'line {number}: the date {found[0]} sits in "{section[2]}", '
                f"which links to no source; cite the page that states it"
            )
        else:
            sourced += len(found)

        tokens = inline_code_tokens(block)
        transcribed = [token for token in tokens if token in SOURCE_RETIREMENT_DATES]
        allowed = {SOURCE_RETIREMENT_DATES[token] for token in transcribed}
        for value in found:
            if value in allowed:
                continue
            if transcribed:
                failures.append(
                    f"line {number}: no transcribed source row gives "
                    f"{value} for {' or '.join(sorted(transcribed))}; the "
                    f"rows this script holds give "
                    f"{', '.join(sorted(allowed))}"
                )
            else:
                failures.append(
                    f"line {number}: the date {value} belongs to no model "
                    f"this block names, so no source row backs it; name the "
                    f"model and add its row to SOURCE_RETIREMENT_DATES"
                )

        if PAST_RETIREMENT_RE.search(strip_inline_code(text)):
            versioned = [
                token
                for token in tokens
                if MODEL_TOKEN_RE.fullmatch(token)
                and VERSIONED_MODEL_RE.match(token)
            ]
            if not versioned:
                failures.append(
                    f"line {number}: the retirement dated {found[0]} names no "
                    f"versioned model identifier such as `gemini-1.5-pro-001`, "
                    f"so no row of a source table can confirm it"
                )
            for token in transcribed:
                replacement = SOURCE_REPLACEMENTS.get(token)
                if replacement and replacement not in tokens:
                    failures.append(
                        f"line {number}: the block dates the retirement of "
                        f"`{token}` but never names `{replacement}`, the "
                        f"upgrade the same row recommends"
                    )
            for value in found:
                try:
                    when = datetime.datetime.strptime(value, "%B %d, %Y").date()
                except ValueError:
                    failures.append(f"line {number}: {value} is not a real date")
                    continue
                if when > today:
                    failures.append(
                        f"line {number}: the block puts a retirement in the "
                        f"past, but {value} has not arrived yet"
                    )

    results.add(
        "dates",
        failures,
        f"{dates} dated claims checked against {len(SOURCE_RETIREMENT_DATES)} "
        f"transcribed source rows, {sourced} in a section that cites a source",
    )



def check_counts(readme: Readme, results: Results) -> None:
    """Check the counted claims against the code that produces them."""
    failures: list[str] = []
    categories, entries, distinct = home_page_counts()
    demos = len(top_level_app_files())
    expectations = [
        (rf"(?:contains|holds|includes|provides|offers|ships)\s+{NUMBER_RE}\s+(?:\w+\s+){{0,3}}?demos\b",
         demos, "demo files directly under apps/"),
        (rf"{NUMBER_RE}\s+demo files\b", demos, "demo files directly under apps/"),
        (rf"{NUMBER_RE}\s+categories\b", categories, "categories in home.py"),
        (rf"{NUMBER_RE}\s+entries\b", entries, "sidebar entries in home.py"),
    ]
    checked = 0
    for start, block in prose_blocks(readme):
        text = strip_links(strip_inline_code(block))
        for pattern, expected, what in expectations:
            for match in re.finditer(pattern, text, re.I):
                value = parse_number(match.group(1))
                if value is None:
                    continue
                checked += 1
                if value != expected:
                    failures.append(
                        f'line {start}: "{match.group(0).strip()}", but the repository has '
                        f"{expected} {what}"
                    )
    if distinct and demos and distinct != demos:
        failures.append(
            f"home.py links {distinct} distinct demo files but apps/ holds {demos}; "
            f"the counted claims in the README cannot all be right"
        )
    results.add(
        "counts",
        failures,
        f"{checked} counted claims checked against home.py and apps/",
    )


def check_ui_labels(readme: Readme, results: Results) -> None:
    """Every bold UI label must exist as a string in the Streamlit source."""
    failures: list[str] = []
    sources = [REPO / "home.py"] + sorted((REPO / "apps").rglob("*.py"))
    text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in sources
        if path.is_file() and not any(part in SKIP_DIRS for part in path.parts)
    )
    checked = 0
    for start, block in prose_blocks(readme):
        lowered = block.lower()
        if not any(word in lowered for word in UI_CONTEXT_WORDS):
            continue
        for match in BOLD_RE.finditer(block):
            label = match.group(1).strip()
            if label.endswith((".", ":", "!", "?")) or len(label.split()) > 5:
                continue
            checked += 1
            if label not in text:
                failures.append(
                    f"line {start}: the README shows the interface element **{label}**, "
                    f"which no string in home.py or apps/ matches"
                )
    results.add("ui_labels", failures, f"{checked} interface labels checked against the source")


def check_demo_labels(readme: Readme, results: Results) -> None:
    """The demo table must name each demo the way its sidebar button does.

    A paraphrase reads well and helps nobody: a reader scanning the sidebar
    for "WCAG accessibility analyzer" finds a button that says "Accessibility
    with Gemini". The comparison runs in both directions, so a label that
    home.py drops cannot linger in the table either.
    """
    failures: list[str] = []
    demos = home_page_demos()

    rows: dict[str, str] = {}
    for line in readme.section("Available demos"):
        match = re.match(r"^\|\s*\*\*(.+?)\*\*\s*\|\s*`(apps/[\w./-]+\.py)`\s*\|", line)
        if match:
            rows[match.group(2)] = match.group(1).strip()

    for path in sorted(set(demos) | set(rows)):
        labels = demos.get(path, set())
        documented = rows.get(path)
        if documented is None:
            joined = " or ".join(sorted(f'"{label}"' for label in labels))
            failures.append(
                f"home.py opens {path} with the sidebar button {joined}, "
                f"which the demo table does not list"
            )
        elif not labels:
            failures.append(
                f'the demo table lists {path} as "{documented}", '
                f"but home.py has no sidebar button for that file"
            )
        elif documented not in labels:
            joined = " or ".join(sorted(f'"{label}"' for label in labels))
            failures.append(
                f'the demo table calls {path} "{documented}", '
                f"but its sidebar button in home.py says {joined}"
            )
        elif labels != {documented}:
            # home.py may list one demo twice, as the Others category does, but
            # only under the same label. A second, different label is a demo
            # the table silently hides.
            joined = ", ".join(sorted(f'"{label}"' for label in labels - {documented}))
            failures.append(
                f"home.py also opens {path} from the sidebar button {joined}, "
                f"which the demo table does not list"
            )

    results.add(
        "demo_labels",
        failures,
        f"{len(rows)} demo table rows matched against {len(demos)} demos in home.py",
    )


def check_ports(readme: Readme, results: Results) -> None:
    failures: list[str] = []
    configured = repo_ports()
    found: dict[str, int] = {}
    for pattern in (r"localhost:(\d+)", r"\bport\s+(\d+)", r"--server\.port=(\d+)"):
        for match in re.finditer(pattern, readme.text, re.I):
            found[match.group(1)] = found.get(match.group(1), 0) + 1
    for first, second in re.findall(r"-p\s+(\d+):(\d+)", readme.text):
        found[first] = found.get(first, 0) + 1
        found[second] = found.get(second, 0) + 1
    if not configured:
        failures.append("the repository configures no port, so the README cannot be checked")
    for port in sorted(found):
        if port not in configured:
            failures.append(
                f"the README mentions port {port}, but the repository configures "
                f"{', '.join(sorted(configured)) or 'no port'}"
            )
    results.add(
        "ports",
        failures,
        f"{len(found)} distinct ports in the README, configured={','.join(sorted(configured)) or 'none'}",
    )


def check_python_version(readme: Readme, results: Results) -> None:
    failures: list[str] = []
    expected = dockerfile_python_version()
    mentions = set(re.findall(r"\bPython\s+(\d+(?:\.\d+)+)", readme.text))
    if expected is None:
        failures.append("the Dockerfile declares no python base image")
    for version in sorted(mentions):
        if version != expected:
            failures.append(
                f"the README asks for Python {version}, but the Dockerfile builds on "
                f"python:{expected}"
            )
    results.add(
        "python_version",
        failures,
        f"Dockerfile python:{expected or '?'}, {len(mentions)} version mentions in the README",
    )


def check_ignore_files(readme: Readme, results: Results) -> None:
    """Every pattern the README attributes to an ignore file must be in one.

    The check is one-directional on purpose: it verifies the patterns the README
    claims are excluded. A claim that something is *not* excluded is a negative
    over an open set and stays a matter for review.
    """
    failures: list[str] = []
    patterns = ignore_file_patterns()
    checked = 0
    for start, block in prose_blocks(readme):
        named = [name for name in IGNORE_FILES if name in block]
        if not named:
            continue
        for token in inline_code_tokens(block):
            if token in IGNORE_FILES:
                continue
            if not ("*" in token or token.startswith(".") or token.endswith((".json", ".pem", ".key"))):
                continue
            checked += 1
            if not any(token in patterns.get(name, set()) for name in named):
                failures.append(
                    f"line {start}: the README says {' or '.join(named)} excludes `{token}`, "
                    f"but no named ignore file lists that pattern"
                )
    results.add("ignore_files", failures, f"{checked} ignore patterns checked against {len(patterns)} files")


def section_spans(readme: Readme) -> list[tuple[int, int, str, list[str]]]:
    """Return (line number, level, title, body) for every heading.

    The body runs to the next heading of the same or a higher level and keeps
    fenced code blocks, which ``Readme.section`` drops. A level-1 title
    therefore owns the whole document, so callers that want only the
    introduction slice to the next heading of any level themselves.
    """
    heads = readme.headings()
    spans: list[tuple[int, int, str, list[str]]] = []
    for index, (number, level, title) in enumerate(heads):
        end = len(readme.lines)
        for later_number, later_level, _ in heads[index + 1:]:
            if later_level <= level:
                end = later_number - 1
                break
        spans.append((number, level, title, readme.lines[number:end]))
    return spans


def body_evidence(body: list[str]) -> tuple[int, int, int]:
    """Count prose lines, fenced code blocks, and tables in a section body."""
    prose_lines = 0
    fences = 0
    tables = 0
    in_fence = False
    for line in body:
        if re.match(r"^\s*```", line):
            in_fence = not in_fence
            if in_fence:
                fences += 1
            continue
        if in_fence:
            continue
        stripped = line.strip()
        if not stripped or HEADING_RE.match(line):
            continue
        # A table delimiter row: | --- | :--- | ---: |
        if re.match(r"^\|[\s:|-]+\|$", stripped) and "-" in stripped:
            tables += 1
            continue
        prose_lines += 1
    return prose_lines, fences, tables


def check_structure(readme: Readme, results: Results) -> None:
    """Require the sections a reader needs, not only accurate ones.

    Every other check here validates what the README says. None of them
    notices what it stopped saying. Deleting the whole troubleshooting section
    leaves the rest of the run green, which makes silence the cheapest way to
    pass. This check closes that gap.
    """
    failures: list[str] = []
    spans = section_spans(readme)
    heads = readme.headings()

    titles = [(number, title) for number, level, title, _ in spans if level == 1]
    if not titles:
        failures.append("the README has no level-1 title")
    elif len(titles) > 1:
        joined = ", ".join(f'line {number} "{title}"' for number, title in titles)
        failures.append(
            f"the README has {len(titles)} level-1 titles, expected 1: {joined}"
        )
    elif heads[0][1] != 1:
        failures.append(
            f'line {heads[0][0]}: the README opens with "{heads[0][2]}" at level '
            f"{heads[0][1]}; the level-1 title must come first"
        )

    # A skipped level (## followed by ####) breaks the outline for a screen
    # reader and for every tool that builds a table of contents. The required
    # subsections below deliberately have no fixed level, so this generic rule
    # is what stops one of them from being demoted out of its parent.
    previous = 0
    for number, level, title in heads:
        if previous and level > previous + 1:
            failures.append(
                f'line {number}: "{title}" is a level-{level} heading directly '
                f"under a level-{previous} heading; do not skip heading levels"
            )
        previous = level

    # The title needs an introduction before the first section heading.
    if heads and heads[0][1] == 1:
        end = heads[1][0] - 1 if len(heads) > 1 else len(readme.lines)
        intro = " ".join(
            line
            for line in readme.lines[heads[0][0]:end]
            if not line.lstrip().startswith(("![", "|", "```", "<!--"))
        )
        words = len(re.findall(r"[A-Za-z][\w'-]*", intro))
        if words < MIN_INTRO_WORDS:
            failures.append(
                f"the introduction under the title holds {words} words, "
                f"expected at least {MIN_INTRO_WORDS}"
            )

    required = [(title, kind, 2) for title, kind in REQUIRED_SECTIONS]
    required += [(title, kind, None) for title, kind in REQUIRED_SUBSECTIONS]

    for title, kind, want_level in required:
        matches = [span for span in spans if title.lower() in span[2].lower()]
        if not matches:
            failures.append(f'the README has no "{title}" section')
            continue
        if len(matches) > 1:
            where = ", ".join(f"line {span[0]}" for span in matches)
            failures.append(
                f'{len(matches)} headings contain "{title}" ({where}); the check '
                f"cannot tell which one is authoritative"
            )
            continue

        number, level, heading, body = matches[0]
        if want_level is not None and level != want_level:
            failures.append(
                f'line {number}: "{heading}" is a level-{level} heading, '
                f"expected level {want_level}"
            )
        prose_lines, fences, tables = body_evidence(body)
        if prose_lines < MIN_SECTION_PROSE_LINES:
            failures.append(
                f'line {number}: "{heading}" holds {prose_lines} lines of prose, '
                f"expected at least {MIN_SECTION_PROSE_LINES}"
            )
        if kind == "commands" and fences == 0:
            failures.append(
                f'line {number}: "{heading}" has no fenced code block, so it '
                f"tells the reader what to do without showing the command"
            )
        if kind == "table" and tables == 0:
            failures.append(f'line {number}: "{heading}" has no table')

    # check_apps accepts a demo file mentioned anywhere in the README. The
    # table is what a reader actually reads, so hold it to the same coverage.
    demo_sections = [span for span in spans if "available demos" in span[2].lower()]
    demos_on_disk = {path for path in app_files() if path.count("/") == 1}
    if len(demo_sections) == 1:
        listed = set(re.findall(r"apps/[\w./-]+\.py", "\n".join(demo_sections[0][3])))
        for path in sorted(demos_on_disk - listed):
            failures.append(
                f'the "Available demos" section does not list {path}'
            )

    results.add(
        "structure",
        failures,
        f"{len(REQUIRED_SECTIONS)} required sections and "
        f"{len(REQUIRED_SUBSECTIONS)} required subsections checked, "
        f"{len(demos_on_disk)} demos expected in the demo table",
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    if len(sys.argv) > 1:
        print("check_readme.py takes no arguments", file=sys.stderr)
        return 2
    if not README_PATH.exists():
        print(f"error: {README_PATH} not found", file=sys.stderr)
        return 2

    readme = Readme(README_PATH.read_text(encoding="utf-8"))
    results = Results()

    print(f"Verifying {README_PATH} against {REPO}")
    print()

    check_structure(readme, results)
    check_paths(readme, results)
    check_links(readme, results)
    check_apps(readme, results)
    check_counts(readme, results)
    check_env_vars(readme, results)
    check_packages(readme, results)
    check_import_claims(readme, results)
    check_models(readme, results)
    check_dates(readme, results)
    check_clone_url(readme, results)
    check_cloudbuild(readme, results)
    check_docker(readme, results)
    check_ports(readme, results)
    check_python_version(readme, results)
    check_setup_script(readme, results)
    check_placeholders(readme, results)
    check_ignore_files(readme, results)
    check_ui_labels(readme, results)
    check_demo_labels(readme, results)
    check_license(readme, results)
    check_headings(readme, results)
    check_banned_words(readme, results)
    check_voice(readme, results)
    check_lists(readme, results)
    check_code_fences(readme, results)
    check_language(readme, results)

    return results.report()


if __name__ == "__main__":
    sys.exit(main())
