

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


import os, re
from gi.repository import Gtk


class BasicGauge:
    def __init__(self, printer, prefix):
        self.printer = printer
        template = os.path.split(__file__)[0]
        template = os.path.join(template, "templates", "temperature_gauges.glade")
        target = prefix + "gauge"
        self.builder = Gtk.Builder()
        self.builder.add_objects_from_file(template, [target])
        self.builder.connect_signals(self)
        self.widget = self.builder.get_object(target)

        self.frame_label = self.builder.get_object(prefix+"frame_label")

        self.img = self.builder.get_object(prefix+"temp_img")
        self.label = self.builder.get_object(prefix+"temp_label")
        self.combo = self.builder.get_object(prefix+"temp_combo")
        self.combo.set_active(0)

    def set_frame_label(self, text):
        self.frame_label.set_markup("<b>%s</b>" % text)

    def set_label(self, val):
        if val is None:
            self.label.set_text("offline")
        else:
            self.label.set_text(u"%s\u2103"%val)

    def disable(self):
        self.set_label(None)
        self.combo.set_sensitive(False)

    def enable(self):
        self.combo.set_sensitive(True)

    def on_focus_in(self, widget, event_info):
        # TODO dim the gauge image when the window loses focus
        pass

    def on_focus_out(self, widget, event_info):
        # TODO dim the gauge image when the window loses focus
        pass

    def set_temperature(self, combo_text):
        request = combo_text.get_active_text()
        found = re.findall("\([0-9]+\)", request)
        if len(found) == 1:
            val = found[0]
            target = val[1:-1]
            self.printer.on_temp_request(self, int(target))
        elif request == "Off":
            self.printer.on_temp_request(self, int(0))

class BedGauge(BasicGauge):
    def __init__(self, printer):
        BasicGauge.__init__(self, printer, "bed_")


class ExtruderGauge(BasicGauge):
    def __init__(self, printer, extruder_number, singular=False):
        BasicGauge.__init__(self, printer, "extruder_")
        self.feed = self.builder.get_object("feed_button")
        self.reverse = self.builder.get_object("reverse_check")

        adjustment = Gtk.Adjustment(5, 0, 500, 1, 10, 0)
        self.dist = self.builder.get_object("feed_distance")
        self.dist.set_adjustment(adjustment)

        adjustment = Gtk.Adjustment(200, 0, 999, 1, 10, 0)
        self.rate = self.builder.get_object("feed_rate")
        self.rate.set_adjustment(adjustment)

        if singular:
            self.set_frame_label("Extruder")
        else:
            self.set_frame_label("Extruder #%s" % (extruder_number+1))


    def disable(self):
        BasicGauge.disable(self)
        self.feed.set_sensitive(False)
        
    def enable(self):
        BasicGauge.enable(self)
        self.feed.set_sensitive(True)
        
