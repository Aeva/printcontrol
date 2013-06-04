

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


import os
from gi.repository import Gtk
from switchprint.printer_interface import PrinterInterface
from crosshair import Crosshair
from gauges import BedGauge, ExtruderGauge


class PrinterController(PrinterInterface):
    """This class implements the gui functionality for the configuring
    and operating a specific printer."""

    def __init__(self, printer_uuid):
        template = os.path.split(__file__)[0]
        template = os.path.join(template, "templates", "printer_control.glade")
        self.builder = Gtk.Builder()
        self.builder.add_from_file(template)
        self.builder.connect_signals(self)

        window = self.builder.get_object("window1")
        self.widget = window.get_child()
        window.remove(self.widget)

        self.controls = self.builder.get_object("control_widgets_box")
        self.crosshair = Crosshair(self)
        self.gauges = [
            BedGauge(self),
            ExtruderGauge(self, 0),
            ExtruderGauge(self, 1)
            ]
        self.update_controls()
        self.disable()
        self.set_printer_name("Unknown Printer")

        PrinterInterface.__init__(self, printer_uuid)
        
    def update_controls(self):
        """Clears out the controls packing box, and then populates it
        with a crosshair widget and some number of temperature
        controllers.
        """
        for child in self.controls.get_children():
            self.controls.remove(child)
        self.controls.add(self.crosshair.widget)
        for gauge in self.gauges:
            self.controls.add(gauge.widget)
            gauge.disable()

    def refocus(self):
        """Called to reset the ui state.  Currently, this is only
        really used by the crosshair when the notebook page changes.
        """
        self.crosshair.refocus()

    def disable(self):
        """Disable the controls for this printer."""
        self.crosshair.disable()
        for gauge in self.gauges:
            gauge.disable()

        motors_off = self.builder.get_object("motors_off_button")
        motors_off.set_sensitive(False)
        
    def enable(self):
        """Enable this printer's controls."""
        self.crosshair.enable()
        for gauge in self.gauges:
            gauge.enable()
        
        motors_off = self.builder.get_object("motors_off_button")
        motors_off.set_sensitive(True)

        # FIXME don't send printer commands by default here
        self.home()
        self.relative_mode()

    def on_state_change(self, state):
        """Signal handler for when the printer goes on or offline."""
        if state == "ready":
            self.enable()
        elif state == "offline":
            self.disable()
        
    def set_printer_name(self, name):
        """Sets the displayed name for this printer."""
        label = self.builder.get_object("dashboard_header")
        label.set_text("Dashboard for %s" % name)

    def on_focus_in(self, widget, event_info):
        self.crosshair.on_focus_in(widget, event_info)
        for gauge in self.gauges:
            gauge.on_focus_in(widget, event_info)

    def on_focus_out(self, widget, event_info):
        self.crosshair.on_focus_out(widget, event_info)
        for gauge in self.gauges:
            gauge.on_focus_out(widget, event_info)
