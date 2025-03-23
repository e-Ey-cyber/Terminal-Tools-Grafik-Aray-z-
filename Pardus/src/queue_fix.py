def __init__(self, application):
    # Existing initialization code...
    
    # Initialize queue
    self.download_queue = queue.Queue()
    self.queue_items = []
    self.is_queue_running = False#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import gi
import queue
from gi.repository import Gtk, GLib, Gio, GdkPixbuf

# This file contains fixes for the queue-related issues in MainWindow

def initialize_queue(self):
    """Initialize the download queue and related attributes"""
    # Create a queue for package downloads
    self.download_queue = queue.Queue()
    
    # List to keep track of queue items for UI display
    self.queue_items = []
    
    # Flag to track if queue is currently running
    self.is_queue_running = False

def add_to_queue(self, package_name, display_name=None):
    """Add package to installation queue"""
    if not display_name:
        display_name = package_name
        
    # Add to queue
    self.download_queue.put((package_name, display_name))
    
    # Add to tracking list for UI
    self.queue_items.append((package_name, display_name))
    
    # Update UI
    self.update_terminal_output(f"{display_name} indirme kuyruğuna eklendi.")
    
    # Update queue count in UI
    self.status_label.set_text(f"Kuyrukta {len(self.queue_items)} araç var")
    
    # Update queue listbox if it exists
    self.update_queue_listbox()

def update_queue_listbox(self):
    """Update the queue listbox in the UI"""
    # Clear existing items in the queue store
    if hasattr(self, 'queue_store'):
        self.queue_store.clear()
        
        # Add all items from queue_items to the store
        for package_name, display_name in self.queue_items:
            self.queue_store.append([package_name, display_name])

def start_queue(self, button=None):
    """Start processing the installation queue"""
    if self.is_installing:
        dialog = Gtk.MessageDialog(
            transient_for=self,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK,
            text="İşlem Devam Ediyor"
        )
        dialog.format_secondary_text("Lütfen mevcut işlemin tamamlanmasını bekleyin.")
        dialog.run()
        dialog.destroy()
        return
    
    if not hasattr(self, 'download_queue') or self.download_queue.empty():
        dialog = Gtk.MessageDialog(
            transient_for=self,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="İndirme kuyruğu boş"
        )
        dialog.run()
        dialog.destroy()
        return
    
    self.is_queue_running = True
    self.update_terminal_output("İndirme kuyruğu başlatıldı.")
    self.process_next_in_queue()

def process_next_in_queue(self):
    """Process next package in queue"""
    try:
        if self.is_installing or self.download_queue.empty():
            if self.download_queue.empty():
                self.is_queue_running = False
                self.update_terminal_output("İndirme kuyruğu tamamlandı.")
                self.status_label.set_text("Kuyruk tamamlandı")
            return

        # Get next package from queue
        package_name, display_name = self.download_queue.get()
        
        # Remove from tracking list
        if (package_name, display_name) in self.queue_items:
            self.queue_items.remove((package_name, display_name))
        
        # Update queue listbox
        self.update_queue_listbox()
        
        # Install package
        self.update_terminal_output(f"Kuyruktan yükleniyor: {display_name}")
        self.run_command(
            ["pkexec", "apt-get", "install", "-y", package_name],
            f"{display_name} paketi başarıyla yüklendi."
        )
    except Exception as e:
        self.update_terminal_output(f"Hata oluştu: {str(e)}")
    finally:
        # Update progress indicator
        if hasattr(self, 'update_progress'):
            self.update_progress(0, "İşlem tamamlandı")

def clear_queue(self, button=None):
    """Clear installation queue"""
    if not hasattr(self, 'download_queue'):
        # Initialize queue if it doesn't exist
        self.download_queue = queue.Queue()
        self.queue_items = []
        return
        
    # Clear the queue
    while not self.download_queue.empty():
        self.download_queue.get()
    
    # Clear the tracking list
    self.queue_items.clear()
    
    # Update queue listbox
    self.update_queue_listbox()
    
    # Update UI
    self.update_terminal_output("İndirme kuyruğu temizlendi.")
    self.status_label.set_text("Kuyruk temizlendi")
    self.is_queue_running = False