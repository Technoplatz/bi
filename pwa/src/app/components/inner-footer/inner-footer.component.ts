import { Component, inject } from '@angular/core';
import { IonFooter } from '@ionic/angular';
import { TranslatePipe } from '@ngx-translate/core';
import { Miscellaneous } from '../../classes/misc';
import { LangComponent } from '../lang/lang.component';

@Component({
  selector: 'app-inner-footer',
  imports: [IonFooter, TranslatePipe, LangComponent],
  templateUrl: './inner-footer.component.html',
  styleUrl: './inner-footer.component.scss',
})
export class InnerFooterComponent {
  misc = inject(Miscellaneous);
}
