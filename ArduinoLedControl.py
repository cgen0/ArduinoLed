import gi
import _thread
import mss.tools
import pyfirmata
import time
import struct
import subprocess
import psutil, os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from PIL import Image
from numpy import *


board = pyfirmata.Arduino('/dev/ttyUSB0', timeout=1)
r = board.get_pin('d:9:o')
g = board.get_pin('d:10:o')
b = board.get_pin('d:11:o')
r.mode = pyfirmata.PWM
g.mode = pyfirmata.PWM
b.mode = pyfirmata.PWM

INTERVAL=0.300
cred=0
cgreen=0
cblue=0
chue=0
kill=0
tiny=0.1
RAW_TARGERT = "/tmp/cava.fifo"
BARS_NUMBER = 1
OUTPUT_BIT_FORMAT = "8bit"
bytetype, bytesize, bytenorm = ("H", 2, 65535) if OUTPUT_BIT_FORMAT == "16bit" else ("B", 1, 255)






def hsv2rgb(h, s, v):
    h = float(h)
    s = float(s)
    v = float(v)
    h60 = h / 60.0
    h60f = math.floor(h60)
    hi = int(h60f) % 6
    f = h60 - h60f
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = 0, 0, 0
    if hi == 0: r, g, b = v, t, p
    elif hi == 1: r, g, b = q, v, p
    elif hi == 2: r, g, b = p, v, t
    elif hi == 3: r, g, b = p, q, v
    elif hi == 4: r, g, b = t, p, v
    elif hi == 5: r, g, b = v, p, q
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return r, g, b

def most_frequent_colour(image):
    w, h = image.size

    image = image.resize((w, h))
    result = image.convert('P', palette=Image.ADAPTIVE, colors=1)
    color = result.convert('RGB').load()[1,1]
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

#def convertHSL(h,l,s):


def SyncMode():
    red = 0
    green = 0
    blue = 0

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

def AudioMode():

    for proc in psutil.process_iter():
        # kill others cava process
        if proc.name() == "cava":
            proc.kill()

    cava = subprocess.Popen(["cava"])
    fifo = open(RAW_TARGERT, "rb")
    chunk = bytesize * BARS_NUMBER
    fmt = bytetype * BARS_NUMBER
    oldsample=0
    while kill == 3:
        data = fifo.read(chunk)
        new_sample = [i / bytenorm for i in struct.unpack(fmt, data)][0]
        sample = tiny * new_sample + (1.0 - tiny) * oldsample
        oldsample=sample
        r, g, b = hsv2rgb(chue,1,sample)
        setred(r)
        setgreen(g)
        setblue(b)
    #kill cava process
    print(cava.pid)
    os.system('pkill ' + str(cava.pid) + " --signal 9")
    setoff()

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
    setoff()

def on_changed(widget):

    val = widget.get_value()
    name = widget.get_name()
    if name == "red":
        global cred
        cred = val
        setred(cred)

    elif name == "green":
        global cgreen
        cgreen = val
        setgreen(cgreen)

    elif name == "blue":
        global cblue
        cblue = val
        setblue(cblue)

    elif name == "hue":
        global chue
        chue = val


    else:
        print("ERROR: Invalid widget name, in on_changed function")

def color_reset( widgetr, widgetg , widgetb):

    global cred, cgreen, cblue
    cred = widgetr.get_value()
    cgreen = widgetg.get_value()
    cblue = widgetb.get_value()
    setcolor(cred, cgreen, cblue)





class LedControl(Gtk.Window):


    def __init__(self):

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
        buttonOff.connect("toggled", self.on_button_toggled, "off")
        hbox.pack_start(buttonOff, True, False, 0)

        buttonColor = Gtk.RadioButton.new_with_mnemonic_from_widget(buttonOff, "Color")
        buttonColor.connect("toggled", self.on_button_toggled, "clr")
        hbox.pack_start(buttonColor, True, False, 0)

        buttonSync = Gtk.RadioButton.new_with_mnemonic_from_widget(buttonOff,"Sync")
        buttonSync.connect("toggled", self.on_button_toggled, "syn")
        hbox.pack_start(buttonSync, True, False, 0)

        buttonFade = Gtk.RadioButton.new_with_mnemonic_from_widget(buttonOff, "Fade")
        buttonFade.connect("toggled", self.on_button_toggled, "fde")
        hbox.pack_start(buttonFade, True, False, 0)

        buttonAudio = Gtk.RadioButton.new_with_mnemonic_from_widget(buttonOff, "Audio")
        buttonAudio.connect("toggled", self.on_button_toggled, "aud")
        hbox.pack_start(buttonAudio, True, False, 0)






        rHbox = Gtk.HBox(homogeneous=True, spacing=0)
        rLabel = Gtk.Label(label="Red: ")
        rHbox.pack_start(rLabel,True, False,0)

        self.rScale = Gtk.HScale()
        self.rScale.set_name(name="red")
        self.rScale.set_range(0, 255)
        self.rScale.set_increments(1, 10)
        self.rScale.set_digits(0)
        self.rScale.set_size_request(160, 35)
        self.rScale.connect("value-changed", on_changed)

        gHbox = Gtk.HBox(homogeneous=True, spacing=0)
        gLabel = Gtk.Label(label="Green: ")
        gHbox.pack_start(gLabel,True, False,0)

        self.gScale = Gtk.HScale()
        self.gScale.set_name(name="green")
        self.gScale.set_range(0, 255)
        self.gScale.set_increments(1, 10)
        self.gScale.set_digits(0)
        self.gScale.set_size_request(160, 35)
        self.gScale.connect("value-changed", on_changed)

        bHbox = Gtk.HBox(homogeneous=True, spacing=0)
        bLabel = Gtk.Label(label="Blue: ")
        bHbox.pack_start(bLabel,True, False,0)

        self.bScale = Gtk.HScale()
        self.bScale.set_name(name="blue")
        self.bScale.set_range(0, 255)
        self.bScale.set_increments(1, 10)
        self.bScale.set_digits(0)
        self.bScale.set_size_request(160, 35)
        self.bScale.connect("value-changed", on_changed)

        hueHbox = Gtk.HBox(homogeneous=True, spacing=0)
        hueLabel = Gtk.Label(label="Hue: ")
        hueHbox.pack_start(hueLabel, True, False, 0)

        self.hueScale = Gtk.HScale()
        self.hueScale.set_name(name="hue")
        self.hueScale.set_range(0, 360)
        self.hueScale.set_increments(1, 10)
        self.hueScale.set_digits(0)
        self.hueScale.set_size_request(160, 35)
        self.hueScale.connect("value-changed", on_changed)

        vbox.pack_start(hbox, False, False, 10)
        vbox.pack_start(self.rScale, False, False, 10)
        vbox.pack_start(self.gScale, False, False, 10)
        vbox.pack_start(self.bScale, False, False, 10)
        vbox.pack_start(self.hueScale, False, False, 10)




    def on_button_toggled(self, button, name):
        global kill

        if button.get_active():

            if name == 'off':
                self.rScale.hide()
                self.gScale.hide()
                self.bScale.hide()
                self.hueScale.hide()
                kill = 0
                setoff()

            elif name == 'clr':
                kill = 0
                self.rScale.show()
                self.gScale.show()
                self.bScale.show()
                self.hueScale.hide()
                time.sleep(0.03)
                color_reset(self.rScale,self.gScale,self.bScale)


            elif name == 'syn':

                self.rScale.hide()
                self.gScale.hide()
                self.bScale.hide()
                self.hueScale.hide()
                kill = 1
                _thread.start_new_thread(SyncMode,())

            elif name == 'fde':

                self.rScale.hide()
                self.gScale.hide()
                self.bScale.hide()
                self.hueScale.hide()
                kill = 2
                setoff()
                _thread.start_new_thread(FadeMode,())

            elif name == 'aud':

                self.rScale.hide()
                self.gScale.hide()
                self.bScale.hide()
                self.hueScale.show()
                kill = 3
                setoff()
                _thread.start_new_thread(AudioMode,())





    def inital_show(self):
        win.show_all()
        self.hueScale.hide()
        self.rScale.hide()
        self.gScale.hide()
        self.bScale.hide()



win = LedControl()
win.connect("destroy", Gtk.main_quit)
win.inital_show()
Gtk.main()

