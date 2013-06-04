

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
from gi.repository import GObject


def htmlcolor(*redgreenblue):
    """Creates the html representation of three color channels."""
    def hexify(val):
        foo = hex(val)[2:]
        if len(foo) < 2:
            foo = "0" + foo
        return foo
    return "".join(map(hexify, redgreenblue))


class Crosshair:
    def __init__(self, printer):

        self.printer = printer

        template = os.path.split(__file__)[0]
        template = os.path.join(template, "templates", "crosshair.glade")
        builder = Gtk.Builder()
        builder.add_from_file(template)
        builder.connect_signals(self)

        self.widget = builder.get_object("crosshair")
        picking = builder.get_object("picking_window")
        picking.show_all()

        self.__picking = builder.get_object("picking_crosshair")
        self.__buttons = {}
        for cardinality in ["north", "east", "south", "west"]:
            for intensity in range(1, 4):
                img_name = "{0}_{1}".format(cardinality, intensity)
                img_widget = builder.get_object(img_name)
                self.__buttons[img_name] = img_widget

        self.connected = False
        self.disable()
        self.__last_pick = None


    def lookup(self, red, green, blue, alpha):
        """Looks up which button is picked by the color passed to this
        function."""

        if alpha < 255:
            return None
        code = htmlcolor(red, green, blue)
        crosshair = {
            "fcaf3e" : "north_1",
            "f57900" : "north_2",
            "ce5c00" : "north_3",
            "ad7fa8" : "east_1",
            "75507b" : "east_2",
            "5c3566" : "east_3",
            "729fcf" : "south_1",
            "3465a4" : "south_2",
            "204a87" : "south_3",
            "fce94f" : "west_1",
            "edd400" : "west_2",
            "c4a000" : "west_3",
            }

        if crosshair.has_key(code):
            return crosshair[code]


    def pick(self, x, y):
        """Return the name of the fake button under the cursor."""
        x, y = int(x), int(y)
        img_buffer = self.__picking.get_pixbuf()
        width = img_buffer.get_width()
        height = img_buffer.get_height()
        n_channels = img_buffer.get_n_channels()
        if x >= 0 and x < width and y>= 0 and y < height:
            rowstride = img_buffer.get_rowstride()
            pixels = img_buffer.get_pixels()
            period = y * rowstride + x * n_channels;
            value = map(ord, pixels[period:period+4])
            return self.lookup(*value)
        else:
            return None


    def update_button(self, name, state):
        """Update the color of the named fake button."""
        widget = self.__buttons[name]
        base_path = os.path.join(os.path.split(__file__)[0], "templates", "svg")
        template = "crosshair_{0}{1}_{2}.svg"
        img = template.format(name[0],name.split("_")[1],state)
        img_path = os.path.join(base_path, img)
        assert os.path.isfile(img_path)
        widget.set_from_file(img_path)


    def update_buttons(self, state):
        for button in self.__buttons.keys():
            self.update_button(button, state)


    def on_mouse_motion(self, widget, event_info):
        if self.connected:
            widget = self.pick(event_info.x, event_info.y)
            if widget != self.__last_pick:
                self.update_buttons("blue")
                self.__last_pick = widget
                if widget:
                    self.update_button(widget, "green")


    def on_button_press(self, widget, event_info):
        widget = self.pick(event_info.x, event_info.y)
        if (widget and self.connected):
            self.update_button(widget, "green")
            self.button_action(widget)


    def on_button_release(self, widget, event_info):
        def reset_buttons(data):
            if self.connected:
                self.update_buttons("blue")
        GObject.timeout_add(50, reset_buttons, None)   


    def enable(self):
        self.connected = True
        self.update_buttons('blue')


    def disable(self):
        self.connected = False
        self.update_buttons('gray')


    def button_action(self, widget):
        group, param = widget.split("_")
        if group in ("north", "east", "south", "west"):
            magnitude = 10**(int(param)-1)
            if group == "north":
                self.printer.move(0, magnitude, 0)
            elif group == "south":
                self.printer.move(0, -1*magnitude, 0)
            elif group == "east":
                self.printer.move(magnitude, 0, 0)
            elif group == "west":
                self.printer.move(-1*magnitude, 0, 0)
                
        elif group in ("z"):
            pass
        elif group == "home":
            pass
        

    def refocus(self):
        """Called to reset the ui state.  Currently, this is only
        really used by the crosshair when the notebook page changes.
        """

        if self.connected:
            self.update_buttons("blue")

    def on_focus_in(self, widget, event_info):
        # TODO dim the gauge image when the window loses focus
        pass

    def on_focus_out(self, widget, event_info):
        # TODO dim the gauge image when the window loses focus
        pass
