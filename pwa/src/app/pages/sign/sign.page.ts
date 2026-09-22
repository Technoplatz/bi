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

import { Component, HostListener, Input, OnDestroy, OnInit, ViewChild, ChangeDetectionStrategy } from "@angular/core";
import { ReactiveFormsModule, UntypedFormBuilder, UntypedFormGroup, Validators } from "@angular/forms";
import { IonButton, IonCheckbox, IonCol, IonContent, IonGrid, IonIcon, IonInput, IonItem, IonLabel, IonRow, IonSpinner } from "@ionic/angular";
import { Storage } from "@ionic/storage-angular";
import { TranslatePipe } from "@ngx-translate/core";
import { Auth } from "../../classes/auth";
import { Miscellaneous } from "../../classes/misc";

@Component({
  // ported code updates plain fields in promise callbacks; angular 22 components are OnPush by default
  changeDetection: ChangeDetectionStrategy.Eager,
  selector: "app-sign",
  imports: [ReactiveFormsModule, IonContent, IonGrid, IonRow, IonCol, IonItem, IonLabel, IonInput, IonButton, IonSpinner, IonIcon, IonCheckbox, TranslatePipe],
  templateUrl: "./sign.page.html",
  styleUrl: "./sign.page.scss"
})
export class SignPage implements OnInit, OnDestroy {
  @Input() op = "";
  @Input() user: any;
  @ViewChild("emailfocus", { static: false }) emailfocus?: IonInput;
  @ViewChild("emailfocussignin", { static: false }) emailfocussignin?: IonInput;
  @ViewChild("emailfocussignup", { static: false }) emailfocussignup?: IonInput;
  @ViewChild("passwordfocus", { static: false }) passwordfocus?: IonInput;
  @ViewChild("tfacfocus", { static: false }) tfacfocus?: IonInput;

  public error = "";
  public success_str = "";
  public successMessage = "";
  public signupForm: UntypedFormGroup;
  public forgotForm: UntypedFormGroup;
  public signinForm: UntypedFormGroup;
  public resetForm: UntypedFormGroup;
  public TFACForm: UntypedFormGroup;
  public successForm: UntypedFormGroup;
  public formtype = "";
  public isInProgress = false;
  public isRememberMe = false;
  public email = "";
  private focustime = 600;
  private passwordpttrn_ = "(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*_-]).{8,32}";

  @HostListener("document:keydown", ["$event"]) onKey(event: KeyboardEvent) {
    if (event.key !== "Enter") {
      return;
    }
    switch (this.formtype) {
      case "success": this.doAfterSuccess(); break;
      case "signup": this.sign_up(); break;
      case "forgot": this.doForgot(); break;
      case "signin": this.sign_in(); break;
      case "tfac": this.TFAC(); break;
      case "reset": this.Reset(); break;
    }
  }

  constructor(private formBuilder: UntypedFormBuilder, private auth: Auth, private misc: Miscellaneous, private storage: Storage) {
    const password_ = [Validators.required, Validators.minLength(8), Validators.maxLength(32), Validators.pattern(this.passwordpttrn_)];
    const code_ = [Validators.required, Validators.pattern(/^\d{6}$/)];
    this.resetForm = this.formBuilder.group({ password: [null, Validators.compose(password_)], tfac: [null, Validators.compose(code_)] });
    this.TFACForm = this.formBuilder.group({ tfac: [null, Validators.compose(code_)] });
    this.successForm = this.formBuilder.group({});
    this.signinForm = this.formBuilder.group({
      email: [null, Validators.compose([Validators.required, Validators.email, Validators.maxLength(64)])],
      password: [null, Validators.compose(password_)],
      isRememberMe: [this.isRememberMe]
    });
    this.signupForm = this.formBuilder.group({
      name: [null, Validators.compose([Validators.required, Validators.minLength(5), Validators.maxLength(32)])],
      email: [null, Validators.compose([Validators.required, Validators.email, Validators.maxLength(32)])],
      password: [null, Validators.compose(password_)]
    });
    this.forgotForm = this.formBuilder.group({
      email: [null, Validators.compose([Validators.required, Validators.email, Validators.maxLength(64)])]
    });
  }

  ngOnInit() {
    this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
      this.email = LSUSERMETA?.email;
      this.storage.get("LSREMEMBERME").then((LSREMEMBERME: boolean) => {
        this.isRememberMe = !!LSREMEMBERME;
        if (LSREMEMBERME) {
          this.signinForm.get("email")?.setValue(this.email);
        }
        this.signinForm.get("isRememberMe")?.setValue(this.isRememberMe);
        this.doSetOp(this.op);
      });
    });
  }

  ngOnDestroy() {
    this.storage.remove("LSOP").then(() => this.storage.remove("LSFORMTYPE")).catch((error: any) => console.error("storage remove error", error));
  }

  private focus(input?: IonInput) {
    setTimeout(() => input?.setFocus(), this.focustime);
  }

  private touch(form: UntypedFormGroup) {
    Object.values(form.controls).forEach((c) => c.markAsTouched());
  }

  doSetOp(op: string) {
    this.storage.set("LSOP", op).then(() => {
      this.op = op;
      if (op === "signup") {
        this.doSetFormType("signup").then(() => { this.focus(this.emailfocussignup); this.touch(this.signupForm); });
      } else if (op === "signin") {
        this.doSetFormType("signin").then(() => {
          this.focus(this.signinForm.get("email")?.value ? this.passwordfocus : this.emailfocussignin);
          this.touch(this.signinForm);
        });
      } else if (op === "forgot") {
        this.doSetFormType("forgot").then(() => { this.focus(this.emailfocus); this.touch(this.forgotForm); });
      }
    }).catch((error: any) => console.error("storage set op error", error));
  }

  doSetFormType(f: string) {
    return this.storage.set("LSFORMTYPE", f).then(() => {
      this.formtype = f;
      return true;
    });
  }

  doAfterSuccess() {
    this.storage.get("LSOP").then((LSOP: string) => {
      if (["forgot", "signup", "checkout"].includes(LSOP)) {
        this.doSetOp("signin");
      }
    });
  }

  sign_in() {
    this.isInProgress = true;
    this.error = "";
    this.success_str = "";
    if (!(this.signinForm.get("email")?.valid && this.signinForm.get("password")?.valid)) {
      this.isInProgress = false;
      this.signinForm.controls["password"].setValue(null);
      this.error = "invalid credentials";
      return;
    }
    const email_ = this.signinForm.get("email")?.value;
    const remember_ = !!this.signinForm.get("isRememberMe")?.value;
    this.auth.sign_in({ email: email_, password: this.signinForm.get("password")?.value }).then(() => {
      // "remember me" keeps only the address, never the password
      const persist_ = remember_ ? this.storage.set("LSREMEMBERME", true).then(() => this.storage.set("LSUSERMETA", { email: email_ })) : this.storage.remove("LSREMEMBERME");
      persist_.then(() => {
        this.email = email_;
        this.doSetFormType("tfac").then(() => this.focus(this.tfacfocus));
      });
    }).catch(() => {
      this.signinForm.controls["password"].setValue(null);
    }).finally(() => {
      this.isInProgress = false;
    });
  }

  TFAC() {
    this.isInProgress = true;
    this.success_str = "";
    this.auth.TFAC({ email: this.email, password: this.signinForm.get("password")?.value, tfac: this.TFACForm.get("tfac")?.value }).then(() => {
      this.doDismissModal();
    }).catch(() => {
      this.TFACForm.controls["tfac"].setValue(null);
    }).finally(() => {
      this.isInProgress = false;
    });
  }

  Reset() {
    this.isInProgress = true;
    this.success_str = "";
    this.auth.Reset({ email: this.email, password: this.resetForm.get("password")?.value, tfac: this.resetForm.get("tfac")?.value }).then(() => {
      this.success_str = "password has been reset successfully";
      this.formtype = "signin";
    }).catch(() => {
      this.resetForm.controls["tfac"].setValue(null);
    }).finally(() => {
      this.isInProgress = false;
    });
  }

  doForgot() {
    if (!this.forgotForm.valid) {
      return;
    }
    this.isInProgress = true;
    this.success_str = "";
    this.auth.Forgot({ email: this.forgotForm.get("email")?.value }).then(() => {
      this.email = this.forgotForm.get("email")?.value;
      this.doSetFormType("reset").then(() => { this.focus(this.tfacfocus); this.touch(this.resetForm); });
    }).catch(() => {
      this.forgotForm.controls["email"].setValue(null);
    }).finally(() => {
      this.isInProgress = false;
    });
  }

  sign_up() {
    if (!(this.signupForm.get("email")?.valid && this.signupForm.get("name")?.valid && this.signupForm.get("password")?.valid)) {
      return;
    }
    this.isInProgress = true;
    this.success_str = "";
    this.auth.sign_up({
      name: this.signupForm.get("name")?.value, email: this.signupForm.get("email")?.value, password: this.signupForm.get("password")?.value
    }).then((res: any) => {
      this.successMessage = res?.msg ?? "";
      this.formtype = "success";
    }).catch(() => {
      this.signupForm.controls["password"].setValue(null);
    }).finally(() => {
      this.isInProgress = false;
    });
  }

  doBackToSignup() {
    this.formtype = "signup";
  }

  doDismissModal() {
    this.misc.dismissModal(null).catch((error: any) => console.error("error", error));
  }
}
