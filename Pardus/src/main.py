#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import gi
import signal
import logging

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GLib

from yedek.mainwindow import MainWindow
from themes import ThemeManager
from tools import ToolManager
from queue_manager import QueueManager
class Application(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.pardus.toolsget",
                        flags=Gio.ApplicationFlags.FLAGS_NONE)
        
        # Initialize managers
        self.theme_manager = ThemeManager()
        self.tool_manager = ToolManager()
        
        # Add signal handler
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, self.on_sigint)
        
        # Add application actions
        self.create_actions()

    def create_actions(self):
        """Create application actions"""
        actions = [
            ("quit", self.on_quit),
            ("update", self.on_update),
            ("sysinfo", self.on_sysinfo), 
            ("about", self.on_about)
        ]
        
        for name, callback in actions:
            action = Gio.SimpleAction.new(name, None)
            action.connect("activate", callback)
            self.add_action(action)

    def do_activate(self):
        """Create and show main window"""
        try:
            win = MainWindow(self)
            win.show_all()
            win.progress_bar.hide() # Hide progress bar initially
        except Exception as e:
            logging.error(f"Failed to create main window: {e}")
            self.quit()
        
    def on_sigint(self):
        """Handle Ctrl+C"""
        self.quit()
        return GLib.SOURCE_REMOVE

    def on_quit(self, _action, _param):
        """Quit application"""
        win = self.get_active_window()
        if win:
            win.queue_manager.clear_queue()
        self.quit()

    def on_update(self, _action, _param):
        """Update package list"""
        win = self.get_active_window()
        if win and not win.is_installing:
            win.run_command(
                ["apt-get", "update"],
                "Paket listesi güncellendi."
            )

    def on_sysinfo(self, _action, _param):
        """Show system info"""
        win = self.get_active_window()
        if win:
            win.show_system_info()

    def on_about(self, _action, _param):
        """Show about dialog"""
        win = self.get_active_window()
        if win:
            win.show_about()

def main():
    """Application entry point"""
    try:
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Run application
        app = Application()
        return app.run(sys.argv)
        
    except KeyboardInterrupt:
        logging.info("Application terminated by user")
        return 0
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())