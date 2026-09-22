import { bootstrapApplication } from '@angular/platform-browser';
import { registerIcons } from './app/icons';
import { appConfig } from './app/app.config';
import { App } from './app/app';

// icons are referenced by name in templates and in collection schemas; the standalone build
// only serves what is registered, so every ionicon is mapped to its svg asset
registerIcons();

bootstrapApplication(App, appConfig)
  .catch((err) => console.error(err));
