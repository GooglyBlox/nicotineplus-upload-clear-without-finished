# Upload Clear Without Finished

This Nicotine+ plugin removes uploads `Clear All` menu entries that clear finished transfers.

Removed entries:

- `Finished / Cancelled / Failed`
- `Finished / Cancelled`
- `Finished`
- `Everything...`

The remaining default clear options are `Cancelled`, `Failed`, `User Logged Off`, and `Queued...`.

<img width="327" height="502" alt="image" src="https://github.com/user-attachments/assets/58bf8d60-2dcb-4b63-94c7-3591785a9ca6" />

## What It Changes

The plugin leaves finished uploads in the uploads list by removing clear actions that would include `Finished`. It does not change Nicotine+'s transfer statuses or upload history; it only changes which clear actions are available in the uploads clear menu.

## Tested Versions

This has been tested on Nicotine+ `3.3.10`, GTK `4.16.12`, and Python `3.12.9`.

Other Nicotine+, GTK, or Python versions may work, but this plugin relies on Nicotine+'s uploads menu internals and can break if that UI structure changes.

## Caveats

This is a UI monkey-patch. Nicotine+ does not currently expose a plugin API for changing this GTK menu, so the plugin waits for the uploads view, grabs `window.uploads.popup_menu_clear`, and rebuilds that submenu with the finished-clearing entries omitted.

If the uploads clear menu behaves strangely after enabling or disabling the plugin, disable it and restart Nicotine+.

## Installing

The intended install method is the zip from [GitHub Releases](https://github.com/GooglyBlox/nicotineplus-upload-clear-without-finished/releases). Then, extract it into your plugins folder.

Once it's installed, enable `Upload Clear Without Finished`, open the uploads tab, and give it a moment. The plugin waits for the window to exist, patches the uploads clear menu, and then removes the options that clear finished uploads.

