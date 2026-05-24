"""Merge 01-MT.tex .. 04-SA.tex into one combined.tex that compiles cleanly.

Each source file has its content between its first \\begin{document} and
first \\end{document}; anything after that (German drafts, duplicates) is
ignored. Labels are prefixed per file (mt:, pt:, sp:, sa:) and references
are rewritten to point at the right file.
"""

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "static" / "teaching" / "probability"

FILES = [
    ("mt", "01-MT.tex", "Measure Theory"),
    ("pt", "02-PT.tex", "Probability Theory"),
    ("sp", "03-SP.tex", "Stochastic Processes"),
    ("sa", "04-SA.tex", "Stochastic Analysis"),
]

REF_COMMANDS = r"(?:ref|eqref|autoref|pageref|nameref|hyperref)"

PREAMBLE = r"""\documentclass[11pt, twoside]{article}
\usepackage{a4wide}
\usepackage[utf8]{inputenc}
\usepackage{rotating, color}
\usepackage[nointegrals]{wasysym}
\usepackage[centertags]{amsmath}
\usepackage{amssymb, amsthm, mathtools}
\usepackage{pictexwd}
\usepackage{mathrsfs}
\usepackage{tikz}
\usepackage{xspace}
\usepackage[hidelinks]{hyperref}

\newcommand{\Frechet}{Fr\'echet\xspace}
\newcommand{\Nikodym}{Nikod\'ym\xspace}
\newcommand{\dickm}[1]{\text{\boldmath ${#1}$}}
\newtheorem{proposition}{Proposition}[section]
\newtheorem{theorem}[proposition]{Theorem}
\newtheorem{lemma}[proposition]{Lemma}
\newtheorem{remark}[proposition]{Remark}
\newtheorem{exercise}[proposition]{Exercise}
\newtheorem{example}[proposition]{Example}
\newtheorem{corollary}[proposition]{Corollary}
\newtheorem{definition}[proposition]{Definition}
\numberwithin{equation}{section}
\setcounter{secnumdepth}{2}
\setcounter{tocdepth}{2}

\title{\LARGE Measure Theory, Probability Theory, Stochastic Processes,\\ and Stochastic Analysis}
\author{{\sc Peter Pfaffelhuber}}
\date{Version: \today}
"""


def extract_body(text: str) -> str:
    m = re.search(r"\\begin\{document\}", text)
    if not m:
        raise ValueError("no \\begin{document}")
    after_begin = text[m.end():]
    end_m = re.search(r"(?m)^(?:[^%\n]*?)\\end\{document\}", after_begin)
    if not end_m:
        raise ValueError("no \\end{document}")
    return after_begin[:end_m.start()]


def _drop_balanced(text: str, cmd: str) -> str:
    """Remove every occurrence of \\<cmd>{...} where ... may contain
    one level of nested braces, e.g. \\author{{\\sc Name}}."""
    out, i = [], 0
    needle = f"\\{cmd}{{"
    while True:
        j = text.find(needle, i)
        if j < 0:
            out.append(text[i:])
            return "".join(out)
        out.append(text[i:j])
        # Scan from j + len(needle) for the matching closing brace
        depth = 1
        k = j + len(needle)
        while k < len(text) and depth > 0:
            c = text[k]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            k += 1
        i = k


def strip_decorations(body: str) -> str:
    for cmd in ("title", "author", "date", "part"):
        body = _drop_balanced(body, cmd)
    for p in (
        r"\\maketitle\b",
        r"\\thispagestyle\{empty\}",
        r"\\tableofcontents\b",
        r"\\setcounter\{section\}\{\d+\}",
    ):
        body = re.sub(p, "", body)
    return body


def collect_labels(body: str) -> set[str]:
    return set(re.findall(r"\\label\{([^}]+)\}", body))


def rewrite(body: str, my_prefix: str, label_to_files: dict[str, list[str]]) -> str:
    def label_repl(m):
        return f"\\label{{{my_prefix}:{m.group(1)}}}"
    body = re.sub(r"\\label\{([^}]+)\}", label_repl, body)

    def ref_repl(m):
        cmd, target = m.group(1), m.group(2)
        targets = [t.strip() for t in target.split(",")]
        out_targets = []
        for t in targets:
            files = label_to_files.get(t, [])
            if my_prefix in files:
                out_targets.append(f"{my_prefix}:{t}")
            elif len(files) == 1:
                out_targets.append(f"{files[0]}:{t}")
            else:
                out_targets.append(t)
        return f"\\{cmd}{{{', '.join(out_targets)}}}"
    body = re.sub(rf"\\({REF_COMMANDS})\{{([^}}]+)\}}", ref_repl, body)
    return body


def main() -> None:
    raw = {}
    for prefix, fname, _ in FILES:
        text = (HERE / fname).read_text(encoding="utf-8")
        raw[prefix] = strip_decorations(extract_body(text))

    label_to_files: dict[str, list[str]] = {}
    for prefix, _, _ in FILES:
        for lbl in collect_labels(raw[prefix]):
            label_to_files.setdefault(lbl, []).append(prefix)

    duplicates = {lbl: fs for lbl, fs in label_to_files.items() if len(fs) > 1}
    print(f"Found {len(label_to_files)} unique labels, {len(duplicates)} duplicated across files.")

    parts_text = ["\\begin{document}", "\\maketitle", "\\tableofcontents", "\\newpage"]
    appendices: list[str] = []
    for prefix, _, title in FILES:
        body = rewrite(raw[prefix], prefix, label_to_files)
        # Pull any \begin{appendix}...\end{appendix} blocks out so the
        # alphabetic numbering they trigger only kicks in at the very end.
        appendix_re = re.compile(r"\\begin\{appendix\}.*?\\end\{appendix\}", re.DOTALL)
        for m in appendix_re.finditer(body):
            appendices.append(m.group(0))
        body = appendix_re.sub("", body)
        parts_text.append(f"\n\\part{{{title}}}\n")
        parts_text.append(body.strip())
    if appendices:
        parts_text.append("\n\\part{Appendix}\n")
        parts_text.extend(appendices)
    parts_text.append("\\end{document}\n")

    out = HERE / "combined.tex"
    out.write_text(PREAMBLE + "\n" + "\n\n".join(parts_text), encoding="utf-8")
    print(f"Wrote {out}  ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
