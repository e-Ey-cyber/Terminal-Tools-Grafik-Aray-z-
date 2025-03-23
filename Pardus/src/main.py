#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import gi
import signal
import logging
import setproctitle
import logging.config

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GLib

from src.mainwindow import MainWindow  # Absolute import
from src.themes import ThemeManager
from src.tools import ToolManager
from src.queue_manager import QueueManager 
from src.config import APP_VERSION, LOG_CONFIG, APP_NAME

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

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_modules = [
        ('gi', 'python3-gi'),
        ('PIL', 'python3-pil'),
        ('requests', 'python3-requests')
    ]
    
    missing = []
    for module, package in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("Eksik bağımlılıklar:", ", ".join(missing))
        print("Yüklemek için: sudo apt install", " ".join(missing))
        return False
    return True

def main():
    """Application entry point"""
    try:
        # Check dependencies first
        if not check_dependencies():
            sys.exit(1)
            
        # Set process title
        setproctitle.setproctitle(APP_NAME.lower())
        
        # Configure logging
        logging.config.dictConfig(LOG_CONFIG)
        logger = logging.getLogger(__name__)
        
        # Handle uncaught exceptions
        def exception_handler(exc_type, exc_value, exc_traceback):
            logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        sys.excepthook = exception_handler
        
        # Run application
        app = Application()
        return app.run(sys.argv)
        
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
        return 0
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())