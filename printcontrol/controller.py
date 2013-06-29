

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


import os, json
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
        self.gauges = {
            "b" : None,
            "t" : [],
            }
        self.update_controls()
        self.disable()
        self.set_printer_name("Unknown Printer")

        PrinterInterface.__init__(self, printer_uuid)

    def add_gauges(self, temps):
        """Adds any necessary gaguges from a given temperature
        report."""
        
        dirty = False
        if temps.has_key("bed") and temps["bed"][0] > 0:
            if self.gauges["b"] is None:
                dirty = True
                self.gauges["b"] = BedGauge(self)

        if temps.has_key("tools"):
            while len(temps["tools"]) > len(self.gauges["t"]):
                tool_num = len(self.gauges["t"])
                self.gauges["t"].append(ExtruderGauge(self, tool_num))
                dirty = True
        if dirty:
            self.update_controls()

    def get_gauges(self):
        """Return a list of all gauge widgets without context."""
        
        gauges = []
        if self.gauges["b"] is not None:
            gauges.append(self.gauges["b"])
        if self.gauges["t"]:
            gauges += self.gauges["t"]
        return gauges

    def update_controls(self):
        """Clears out the controls packing box, and then populates it
        with a crosshair widget and some number of temperature
        controllers.
        """
        for child in self.controls.get_children():
            self.controls.remove(child)
        self.controls.add(self.crosshair.widget)
    
        for gauge in self.get_gauges():
            self.controls.add(gauge.widget)
            gauge.enable()

    def on_temp_request(self, gauge, target):
        """Called by a gauge when a user requests a temperature change."""

        # first determine if we're talking about a tool or the bed
        if self.gauges["b"] == gauge:
            # its the bed
            self.set_bed_temp(target)
        else:
            # which tool?
            tool = self.gauges["t"].index(gauge)
            self.set_tool_temp(tool, target)
            
    def refocus(self):
        """Called to reset the ui state.  Currently, this is only
        really used by the crosshair when the notebook page changes.
        """
        self.crosshair.refocus()

    def disable(self):
        """Disable the controls for this printer."""
        self.crosshair.disable()
        for gauge in self.get_gauges():
            gauge.disable()

        motors_off = self.builder.get_object("motors_off_button")
        motors_off.set_sensitive(False)
        
    def enable(self):
        """Enable this printer's controls."""
        self.crosshair.enable()
        for gauge in self.get_gauges():
            gauge.enable()
        
        motors_off = self.builder.get_object("motors_off_button")
        motors_off.set_sensitive(True)

    def on_state_change(self, state):
        """Signal handler for when the printer goes on or offline."""
        if state == "ready":
            self.enable()
        elif state == "offline":
            self.disable()

    def on_report(self, blob):
        packet = json.loads(blob)
        if packet.has_key("thermistors"):
            temps = packet['thermistors']
            self.add_gauges(temps)
            self.gauges["b"].set_label(temps["bed"][0])
            for gauge, temp in zip(self.gauges["t"], temps["tools"]):
                gauge.set_label(temp[0])
            
        
    def set_printer_name(self, name):
        """Sets the displayed name for this printer."""
        label = self.builder.get_object("dashboard_header")
        label.set_text("Dashboard for %s" % name)

    def on_focus_in(self, widget, event_info):
        self.crosshair.on_focus_in(widget, event_info)
        for gauge in self.get_gauges():
            gauge.on_focus_in(widget, event_info)

    def on_focus_out(self, widget, event_info):
        self.crosshair.on_focus_out(widget, event_info)
        for gauge in self.get_gauges():
            gauge.on_focus_out(widget, event_info)

    def on_motors_off(self, *args):
        self.motors_off()
