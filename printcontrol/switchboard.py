

# This file is part of Printcontrol.
#
# Printcontrol is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Printcontrol is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Printcontrol.  If not, see <http://www.gnu.org/licenses/>.


from gi.repository import Gtk
from switchprint.switch_board import SwitchBoard
from controller import PrinterController


class SwitchBoardWindow(Gtk.Window, SwitchBoard):
    """Main window for PrinterControl"""
    def __init__(self):
        Gtk.Window.__init__(self, title="Printer Control")
        self.connect("delete-event", Gtk.main_quit)
        self.connect("focus-in-event", self.on_focus_in)
        self.connect("focus-out-event", self.on_focus_out)
        self.__show_placeholder()
        self.printers = []
        SwitchBoard.__init__(self, PrinterClass=PrinterController)
        
    def on_new_printer(self, printer):
        self.printers.append(printer)
        self.__update_content()

    def __update_content(self):
        self.__clear_window()
        if len(self.printers) == 1:
            self.__show_single_printer()
            
        elif len(self.printers) > 1:
            self.__show_notebook()

    def __clear_window(self):
        for child in self.get_children():
            self.remove(child)

    def __show_placeholder(self):
        placeholder = Gtk.Label("No printers detected.")
        placeholder.set_padding(40, 40)
        self.add(placeholder)

    def __show_single_printer(self):
        printer = self.printers[0]
        self.add(printer.widget)

    def __show_notebook(self):
        notebook = Gtk.Notebook()
        notebook.set_tab_pos(0)
        n = 1
        for printer in self.printers:
            name = "Unknown\n Printer %s" % n
            n += 1
            label = Gtk.Label(name)
            notebook.append_page(printer.widget, label)
            #notebook.add(label)
        self.add(notebook)
        notebook.connect("switch-page", self.on_change_page)
        
    def on_change_page(self, widget, page_num, data):
        self.printers[data].refocus()

    def on_focus_in(self, widget, event_info):
        for printer in self.printers:
            printer.on_focus_in(widget, event_info)

    def on_focus_out(self, widget, event_info):
        for printer in self.printers:
            printer.on_focus_out(widget, event_info)
