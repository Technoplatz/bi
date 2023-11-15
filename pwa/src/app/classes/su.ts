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

import { Injectable } from "@angular/core";
import { SwUpdate, VersionEvent } from "@angular/service-worker";
import { Miscellaneous } from "./misc";
import { environment } from "../../environments/environment";

@Injectable({
    providedIn: "root"
})

export class Su {
    private delay_: number = environment.swu_interval_mins;
    private swu_check_: boolean = true;

    constructor(
        private swu: SwUpdate,
        private misc: Miscellaneous
    ) {
        if (this.swu.isEnabled) {
            console.log("swu enabled");
            setInterval(() => {
                this.swu_check_ ?
                    this.swu.checkForUpdate().then((res_: any) => {
                        console.log(res_ ? "swu processed" : "no swu found");
                    }).catch((err_: any) => {
                        console.error("swu check error", err_);
                    }) : null;
            }, this.delay_ * 60 * 1000);
        } else {
            this.swu_check_ = false;
            console.error("swu is not enabled");
        }
    }

    public checkForUpdates(): void {
        this.swu.versionUpdates.subscribe((event_: VersionEvent) => {
            switch (event_.type) {
                case "VERSION_DETECTED":
                    this.swu_check_ = false;
                    console.log(`swu version detected ${event_.version.hash}`);
                    console.log("downloading...");
                    this.misc.version.next({ downloading: true, upgrade: false, version: event_.version.hash });
                    break;
                case "VERSION_READY":
                    this.swu_check_ = false;
                    console.log("swu version is ready");
                    this.misc.version.next({ downloading: false, upgrade: true, version: event_.latestVersion.hash });
                    break;
            }
        });
    }
}