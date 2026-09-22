/*
Technoplatz BI

Copyright ©Technoplatz IT Solutions GmbH, Mustafa Mat

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see https://www.gnu.org/licenses.
*/

import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, EventEmitter, Input, OnChanges, OnDestroy, Output, SimpleChanges, ViewChild } from "@angular/core";
import { createJSONEditor, Mode } from "vanilla-jsoneditor";
import { EditorView } from "@codemirror/view";

/**
 * Options object with the same shape the pages used with the previous editor library,
 * so their configuration code stays unchanged.
 */
export class JsonEditorOptions {
  public modes: string[] = ["tree", "code", "text"];
  public mode = "code";
  public statusBar = false;
  public navigationBar = false;
  public mainMenuBar = true;
  public enableSort = false;
  public expandAll = false;
}

/**
 * Replacement for the ang-jsoneditor component on top of vanilla-jsoneditor.
 * Emits the parsed document on every valid change; invalid text is not emitted.
 */
@Component({
  changeDetection: ChangeDetectionStrategy.Eager,
  selector: "json-editor",
  template: `<div #host class="json-editor-host"></div>`,
  styles: [`:host { display: block; } .json-editor-host { height: 100%; }`]
})
export class JsonEditorComponent implements AfterViewInit, OnChanges, OnDestroy {
  @Input() options: JsonEditorOptions = new JsonEditorOptions();
  @Input() data: any = null;
  @Output() change = new EventEmitter<any>();
  @ViewChild("host", { static: true }) host!: ElementRef<HTMLDivElement>;
  private editor: any = null;
  private lastEmitted: string | null = null;
  private observer: MutationObserver | null = null;

  ngAfterViewInit() {
    // CodeMirror mounts its stylesheet into the nearest shadow root the editor is slotted into, here
    // an Ionic layout component, where it cannot style the light DOM editor. Re-root every text
    // mode editor to the document; the observer catches the ones created on a mode switch.
    const reroot = () => {
      const dom = this.host.nativeElement.querySelector(".cm-editor") as HTMLElement | null;
      const view = dom && EditorView.findFromDOM(dom);
      if (view && view.root !== document) {
        view.setRoot(document);
      }
    };
    this.observer = new MutationObserver(reroot);
    this.observer.observe(this.host.nativeElement, { childList: true, subtree: true });
    this.editor = createJSONEditor({
      target: this.host.nativeElement,
      props: {
        content: { json: this.data ?? [] },
        mode: this.options?.mode === "tree" ? Mode.tree : Mode.text,
        mainMenuBar: this.options?.mainMenuBar ?? true,
        navigationBar: this.options?.navigationBar ?? false,
        statusBar: this.options?.statusBar ?? false,
        onChange: (content: any, _previous: any, status: any) => {
          if (status?.contentErrors) {
            return;
          }
          try {
            const value = "json" in content ? content.json : JSON.parse(content.text);
            const serialized = JSON.stringify(value);
            if (serialized !== this.lastEmitted) {
              this.lastEmitted = serialized;
              this.change.emit(value);
            }
          } catch {
            // incomplete text while typing
          }
        }
      }
    });
  }

  ngOnChanges(changes: SimpleChanges) {
    if (this.editor && changes["data"] && !changes["data"].firstChange) {
      const serialized = JSON.stringify(this.data ?? []);
      if (serialized !== this.lastEmitted) {
        this.lastEmitted = serialized;
        this.editor.set({ json: this.data ?? [] });
      }
    }
    if (this.editor && changes["options"] && !changes["options"].firstChange) {
      this.editor.updateProps({ mode: this.options?.mode === "tree" ? Mode.tree : Mode.text });
    }
  }

  ngOnDestroy() {
    this.observer?.disconnect();
    this.observer = null;
    this.editor?.destroy();
    this.editor = null;
  }
}
