/*
Technoplatz BI

Copyright (C) 2019-2023 Technoplatz IT Solutions GmbH, Mustafa Mat

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

If your software can interact with users remotely through a computer
network, you should also make sure that it provides a way for users to
get its source.  For example, if your program is a web application, its
interface could display a "Source" link that leads users to an archive
of the code.  There are many ways you could offer source, and different
solutions will be better for different programs; see section 13 for the
specific requirements.

You should also get your employer (if you work as a programmer) or school,
if any, to sign a "copyright disclaimer" for the program, if necessary.
For more information on this, and how to apply and follow the GNU AGPL, see
https://www.gnu.org/licenses.
*/

import { Component, OnInit, ViewChild, HostListener, Input } from "@angular/core";
import { IonInput } from "@ionic/angular";
import { Validators, UntypedFormBuilder, UntypedFormGroup } from "@angular/forms";
import { Storage } from "@ionic/storage";
import { Auth } from "../../classes/auth";
import { Miscellaneous } from "../../classes/misc";

@Component({
  selector: "app-sign",
  templateUrl: "./sign.page.html",
  styleUrls: ["./sign.page.scss"],
})
export class SignPage implements OnInit {
  @Input() op: string = "";
  @Input() user: any;
  @Input() isSignedIn: boolean = false;
  @ViewChild("emailfocus", { static: false }) emailfocus?: IonInput;
  @ViewChild("emailfocussignin", { static: false }) emailfocussignin?: IonInput;
  @ViewChild("emailfocussignup", { static: false }) emailfocussignup?: IonInput;
  @ViewChild("namefocus", { static: false }) namefocus?: IonInput;
  @ViewChild("passwordfocus", { static: false }) passwordfocus?: IonInput;
  @ViewChild("passcodefocus", { static: false }) passcodefocus?: IonInput;
  @ViewChild("tfacfocus", { static: false }) tfacfocus?: IonInput;

  public error: string = "";
  public success_str: string = "";
  public successMessage: string = "";
  public signupForm: UntypedFormGroup;
  public forgotForm: UntypedFormGroup;
  public signinForm: UntypedFormGroup;
  public resetForm: UntypedFormGroup;
  public TFACForm: UntypedFormGroup;
  public successForm: UntypedFormGroup;
  public formtype: string = "";
  public isInProgress: boolean = false;
  public isEuTaxRequired: boolean = false;
  public cart: any;
  public taxExcluded: boolean = false;
  public tax: Number = 0;
  public rate: number = 0;
  public total: any = 0;
  public grandtotal: any = 0;
  public currency: string = "";
  public isRememberMe: boolean = false;
  public email: string = "";
  private focustime = 600;
  private passwordpttrn_: string = "(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*_-]).{8,32}";

  @HostListener("document:keydown", ["$event"]) func(event: any) {
    if (event.key === "Enter") {
      const q =
        this.formtype === "success"
          ? this.doAfterSuccess()
          : this.formtype === "signup"
            ? this.Signup()
            : this.formtype === "forgot"
              ? this.doForgot()
              : this.formtype === "signin"
                ? this.Signin()
                : this.formtype === "tfac"
                  ? this.TFAC()
                  : null;
    }
  }
  constructor(private formBuilder: UntypedFormBuilder, private auth: Auth, private misc: Miscellaneous, private storage: Storage) {
    this.resetForm = this.formBuilder.group({
      password: [
        null,
        Validators.compose([
          Validators.required,
          Validators.minLength(8),
          Validators.maxLength(32),
          Validators.pattern(this.passwordpttrn_)
        ]),
      ],
      tfac: [
        null,
        Validators.compose([
          Validators.required,
          Validators.pattern(/^\d{6}$/)
        ])]
    },
      {}
    );
    this.signupForm = this.formBuilder.group({
      name: [
        null,
        Validators.compose([
          Validators.required,
          Validators.minLength(5),
          Validators.maxLength(32)
        ])
      ],
      email: [
        null,
        Validators.compose([
          Validators.required,
          Validators.email,
          Validators.maxLength(32)
        ])
      ],
      password: [
        null,
        Validators.compose([
          Validators.required,
          Validators.minLength(8),
          Validators.maxLength(32),
          Validators.pattern(this.passwordpttrn_)
        ]),
      ],
      passcode: [
        null,
        Validators.compose([
          Validators.required,
          Validators.minLength(16),
          Validators.maxLength(32)
        ])
      ]
    },
      {}
    );
    this.TFACForm = this.formBuilder.group({
      tfac: [
        null,
        Validators.compose([
          Validators.required,
          Validators.pattern(/^\d{6}$/)
        ])],
    },
      {}
    );
    this.forgotForm = this.formBuilder.group({
      email: [
        null,
        Validators.compose([
          Validators.required,
          Validators.email,
          Validators.maxLength(64)]
        )]
    },
      {}
    );
    this.successForm = this.formBuilder.group({}, {});
    this.resetForm = this.formBuilder.group({
      password: [
        null,
        Validators.compose([
          Validators.required,
          Validators.minLength(8),
          Validators.maxLength(32),
          Validators.pattern(this.passwordpttrn_)
        ]),
      ],
      tfac: [
        null,
        Validators.compose([
          Validators.required,
          Validators.pattern(/^\d{6}$/)
        ])]
    },
      {}
    );
    this.signinForm = this.formBuilder.group({
      email: [
        null,
        Validators.compose([
          Validators.required,
          Validators.email,
          Validators.maxLength(64)
        ])],
      password: [
        null,
        Validators.compose([
          Validators.required,
          Validators.minLength(8),
          Validators.maxLength(32),
          Validators.pattern(this.passwordpttrn_)
        ])],
      isRememberMe: [this.isRememberMe, Validators.compose([])],
    },
      {}
    );
    this.signupForm = this.formBuilder.group({
      name: [
        null,
        Validators.compose([
          Validators.required,
          Validators.minLength(5),
          Validators.maxLength(32)
        ])
      ],
      email: [
        null,
        Validators.compose([
          Validators.required,
          Validators.email,
          Validators.maxLength(32)
        ])
      ],
      password: [
        null,
        Validators.compose([
          Validators.required,
          Validators.minLength(8),
          Validators.maxLength(32),
          Validators.pattern(this.passwordpttrn_)
        ]),
      ],
      passcode: [
        null,
        Validators.compose([
          Validators.required,
          Validators.minLength(16),
          Validators.maxLength(32)
        ])
      ]
    },
      {}
    );
    this.TFACForm = this.formBuilder.group({
      tfac: [
        null,
        Validators.compose([
          Validators.required,
          Validators.pattern(/^\d{6}$/)
        ])],
    },
      {}
    );
    this.forgotForm = this.formBuilder.group({
      email: [
        null,
        Validators.compose([
          Validators.required,
          Validators.email,
          Validators.maxLength(64)]
        )]
    },
      {}
    );
    this.successForm = this.formBuilder.group({}, {});
  }

  ngOnInit() {
    this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
      this.email = LSUSERMETA?.email;
      this.storage.get("LSREMEMBERME").then((LSREMEMBERME: boolean) => {
        this.isRememberMe = LSREMEMBERME ? true : false;
        LSREMEMBERME ? this.signinForm.get("email")?.setValue(this.email) : null;
        this.signinForm.get("isRememberMe")?.setValue(this.isRememberMe);
        this.doSetOp(this.op);
      });
    });
  }

  ngOnDestroy() {
    this.storage.remove("LSOP").then(() => {
      this.storage.remove("LSFORMTYPE").then(() => { }).catch((error: any) => {
        console.error("storage formtype remove error", error);
      });
    }).catch((error: any) => {
      console.error("storage op remove error", error);
    });
  }

  doSetOp(op: string) {
    this.storage.set("LSOP", op).then(() => {
      this.op = op;
      if (op === "signup") {
        this.doStartSignup().then(() => { }).catch((error: any) => {
          console.error("signup start error", error);
        });
      } else if (op === "signin") {
        this.doStartSignin().then(() => { }).catch((error: any) => {
          console.error("signin start error", error);
        });
      } else if (op === "forgot") {
        this.doStartForgot().then(() => { }).catch((error: any) => {
          console.error("forgot start error", error);
        });
      }
    }).catch((error: any) => {
      console.error("storage set op error", error);
    });
  }

  doSetFormType(f: string) {
    return new Promise((resolve, reject) => {
      this.storage.set("LSFORMTYPE", f).then(() => {
        this.formtype = f;
        resolve(true);
      }).catch((error: any) => {
        console.error("storage set error", error);
        reject(error);
      });
    });
  }

  doStartSignin() {
    return new Promise((resolve, reject) => {
      this.doSetFormType("signin").then(() => {
        this.signinForm?.get("email")?.value ? setTimeout(() => {
          this.passwordfocus?.setFocus().then(() => {
            resolve(true);
          });
        }, this.focustime)
          : setTimeout(() => {
            this.emailfocussignin?.setFocus().then(() => {
              resolve(true);
            });
          }, this.focustime);
      }).catch((error: any) => {
        console.error(error);
        reject(error);
      });
    });
  }

  doStartForgot() {
    return new Promise((resolve, reject) => {
      this.doSetFormType("forgot").then(() => {
        setTimeout(() => {
          this.emailfocus?.setFocus().then(() => {
            resolve(true);
          });
        }, this.focustime);
      }).catch((error: any) => {
        console.error(error);
        reject(error);
      });
    });
  }

  doStartSignup() {
    return new Promise((resolve, reject) => {
      this.doSetFormType("signup").then(() => {
        setTimeout(() => {
          this.emailfocussignup?.setFocus().then(() => {
            resolve(true);
          });
        }, this.focustime);
      }).catch((error: any) => {
        console.error(error);
        reject(error);
      });
    });
  }

  doAfterSuccess() {
    this.storage.get("LSOP").then((LSOP: string) => {
      ["forgot", "signup", "checkout"].includes(LSOP) ? this.doSetOp("signin") : null;
    }).catch((error: any) => {
      console.error("storage get error", error);
    });
  }

  Signin() {
    this.isInProgress = true;
    this.error = "";
    this.success_str = "";
    const r = this.isRememberMe
      ? this.storage.set("LSREMEMBERME", this.isRememberMe).then(() => {
        this.storage.set("LSUSERMETA", { email: this.signinForm?.get("email")?.value }).then(() => { });
      })
      : this.storage.remove("LSREMEMBERME").then(() => { });
    if (this.signinForm?.get("email")?.valid && this.signinForm?.get("password")?.valid) {
      this.auth.Signin({
        email: this.signinForm.get("email")?.value,
        password: this.signinForm.get("password")?.value
      }).then(() => {
        this.storage.set("LSREMEMBERME", this.signinForm?.get("isRememberMe")?.value).then(() => {
          this.storage.set("LSUSERMETA", { email: this.signinForm?.get("email")?.value }).then(() => {
            this.email = this.signinForm.get("email")?.value;
            this.doSetFormType("tfac").then(() => {
              setTimeout(() => {
                this.tfacfocus?.setFocus().then(() => { });
              }, this.focustime);
            }).catch((error: any) => {
              console.error(error);
            });
          });
        });
      }).catch((err: any) => {
        this.signinForm?.controls["password"].setValue(null);
      }).finally(() => {
        this.isInProgress = false;
      });
    } else {
      this.isInProgress = false;
      this.signinForm?.controls["password"].setValue(null);
      this.error = "invalid credentials";
    }
  }

  TFAC() {
    this.isInProgress = true;
    this.success_str = "";
    this.auth.TFAC({
      email: this.email,
      password: this.signinForm.get("password")?.value,
      tfac: this.TFACForm.get("tfac")?.value
    }).then(() => {
      this.doDismissModal();
    }).catch((error: any) => {
      this.TFACForm.controls["tfac"].setValue(null);
    }).finally(() => {
      this.isInProgress = false;
    });
  }

  Reset() {
    this.isInProgress = true;
    this.success_str = "";
    this.auth.Reset({
      email: this.email,
      password: this.resetForm.get("password")?.value,
      tfac: this.resetForm.get("tfac")?.value
    }).then(() => {
      this.isInProgress = false;
      this.success_str = "password was reset successfully";
      this.formtype = "signin"
    }).catch((error: any) => {
      this.isInProgress = false;
      console.error("error reset", error);
      this.resetForm.controls["tfac"].setValue(null);
    });
  }

  doForgot() {
    if (!this.forgotForm.valid) {
      console.error("form is not valid");
    } else {
      this.isInProgress = true;
      this.success_str = "";
      this.auth.Forgot({
        email: this.forgotForm.get("email")?.value
      }).then(() => {
        this.email = this.forgotForm.get("email")?.value
        this.doSetFormType("reset").then(() => {
          setTimeout(() => {
            this.tfacfocus?.setFocus().then(() => {
              this.isInProgress = false;
            });
          }, this.focustime);
        }).catch((error: any) => {
          console.error(error);
        });
      }).catch((error: any) => {
        this.isInProgress = false;
        this.forgotForm.controls["email"].setValue(null);
      });
    }
  }

  Signup() {
    if (this.signupForm.get("email")?.valid && this.signupForm.get("name")?.valid && this.signupForm.get("password")?.valid && this.signupForm.get("passcode")?.valid) {
      this.isInProgress = true;
      this.success_str = "";
      this.auth.Signup({
        name: this.signupForm.get("name")?.value,
        email: this.signupForm.get("email")?.value,
        password: this.signupForm.get("password")?.value,
        passcode: this.signupForm.get("passcode")?.value
      }).then((res: any) => {
        this.isInProgress = false;
        this.successMessage = res.msg;
        this.formtype = "success";
      }).catch((error: any) => {
        this.isInProgress = false;
        this.signinForm?.controls["password"].setValue(null);
      });
    }
  }

  doBackToSignup() {
    this.formtype = "signup";
  }

  doDismissModal() {
    this.misc.dismissModal(null).then(() => { }).catch((error: any) => {
      console.error("error", error.msg);
    });
  }
}
