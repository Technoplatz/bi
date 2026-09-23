#!/usr/bin/env python3
"""
Reports component fields that a template reads although they are plain, mutable fields (not signals).
In zoneless mode such a field changes without the view noticing. A field counts as mutable when the
controller assigns or mutates it after its declaration; constants (environment values, arrays that are
never written) are ignored.

Usage: tools/check-signals.py [src/app]     exit code 1 when something is reported
"""
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "src/app")
CONTEXTS = [
    re.compile(r"\{\{(.*?)\}\}", re.S),
    re.compile(r"@(?:if|else if|for|switch|case)\s*\((.*?)\)\s*\{", re.S),
    re.compile(r"(?<=[\[\(\*])[\w.\-\(\)]+\]?\)?=\"(.*?)\"", re.S),
]
SIGNAL_INIT = re.compile(r"=\s*(signal|computed|input|model|output|toSignal|viewChild|viewChildren|contentChild|contentChildren|linkedSignal|inject)\b")
FIELD = re.compile(r"^\s{2}(?:public\s+|private\s+|protected\s+)?(?:readonly\s+)?([A-Za-z_$][\w$]*)\s*(?:\?|!)?\s*(?::[^=;\n]+)?\s*(=[^=]|;)", re.M)


def template_of(ts_path, ts):
    html = ts_path.with_suffix(".html")
    if html.exists():
        return html.read_text()
    m = re.search(r"template:\s*`(.*?)`", ts, re.S)
    return m.group(1) if m else ""


def main():
    problems = 0
    for ts_path in sorted(ROOT.rglob("*.ts")):
        if ts_path.name.endswith(".spec.ts") or "@Component" not in ts_path.read_text():
            continue
        ts = ts_path.read_text()
        html = template_of(ts_path, ts)
        if not html:
            continue
        body = ts[ts.index("@Component"):]
        body = re.sub(r"//[^\n]*", "", body)  # writes inside comments do not count
        plain = []
        for m in FIELD.finditer(body):
            name = m.group(1)
            line = body[m.start():body.find("\n", m.start())]
            if SIGNAL_INIT.search(line) or name in ("constructor",) or line.strip().startswith(("get ", "set ", "async ", "static ")):
                continue
            if re.search(r"\(\s*[^)]*\)\s*\{", line):  # method
                continue
            if re.search(r":\s*(Untyped)?Form(Group|Array|Control)\b", line):  # reactive forms are built once
                continue
            writes = re.search(r"this\.%s\s*(=[^=]|\+\+|--|\+=|-=|\.(push|pop|shift|unshift|splice|sort|reverse|fill)\(|\[[^\]]*\]\s*=[^=]|\.[A-Za-z_]\w*\s*=[^=])" % re.escape(name), body)
            if not writes:
                continue
            plain.append(name)
        if not plain:
            continue
        alt = "|".join(re.escape(n) for n in plain)
        read = re.compile(r"(?<![\w.$'\"#])(%s)\b(?!\s*\(|\s*:)" % alt)  # not a call, not an object key
        hits = {}
        for ctx in CONTEXTS:
            for m in ctx.finditer(html):
                expression = re.sub(r"'[^']*'", "''", m.group(1))  # words inside string literals are not reads
                for r in read.finditer(expression):
                    hits.setdefault(r.group(1), 0)
                    hits[r.group(1)] += 1
        for name, count in sorted(hits.items()):
            problems += 1
            print(f"{ts_path}: plain mutable field '{name}' is read {count}x in the template")
    if problems:
        print(f"{problems} field(s) should be signals")
        sys.exit(1)
    print("no plain mutable fields are read by templates")


if __name__ == "__main__":
    main()
