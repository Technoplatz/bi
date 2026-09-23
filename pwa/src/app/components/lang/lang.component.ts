import { Component, computed, inject, signal } from "@angular/core";
import { Miscellaneous } from '../../classes/misc';

@Component({
  selector: 'app-lang',
  template: `
    <div class="flex-container">
      @for (item of langs_(); track item.id) {
        <div [class]="item.class" (click)="do_set_locale(item.id)">{{ item.name }}</div>
      }
    </div>
  `,
  styleUrl: './lang.component.scss',
})
export class LangComponent {
  private misc = inject(Miscellaneous);

  private readonly locale_ = signal<string | null>(null);
  readonly lang_proc_ = signal(false);
  readonly langs_ = computed(() =>
    [
      { id: "en", name: "EN" },
      { id: "de", name: "DE" },
      { id: "tr", name: "TR" }
    ].map((l) => ({ ...l, class: l.id === this.locale_() ? "selection-active" : "selection-passive" }))
  );

  constructor() {
    this.misc.locale().then((LSLOCALE_: any) => this.locale_.set(LSLOCALE_ ?? null));
  }

  do_set_locale(lang_: string) {
    this.lang_proc_.set(true);
    this.misc.set_locale(lang_).then(() => {
      this.locale_.set(lang_);
      setTimeout(() => this.lang_proc_.set(false), 500);
    });
  }
}
