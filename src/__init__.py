import gc

from pynicotine.events import events
from pynicotine.gtkgui.application import Application
from pynicotine.gtkgui.mainwindow import MainWindow
from pynicotine.pluginsystem import BasePlugin

INACTIVE_PLUGIN_ID = "upload_clear_inactive"


class Plugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self._install_attempts = 0
        self._install_scheduled = False
        self._periodic_check_started = False
        self._menu = None

    def loaded_notification(self):
        self._schedule_ui_install()
        if not self._periodic_check_started:
            self._periodic_check_started = True
            events.schedule(delay=2, callback=self._schedule_ui_install, repeat=True)

    def disable(self):
        self._restore_clear_menu()
        self._reset_runtime_refs()

    def unloaded_notification(self):
        self._reset_runtime_refs()

    def _schedule_ui_install(self):
        if self._install_scheduled:
            return

        if self._is_menu_installed():
            return

        self._install_scheduled = True
        events.invoke_main_thread(self._install_menu)

    def _is_menu_installed(self):
        if self._menu is None:
            return False

        try:
            item_labels = set(getattr(self._menu, "items", {}))
        except Exception:
            return False

        blocked_labels = {
            "Finished / Cancelled / Failed",
            "Finished / Cancelled",
            "Finished",
            "Everything\u2026",
            "Everything...",
        }
        return not item_labels.intersection(blocked_labels)

    def _find_main_window(self):
        for obj in gc.get_objects():
            if isinstance(obj, Application):
                try:
                    if obj.window is not None:
                        return obj.window
                except Exception:
                    pass

        visible_windows = []
        fallback_windows = []

        for obj in gc.get_objects():
            if isinstance(obj, MainWindow):
                try:
                    if obj.widget is not None and obj.widget.get_visible():
                        visible_windows.append(obj)
                    else:
                        fallback_windows.append(obj)
                except Exception:
                    fallback_windows.append(obj)

        if visible_windows:
            return visible_windows[-1]

        if fallback_windows:
            return fallback_windows[-1]

        return None

    def _get_uploads_view_and_menu(self):
        window = self._find_main_window()
        if window is None:
            return None, None

        try:
            uploads_view = window.uploads
            menu = uploads_view.popup_menu_clear
        except Exception:
            return None, None

        return uploads_view, menu

    def _install_menu(self):
        self._install_scheduled = False

        uploads_view, menu = self._get_uploads_view_and_menu()
        if menu is None:
            self._retry_install()
            return

        try:
            menu.update_model()
        except Exception:
            self._retry_install()
            return

        blocked_labels = {
            "Finished / Cancelled / Failed",
            "Finished / Cancelled",
            "Finished",
            "Everything\u2026",
            "Everything...",
        }

        item_labels = set(getattr(menu, "items", {}))
        if not item_labels.intersection(blocked_labels):
            self._menu = menu
            self._install_attempts = 0
            return

        self._rebuild_clear_menu(
            uploads_view,
            menu,
            include_finished_options=False,
            inactive_callback=self._get_inactive_callback(),
        )
        self._menu = menu
        self._install_attempts = 0

    def _retry_install(self):
        self._install_attempts += 1
        if self._install_attempts <= 60:
            events.schedule(delay=0.5, callback=self._schedule_ui_install)

    def _get_inactive_callback(self):
        try:
            plugin = self.parent.enabled_plugins.get(INACTIVE_PLUGIN_ID)
        except Exception:
            plugin = None

        if plugin is None:
            return None

        return getattr(plugin, "on_clear_cancelled_failed_logged_off", None)

    def _restore_clear_menu(self):
        uploads_view, menu = self._get_uploads_view_and_menu()
        if menu is None:
            return

        self._rebuild_clear_menu(
            uploads_view,
            menu,
            include_finished_options=True,
            inactive_callback=self._get_inactive_callback(),
        )

    def _rebuild_clear_menu(self, uploads_view, menu, include_finished_options=True, inactive_callback=None):
        menu.clear()
        items = []

        if include_finished_options:
            items.extend([
                ("#Finished / Cancelled / Failed", uploads_view.on_clear_finished_failed),
                ("#Finished / Cancelled", uploads_view.on_clear_finished_cancelled),
            ])

        if inactive_callback is not None:
            items.append(("#Cancelled / Failed / User Logged Off", inactive_callback))

        if items:
            items.append(("", None))

        if include_finished_options:
            items.append(("#Finished", uploads_view.on_clear_finished))

        items.extend([
            ("#Cancelled", uploads_view.on_clear_cancelled),
            ("#Failed", uploads_view.on_clear_failed),
            ("#User Logged Off", uploads_view.on_clear_logged_off),
            ("#Queued\u2026", uploads_view.on_try_clear_queued),
        ])

        if include_finished_options:
            items.extend([
                ("", None),
                ("#Everything\u2026", uploads_view.on_try_clear_all),
            ])

        menu.add_items(*items)
        menu.update_model()

    def _reset_runtime_refs(self):
        self._menu = None
