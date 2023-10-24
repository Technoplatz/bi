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

@Injectable({
    providedIn: "root"
})

export class Su {

    constructor(
        private swu: SwUpdate,
        private misc: Miscellaneous
    ) {
        if (swu.isEnabled) {
            console.log("swu is enabled");
            setInterval(() => {
                console.log("swu checking for an update...");
                this.swu.checkForUpdate().then((res: any) => {
                    console.log("swu checked for update", res);
                }).catch((err: any) => {
                    console.error("swu update check error", err);
                });
            }, 3 * 60 * 1000);
        } else {
            console.error("swu is not enabled");
        }
    }

    public checkForUpdates(): void {
        this.swu.versionUpdates.subscribe((event_: VersionEvent) => {
            switch (event_.type) {
                case "VERSION_DETECTED":
                    console.log(`swu downloading new version: ${event_.version.hash}`);
                    break;
                case "VERSION_READY":
                    console.log(`swu current version: ${event_.currentVersion.hash}`);
                    console.log(`swu new version: ${event_.latestVersion.hash}`);
                    this.promptUser(event_);
                    break;
                case "VERSION_INSTALLATION_FAILED":
                    console.log(`swu failed installing new version "${event_.version.hash}": ${event_.error}`);
                    break;
            }
        });
    }

    private promptUser(event_: any): void {
        console.log("swu new version available");
        this.swu.activateUpdate().then(() => {
            console.log("swu update activated");
            this.misc.version.next({
                upgrade: true,
                version: event_.latestVersion.hash
            });
        });
    }
}