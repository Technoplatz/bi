import { Component, OnInit, inject, signal } from "@angular/core";
import {
  IonButton,
  IonCol,
  IonContent,
  IonGrid,
  IonHeader,
  IonIcon,
  IonRow,
  IonToolbar,
} from '@ionic/angular';
import { Storage } from '@ionic/storage-angular';
import { TranslatePipe } from '@ngx-translate/core';
import { Miscellaneous } from '../../classes/misc';
import { FooterComponent } from '../../components/footer/footer.component';
import { LangComponent } from '../../components/lang/lang.component';

@Component({
  selector: 'app-home',
  imports: [
    IonHeader,
    IonToolbar,
    IonGrid,
    IonRow,
    IonCol,
    IonContent,
    IonIcon,
    IonButton,
    TranslatePipe,
    FooterComponent,
    LangComponent,
  ],
  templateUrl: './home.page.html',
  styleUrl: './home.page.scss',
})
export class HomePage implements OnInit {
  misc = inject(Miscellaneous);
  private storage = inject(Storage);

  readonly user = signal<any>(undefined);

  ngOnInit() {
    this.storage.get('LSUSERMETA').then((LSUSERMETA: any) => {
      this.user.set(LSUSERMETA ? LSUSERMETA : null);
    });
  }
}
