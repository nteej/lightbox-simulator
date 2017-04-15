import argparse
import socket
import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import QObject, pyqtSignal
from threading import Thread

class LedStripWidget(QWidget):
    labels =  []
    def __init__(self, numLed):
        super().__init__()
        self.initUI(numLed)
        
    def initUI(self, numLed):
        self.numLed = numLed
        strip = QHBoxLayout()
        strip.setSpacing(0)
        for i in range(numLed):
            label = QLabel()
            pal = QPalette()
            pal.setColor(QPalette.Background, QColor(0,0,0))
            label.setAutoFillBackground(True)
            label.setPalette(pal)
            strip.addWidget(label)
            self.labels.append(label)
        self.setLayout(strip)
    def changeColors(self,colors):
        if(len(colors) == 160):
            for i, color in enumerate(colors):
                pal = QPalette()
                pal.setColor(QPalette.Background, color)
                self.labels[i].setPalette(pal)
        else:
            print("Invalid number of Colors. Expected " + str(self.numLed) + ", got " + str(len(colors)))
        
class Networker(QObject):
    def __init__(self, port=5005, addr = "127.0.0.1"):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((addr, port))
    
    dataArrived = pyqtSignal(list)
    def sim(self):
        while(True):
            data, addr = self.sock.recvfrom(1024)
            colors = []
            for i in range (0, len(data)-2, 3): # -2 to prevent buffer overread
                colors.append(QColor(data[i],data[i+1],data[i+2]))
            self.dataArrived.emit(colors)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simulates an individually programmable LED strip (WS2801, WS2811, WS2812,...)')
    
    def positiveInt(value):
        n = int(value)
        if n <= 0:
            raise argparse.ArgumentTypeError("invalid positiveInt value: %s" % value)
        return n
    def port(value):
        n = int(value)
        if n <= 0 or n > 65535:
            raise argparse.ArgumentTypeError("invalid port number: %s" % value)
        return n
    parser.add_argument("leds", help="Number of LEDs to simulate, 1 or greater", type=positiveInt)
    parser.add_argument("-p", "--port", help="UPD Port", type=port)
    parser.add_argument("-a", "--address", help="IP to listen on")
    args = parser.parse_args()
    
    ndict = dict()
    if (args.port):
        ndict["port"] = args.port
    if(args.address):
        ndict["addr"] = args.address
    
    app = QApplication(sys.argv)

    w = LedStripWidget(args.leds)
    w.resize(250, 150)
    w.move(300, 300)
    w.setWindowTitle('Simple')
    w.show()
    
    n = Networker(**ndict)
    n.dataArrived.connect(w.changeColors)

    t = Thread(target=n.sim)
    t.daemon = True
    t.start()

    app.exec()
    
