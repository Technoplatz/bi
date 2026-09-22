#!/usr/bin/env python3
"""
Ports a page or component from the old NgModule-based pwa into the standalone pwa-next workspace.

The template and styles are copied (license comment stripped); the controller keeps its logic and
gets a standalone @Component decorator with the imports derived from the template: Ionic
components by tag, the shared components by selector, the translate and sort pipes, forms modules
and the common module for the legacy structural directives.

Usage: tools/port-page.py pages/collection components/kov ...
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / "pwa" / "src" / "app"
NEW = ROOT / "pwa-next" / "src" / "app"

SELECTOR_TO_COMPONENT = {
    "app-inner-footer": ("InnerFooterComponent", "components/inner-footer/inner-footer.component"),
    "app-footer": ("FooterComponent", "components/footer/footer.component"),
    "app-lang": ("LangComponent", "components/lang/lang.component"),
    "app-pagination": ("PaginationComponent", "components/pagination/pagination.component"),
    "app-kov": ("KovComponent", "components/kov/kov.component"),
    "app-chart": ("ChartComponent", "components/chart/chart.component"),
    "app-menu": ("MenuComponent", "components/menu/menu.component"),
    "app-tools": ("ToolsComponent", "components/tools/tools.component"),
    "modal-footer": ("ModalFooterComponent", "components/modal-footer/modal-footer.component"),
    "json-editor": ("JsonEditorComponent", "components/json-editor/json-editor.component"),
    "qrcode": ("QRCodeComponent", "angularx-qrcode"),
}
HEADER = "/*\nTechnoplatz BI\n\nCopyright ©Technoplatz IT Solutions GmbH, Mustafa Mat\n\nThis program is free software: you can redistribute it and/or modify\nit under the terms of the GNU Affero General Public License as published by\nthe Free Software Foundation, either version 3 of the License, or\nany later version.\n\nThis program is distributed in the hope that it will be useful,\nbut WITHOUT ANY WARRANTY; without even the implied warranty of\nMERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\nGNU Affero General Public License for more details.\n\nYou should have received a copy of the GNU Affero General Public License\nalong with this program.  If not, see https://www.gnu.org/licenses.\n*/\n\n"


def pascal(tag):
    return "".join(part.capitalize() for part in tag.split("-"))


def rel(from_dir, module_path):
    if not module_path.startswith("components/") and not module_path.startswith("pages/"):
        return module_path
    depth = len(Path(from_dir).parts)
    return "../" * depth + module_path


def port(unit):
    kind, name = unit.split("/")
    suffix = "page" if kind == "pages" else "component"
    src_dir = OLD / kind / name
    dst_dir = NEW / kind / name
    dst_dir.mkdir(parents=True, exist_ok=True)
    base = f"{name}.{suffix}"
    html = (src_dir / f"{base}.html").read_text()
    html = re.sub(r"^<!--.*?-->\s*", "", html, count=1, flags=re.S)
    (dst_dir / f"{base}.html").write_text(html)
    scss_src = src_dir / f"{base}.scss"
    (dst_dir / f"{base}.scss").write_text(scss_src.read_text() if scss_src.exists() else "")

    ts = (src_dir / f"{base}.ts").read_text()
    ts = re.sub(r"^/\*.*?\*/\s*", "", ts, count=1, flags=re.S)
    ts = ts.replace('from "@ionic/storage"', 'from "@ionic/storage-angular"')
    ts = ts.replace('from "ang-jsoneditor"', f'from "{rel(unit, "components/json-editor/json-editor.component")}"')
    ts = re.sub(r'editor: any = new JsonEditorComponent\(\);', "editor?: JsonEditorComponent;", ts)
    ts = re.sub(r'styleUrls: \[(["\'])([^"\']+)\1\],?', r'styleUrl: \1\2\1', ts)

    imports = ["CommonModule"]
    import_lines = ['import { CommonModule } from "@angular/common";']
    if "ngModel" in html:
        imports.append("FormsModule")
    if "formGroup" in html or "formControlName" in html:
        imports.append("ReactiveFormsModule")
    forms = [i for i in imports if i in ("FormsModule", "ReactiveFormsModule")]
    if forms:
        import_lines.append(f'import {{ {", ".join(forms)} }} from "@angular/forms";')
    if re.search(r"\|\s*translate", html):
        imports.append("TranslatePipe")
        import_lines.append('import { TranslatePipe } from "@ngx-translate/core";')
    if re.search(r"\|\s*sort\b", html):
        imports.append("ArraySortPipe")
        import_lines.append(f'import {{ ArraySortPipe }} from "{rel(unit, "pipes/array-sort.pipe")}";')
    ion_tags = sorted(set(re.findall(r"<(ion-[a-z-]+)", html)))
    ion_components = [pascal(t) for t in ion_tags]
    if ion_components:
        imports += ion_components
        existing = re.search(r'import \{([^}]*)\} from "@ionic/angular";', ts)
        if existing:
            names = [n.strip() for n in existing.group(1).split(",") if n.strip()]
            ts = ts[:existing.start()] + 'import { ' + ", ".join(sorted(set(names + ion_components))) + ' } from "@ionic/angular";' + ts[existing.end():]
        else:
            import_lines.append(f'import {{ {", ".join(ion_components)} }} from "@ionic/angular";')
    if re.search(r"<ngx-charts-", html):
        imports.append("NgxChartsModule")
        import_lines.append('import { NgxChartsModule } from "@swimlane/ngx-charts";')
    for selector, (cls, path) in SELECTOR_TO_COMPONENT.items():
        if re.search(rf"<{selector}[\s>]", html) and cls not in ts.split("@Component")[0]:
            imports.append(cls)
            import_lines.append(f'import {{ {cls} }} from "{rel(unit, path)}";')
    if "JsonEditorComponent" in ts and "JsonEditorComponent" not in imports and "<json-editor" in html:
        imports.append("JsonEditorComponent")

    decorator = re.search(r"@Component\(\{\n", ts)
    assert decorator, f"no @Component in {unit}"
    injected = ("  // ported code updates plain fields in promise callbacks; angular 22 components are OnPush by default\n"
                "  changeDetection: ChangeDetectionStrategy.Eager,\n"
                f"  imports: [{', '.join(imports)}],\n")
    ts = ts[:decorator.end()] + injected + ts[decorator.end():]
    core = re.search(r'import \{([^}]*)\} from "@angular/core";', ts)
    names = [n.strip() for n in core.group(1).split(",") if n.strip()]
    if "ChangeDetectionStrategy" not in names:
        names.append("ChangeDetectionStrategy")
    ts = ts[:core.start()] + 'import { ' + ", ".join(names) + ' } from "@angular/core";' + ts[core.end():]
    first_import = ts.index("import ")
    ts = ts[:first_import] + "\n".join(import_lines) + "\n" + ts[first_import:]
    (dst_dir / f"{base}.ts").write_text(HEADER + ts.lstrip())
    print(f"ported {unit}: imports={len(imports)} ion={len(ion_components)}")


if __name__ == "__main__":
    for unit in sys.argv[1:]:
        port(unit)
