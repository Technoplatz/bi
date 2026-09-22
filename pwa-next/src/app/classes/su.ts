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

import { Injectable } from "@angular/core";
import { SwUpdate, VersionEvent } from "@angular/service-worker";
import { Miscellaneous } from "./misc";
import { environment } from "../../environments/environment";

@Injectable({ providedIn: "root" })
export class Su {
  private delay_: number = environment.swu_interval_mins;

  constructor(private swu: SwUpdate, private misc: Miscellaneous) {
    if (this.swu.isEnabled) {
      setInterval(() => {
        this.swu.checkForUpdate().catch((error_: any) => {
          console.error("swu check error", error_);
        });
      }, this.delay_ * 60 * 1000);
    }
  }

  check_for_updates() {
    if (!this.swu.isEnabled) {
      return;
    }
    this.swu.versionUpdates.subscribe((event_: VersionEvent) => {
      switch (event_.type) {
        case "VERSION_DETECTED":
          this.misc.version.next({ detected: true });
          break;
        case "VERSION_READY":
          this.misc.version.next({ ready: true });
          break;
        case "VERSION_INSTALLATION_FAILED":
          console.error("swu version installation failed");
          break;
        default:
          break;
      }
    });
  }
}
