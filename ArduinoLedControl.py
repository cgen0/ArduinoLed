
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import _thread
import mss.tools
import pyfirmata
import time
from PIL import Image

board = pyfirmata.Arduino('/dev/ttyUSB0')
r = board.get_pin('d:9:o')
g = board.get_pin('d:10:o')
b = board.get_pin('d:11:o')
r.mode = pyfirmata.PWM
g.mode = pyfirmata.PWM
b.mode = pyfirmata.PWM

INTERVAL=0.5





def most_frequent_colour(image):
    w, h = image.size

    image = image.resize((w, h))
    result = image.convert('P', palette=Image.ADAPTIVE, colors=1)
    result.putalpha(0)
    colors = result.getcolors((w) * (h))


    for count, col in colors:
        color=col
    return color


def setcolor(red,green,blue):
    red,green,blue = convert(red,green,blue)
    r.write(red)
    g.write(green/1.2442)
    b.write(blue/1.8433)


def setred(red):
    red = red / 255.0
    r.write(red)


def setgreen(green):

    green = green / 255.0
    g.write(green/1.2442)


def setblue(blue):

    blue = blue / 255.0
    b.write(blue/1.8433)


def setoff():
    r.write(0)
    g.write(0)
    b.write(0)


def fade(red, green, blue, oldred, oldgreen, oldblue):
    tupr=(red, oldred,'r')
    tupg=(green, oldgreen,'g')
    tupb=(blue, oldblue,'b')
    _thread.start_new_thread(fadethread,tupr)
    _thread.start_new_thread(fadethread, tupg)
    _thread.start_new_thread(fadethread, tupb)
    return

def fadesingle(old,new,channel):
    if (old-new)== 0:
        return
    Sleep=0.04
    while old != new:
            if old < new:
                old += 1
            elif old > new:
                old -= 1
            if kill != 2:
                old=0
                setred(old)
                setgreen(old)
                setblue(old)
                return

            else:
                time.sleep(Sleep)

            if channel == "r":
                setred(old)
            elif channel == "g":
                setgreen(old)
            elif channel == "b":
                setblue(old)


def fadethread(new, old,flag):

    if (old-new)== 0:
        return
    Sleep=INTERVAL/abs(old-new)
    if flag=='r':
        while old!= new:
            if old< new:
                old+= 1
            elif old> new:
                old-= 1
            time.sleep(Sleep)
            setred(old)
    if flag=='g':
        while old!= new:
            if old< new:
                old+= 1
            elif old> new:
                old-= 1
            time.sleep(Sleep)
            setgreen(old)
    if flag=='b':
        while old!= new:
            if old< new:
                old+= 1
            elif old> new:
                old-= 1
            time.sleep(Sleep)
            setblue(old)
    return



def convert(r,g,b):

    r= r/ 255.0
    g= g/ 255.0
    b= b/ 255.0
    return r,g,b

def Sync():
    red = 0
    green = 0
    blue = 0

    im = Image.open('temp.png')
    with mss.mss() as sct:
        while kill == 1:
            monitor = {"top": 780, "left": 0, "width": 1920, "height": 300}
            sct_img = sct.grab(monitor)
            im = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            oldred = red
            oldgreen=green
            oldblue=blue
            color = most_frequent_colour(im)
            red = color[0]
            green = color[1]
            blue = color[2]
            fade(red,green,blue,oldred,oldgreen,oldblue)
            time.sleep(INTERVAL)
    return

def on_changed(widget):
    global cred, cgreen, cblue

    val = widget.get_value()
    name = widget.get_name()
    if name == "red":
        cred = val
        setred(cred)

    elif name == "green":
         cgreen = val
         setgreen(cgreen)

    elif name == "blue":
        cblue = val
        setblue(cblue)

    else:
        print("ERROR: Invalid widget name, in on_changed function")

def color_reset( widgetr, widgetg , widgetb):
    global cred, cgreen, cblue
    cred = widgetr.get_value()
    cgreen = widgetg.get_value()
    cblue = widgetb.get_value()
    print(type(cred))
    setcolor(cred, cgreen, cblue)



def FadeMode():
    oldred = 0
    oldgreen=0
    oldblue =0
    blue=0
    green=0

    red = 255

    fadesingle(oldred, red, "r")

    oldred = red

    while kill==2:
        green = 255

        if kill != 2:
            return

        fadesingle(oldgreen, green, "g")

        if kill != 2:

            return

        oldgreen=green
        red=0

        fadesingle(oldred, red, "r")

        if kill != 2:
            return

        oldred=red
        blue=255

        fadesingle(oldblue, blue,"b")

        if kill != 2:
            return

        oldblue=blue
        green = 0

        fadesingle(oldgreen, green, "g")

        if kill != 2:
            return

        oldgreen = green
        red = 255

        fadesingle(oldred, red, "r")

        if kill != 2:
            return

        oldred = red
        blue=0


        fadesingle(oldblue, blue,"b")

        if kill != 2:
            return

        oldblue=blue

class LedControl(Gtk.Window):


    def __init__(self):
        cred=0
        cgreen=0
        cblue=0
        kill=0
        Gtk.Window.__init__(self, title="LED Control")
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(10)
        self.set_size_request(400,200)
        self.set_resizable(False)
        vbox = Gtk.VBox()
        hbox = Gtk.Box(spacing=6)
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

        buttonFade = Gtk.RadioButton.new_with_mnemonic_from_widget(buttonOff, "Fade")
        buttonFade.connect("toggled", self.on_button_toggled, "4")
        hbox.pack_start(buttonFade, True, False, 0)

        rHbox = Gtk.HBox(True, 0)
        rLabel = Gtk.Label("Red: ")
        rHbox.pack_start(rLabel,True, False,0)

        self.rScale = Gtk.HScale()
        self.rScale.set_name("red")
        self.rScale.set_range(0, 255)
        self.rScale.set_increments(1, 10)
        self.rScale.set_digits(0)
        self.rScale.set_size_request(160, 35)
        self.rScale.connect("value-changed", on_changed)

        gHbox = Gtk.HBox(True, 0)
        gLabel = Gtk.Label("Green: ")
        gHbox.pack_start(gLabel,True, False,0)

        self.gScale = Gtk.HScale()
        self.gScale.set_name("green")
        self.gScale.set_range(0, 255)
        self.gScale.set_increments(1, 10)
        self.gScale.set_digits(0)
        self.gScale.set_size_request(160, 35)
        self.gScale.connect("value-changed", on_changed)

        bHbox = Gtk.HBox(True, 0)
        bLabel = Gtk.Label("Blue: ")
        bHbox.pack_start(bLabel,True, False,0)

        self.bScale = Gtk.HScale()
        self.bScale.set_name("blue")
        self.bScale.set_range(0, 255)
        self.bScale.set_increments(1, 10)
        self.bScale.set_digits(0)
        self.bScale.set_size_request(160, 35)
        self.bScale.connect("value-changed", on_changed)

        vbox.pack_start(hbox, False, False, 10)
        vbox.pack_start(self.rScale, False, False, 10)
        vbox.pack_start(self.gScale, False, False, 10)
        vbox.pack_start(self.bScale, False, False, 10)


    def on_button_toggled(self, button, name):
        global kill

        if button.get_active():

            if name == '1':
                self.rScale.hide()
                self.gScale.hide()
                self.bScale.hide()
                kill = 0
                setoff()

            elif name == '2' :
                kill = 0
                self.rScale.show()
                self.gScale.show()
                self.bScale.show()
                time.sleep(0.03)
                color_reset(self.rScale,self.gScale,self.bScale)


            elif name == '3':

                self.rScale.hide()
                self.gScale.hide()
                self.bScale.hide()
                kill = 1
                _thread.start_new_thread(Sync,())

            elif name == '4':

                self.rScale.hide()
                self.gScale.hide()
                self.bScale.hide()
                kill = 2
                setoff()
                _thread.start_new_thread(FadeMode,())






    def inital_show(self):
        win.show_all()
        self.rScale.hide()
        self.gScale.hide()
        self.bScale.hide()



win = LedControl()
win.connect("destroy", Gtk.main_quit)
win.inital_show()
Gtk.main()
