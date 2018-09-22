
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import _thread
import mss.tools
from PIL import Image
import pyfirmata
import time
import colorsys


board = pyfirmata.Arduino('/dev/ttyUSB0')
r = board.get_pin('d:9:o')
g = board.get_pin('d:10:o')
b = board.get_pin('d:11:o')
r.mode = pyfirmata.PWM
g.mode = pyfirmata.PWM
b.mode = pyfirmata.PWM
global kill

def most_frequent_colour(image):
    w, h = image.size
    pixels = image.getcolors(w * h)

    most_frequent_pixel = pixels[0]
    for count, colour in pixels:
        if count > most_frequent_pixel[0]:
            most_frequent_pixel = (count, colour)
    return most_frequent_pixel[1]


def setcolor(red,green,blue):
    red,green,blue = convert(red,green,blue)
    r.write(red)
    g.write(green/1.2442)
    b.write(blue/1.8433)


def setoff():
    r.write(0)
    g.write(0)
    b.write(0)


def fade(red, green, blue, oldred, oldgreen, oldblue):
    while oldred != red or oldgreen != green or oldblue != blue:
        if oldred < red:
            oldred += 1
        elif oldred > red:
            oldred -= 1

        if oldgreen < green:
            oldgreen += 1
        elif oldgreen >green:
            oldgreen -= 1

        if oldblue < blue:
            oldblue += 1
        elif oldblue > blue:
            oldblue -= 1
        setcolor(oldred,oldgreen,oldblue)


def convert(r,g,b):

    r= r/ 255.0
    g= g/ 255.0
    b= b/ 255.0

    h, l, s = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return r,g,b


def Sync():
    red = 0
    green = 0
    blue = 0

    while kill != 1:
        with mss.mss() as sct:
            # The screen part to capture
            monitor = {"top": 780, "left": 0, "width": 1920, "height": 300}
            output = "temp.png".format(**monitor)

            # Grab the data
            sct_img = sct.grab(monitor)

            # Save to the picture file
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
            im = Image.open('temp.png')
            oldred = red
            oldgreen=green
            oldblue=blue
            color = most_frequent_colour(im)
            red = color[0]
            green = color[1]
            blue = color[2]
            print (color)
         
            fade(red,green,blue,oldred,oldgreen,oldblue)
        time.sleep(1)
    return


class LedControl(Gtk.Window):


    def __init__(self):
        Gtk.Window.__init__(self, title="LED Control")
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(10)
        self.set_size_request(400,200)
        self.set_resizable(False);
        vbox = Gtk.VBox()
        hbox = Gtk.Box(spacing=6)
        global cbox
        self.add(vbox)
        vbox.show()

        buttonOff = Gtk.RadioButton.new_with_label_from_widget(None, "Off")
        buttonOff.connect("toggled", self.on_button_toggled, "1")
        hbox.pack_start(buttonOff, True, False, 0)

        buttonColor = Gtk.RadioButton.new_with_mnemonic_from_widget(buttonOff, "Color")
        buttonColor.connect("toggled", self.on_button_toggled, "2")
        hbox.pack_start(buttonColor, True, False, 0)

        buttonSync = Gtk.RadioButton.new_with_mnemonic_from_widget(buttonOff,"Sync")
        buttonSync.connect("toggled", self.on_button_toggled, "3")
        hbox.pack_start(buttonSync, True, False, 0)

        rHbox = Gtk.HBox(True, 0)
        rLabel = Gtk.Label("Red: ")
        rHbox.pack_start(rLabel,True, False,0)

        self.rScale = Gtk.HScale()
        self.rScale.set_name("red")
        self.rScale.set_range(0, 255)
        self.rScale.set_increments(1, 10)
        self.rScale.set_digits(0)
        self.rScale.set_size_request(160, 35)
        self.rScale.connect("value-changed", self.on_changed)

        gHbox = Gtk.HBox(True, 0)
        gLabel = Gtk.Label("Green: ")
        gHbox.pack_start(gLabel,True, False,0)

        self.gScale = Gtk.HScale()
        self.gScale.set_name("green")
        self.gScale.set_range(0, 255)
        self.gScale.set_increments(1, 10)
        self.gScale.set_digits(0)
        self.gScale.set_size_request(160, 35)
        self.gScale.connect("value-changed", self.on_changed)

        bHbox = Gtk.HBox(True, 0)
        bLabel = Gtk.Label("Blue: ")
        bHbox.pack_start(bLabel,True, False,0)

        self.bScale = Gtk.HScale()
        self.bScale.set_name("blue")
        self.bScale.set_range(0, 255)
        self.bScale.set_increments(1, 10)
        self.bScale.set_digits(0)
        self.bScale.set_size_request(160, 35)
        self.bScale.connect("value-changed", self.on_changed)

        vbox.pack_start(hbox, False, False, 10)
        vbox.pack_start(self.rScale, False, False, 10)
        vbox.pack_start(self.gScale, False, False, 10)
        vbox.pack_start(self.bScale, False, False, 10)


    def on_button_toggled(self, button, name):

        if button.get_active():
            state = "on"

            if name == '1':
                global kill
                self.rScale.hide();
                self.gScale.hide();
                self.bScale.hide();
                setoff()
                kill = 1

            elif name == '2' :
                global cred, cgreen,cblue
                cred = 0
                cgreen = 0
                cblue = 0
                self.rScale.show();
                self.gScale.show();
                self.bScale.show();
                self.color_reset(self.rScale,self.gScale,self.bScale)
		
                kill = 1

            elif name == '3':

                self.rScale.hide();
                self.gScale.hide();
                self.bScale.hide();
                kill = 0
                _thread.start_new_thread(Sync,())

    def on_changed(self, widget):
        val = widget.get_value()
        name = widget.get_name()
        global cred, cgreen, cblue
        if name == "red":
            cred = val
            setcolor(cred,cgreen,cblue)

        elif name == "green":
            cgreen = val
            setcolor(cred,cgreen,cblue)

        elif name == "blue":
            cblue = val
            setcolor(cred,cgreen,cblue)

        else:
            print("ERROR: Invalid widget name, in on_changed function")

    def color_reset(self,widgetr,widgetg,widgetb):
        global cred, cgreen, cblue
        cred = widgetr.get_value()
        cgreen = widgetg.get_value()
        cblue = widgetb.get_value()
        setcolor(cred,cgreen,cblue)


    def inital_show(self):
        win.show_all()
        self.rScale.hide();
        self.gScale.hide();
        self.bScale.hide();



win = LedControl()
win.connect("destroy", Gtk.main_quit)
win.inital_show()
Gtk.main()
