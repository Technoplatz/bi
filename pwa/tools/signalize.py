#!/usr/bin/env python3
"""
Turns plain component fields into Angular signals: the declaration becomes `readonly name = signal(...)`,
`this.name = expr` becomes `this.name.set(expr)`, other reads become `this.name()`, and reads in the
component template (same base name, .html) become `name()` inside bindings, interpolations and control
flow blocks. Writes that mutate in place (push, splice, index assignment, ++, +=) are only reported,
they need `update()` with a new array or object by hand, as do two-way [(ngModel)] bindings.

Usage: tools/signalize.py src/app/pages/x/x.page.ts field1 field2 ... [--dry]
"""
import re
import sys
from pathlib import Path

MUTATIONS = re.compile(r"this\.(%s)\s*(\+\+|--|\+=|-=|\*=|\[[^\]]*\]\s*=[^=]|\.(push|pop|shift|unshift|splice|sort|reverse|length\s*=|fill|copyWithin)\b)")


def find_statement_end(text, start):
    """index just after the `;` that ends the statement starting at `start`, honouring brackets and strings"""
    depth = 0
    i = start
    quote = None
    while i < len(text):
        ch = text[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = None
            elif quote == "`" and ch == "$" and text[i + 1:i + 2] == "{":
                depth += 1
        elif ch in "\"'`":
            quote = ch
        elif ch in "([{":
            depth += 1
        elif ch in ")]}":
            if depth == 0:
                return i
            depth -= 1
        elif ch == ";" and depth == 0:
            return i + 1
        elif ch == "\n" and depth == 0 and text[start:i].strip() and not text[start:i].rstrip().endswith((",", "+", "-", "?", ":", "&&", "||", "=", "(")):
            # statement without semicolon
            return i
        i += 1
    return len(text)


def convert_ts(ts, names):
    report = []
    for name in names:
        # declaration
        decl = re.compile(r"^(\s*)(?:public\s+|private\s+|protected\s+)?(?:readonly\s+)?%s\b(\??)(?:\s*:\s*([^=;\n]+?))?\s*(=|;)" % re.escape(name), re.M)
        m = decl.search(ts)
        if not m:
            report.append(f"{name}: no field declaration found")
        else:
            indent = m.group(1)
            typ = (m.group(3) or "").strip()
            if m.group(4) == "=":
                rest_start = m.end()
                end = find_statement_end(ts, rest_start)
                init = ts[rest_start:end].strip().rstrip(";").strip()
            else:
                end = m.end()
                init = "undefined"
                if not typ:
                    typ = "any"
            generic = f"<{typ}>" if typ else ""
            ts = ts[:m.start()] + f"{indent}readonly {name} = signal{generic}({init});" + ts[end:]
        # in-place mutations are reported, not converted
        for mm in MUTATIONS.finditer(ts):
            if mm.group(1) == name:
                line = ts.count("\n", 0, mm.start()) + 1
                report.append(f"{name}: in-place mutation at line {line}: {ts[mm.start():mm.start() + 60].splitlines()[0]}")
        # assignments -> set()
        pattern = re.compile(r"this\.%s\s*=(?!=)\s*" % re.escape(name))
        pos = 0
        while True:
            m = pattern.search(ts, pos)
            if not m:
                break
            end = find_statement_end(ts, m.end())
            expr = ts[m.end():end].strip().rstrip(";").strip()
            replacement = f"this.{name}.set({expr});"
            ts = ts[:m.start()] + replacement + ts[end:]
            pos = m.start() + len(replacement)
        # remaining reads -> call
        ts = re.sub(r"this\.%s\b(?!\s*[\(=]|\.set\(|\.update\()" % re.escape(name), f"this.{name}()", ts)
    # import
    core = re.search(r'import \{([^}]*)\} from ["\']@angular/core["\'];', ts)
    if core:
        parts = [p.strip() for p in core.group(1).split(",") if p.strip()]
        if "signal" not in parts:
            parts.append("signal")
            ts = ts[:core.start()] + "import { " + ", ".join(parts) + ' } from "@angular/core";' + ts[core.end():]
    else:
        ts = 'import { signal } from "@angular/core";\n' + ts
    return ts, report


CONTEXTS = [
    re.compile(r"\{\{(.*?)\}\}", re.S),                                  # interpolation
    re.compile(r"@(?:if|else if|for|switch|case)\s*\((.*?)\)\s*\{", re.S),  # control flow heads
    re.compile(r"(?<=[\[\(\*])[\w.\-\(\)]+\]?\)?=\"(.*?)\"", re.S),      # [prop]="", (event)="", *dir=""
]


def convert_html(html, names):
    report = []
    alt = "|".join(re.escape(n) for n in names)
    read = re.compile(r"(?<![\w.$'\"#])(%s)\b(?!\s*\(|\s*:)" % alt)
    for m in re.finditer(r'\[\(ngModel\)\]="([^"]*)"', html):
        if re.search(r"\b(%s)\b" % alt, m.group(1)):
            report.append(f"two-way binding needs [ngModel]/(ngModelChange) by hand: {m.group(0)}")

    def in_context(m):
        inner = read.sub(lambda r: r.group(1) + "()", m.group(1))
        return m.group(0)[:m.start(1) - m.start(0)] + inner + m.group(0)[m.end(1) - m.start(0):]

    for ctx in CONTEXTS:
        html = ctx.sub(in_context, html)
    return html, report


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry" in sys.argv
    ts_path = Path(args[0])
    names = args[1:]
    ts, report = convert_ts(ts_path.read_text(), names)
    html_path = ts_path.with_suffix(".html")
    html = None
    if html_path.exists():
        html, r2 = convert_html(html_path.read_text(), names)
        report += r2
    if not dry:
        ts_path.write_text(ts)
        if html is not None:
            html_path.write_text(html)
    for line in report:
        print("NOTE", line)
    print(f"{'would convert' if dry else 'converted'} {len(names)} fields in {ts_path.name}" + (f" and {html_path.name}" if html is not None else ""))


if __name__ == "__main__":
    main()
