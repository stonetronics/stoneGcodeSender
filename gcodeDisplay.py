#!/usr/bin/python3

# This was built after this tutorial: https://pythonprogramming.net/how-to-embed-matplotlib-graph-tkinter-gui/
# License: http://creativecommons.org/licenses/by-sa/3.0/	

import os

import matplotlib
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

import tkinter as tk
from tkinter import ttk


class GcodeDisplayApp(tk.Tk):

    def __init__(self, data, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)

        #iconpath = str(os.path.dirname(os.path.realpath(__file__)))+os.path.sep+'stonetronicsLogo.png'
        #tk.Tk.iconphoto(True, tk.PhotoImage(file=iconpath))
        tk.Tk.wm_title(self, "Gcode Display")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        diagramFrame = DiagramFrame(container, data)
        diagramFrame.pack(side="top",fill='both',expand=True)

        
class DiagramFrame(tk.Frame):

    def __init__(self, parent, data):
        tk.Frame.__init__(self,parent)
                
        label = tk.Label(self, text="Gcode Diagram", font=("Verdana", 12))
        label.pack(pady=10,padx=10)


        f = Figure(figsize=(8,8), dpi=100)
        a = f.add_subplot(111)
        a.plot(data.X, data.Y, 'r')
        a.plot(data.U, data.V, 'g')  
        a.axis("equal")    
        a.grid(color='grey', linestyle='-', linewidth=0.5)
        a.legend(["XY", "UV"])  

        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

class Data:
    X = []
    Y = []
    U = []
    V = []

#parse a float number with a key
def parseFloatNumber(string, key) :
    start = string.find(key) + 1
    end = string.find(' ', start)
    if not (start == 0) : #if the number at the key has been found
        return float(string[start:end])
    else :
        return 0
    

class GcodeDisplay:
    
    def __init__(self, *args, **kwargs):
        if not "gcode" in kwargs:
            print ("no gcode provided. returning...")
            return
        
        self.data = Data()
        
        #extract positions out of gcode
        integralPosition = [0.0,0.0,0.0,0.0]
        mode = 'abs'
        for line in kwargs["gcode"].splitlines() :
            
            if (line[0:3] == 'G28') : #home
                integralPosition = [0,0,0,0]
                self.data.X.append(integralPosition[0])
                self.data.Y.append(integralPosition[1])
                self.data.U.append(integralPosition[2])
                self.data.V.append(integralPosition[3])
                continue
                
            if (line[0:3] == 'G90') : #absolute mode
                mode = 'abs'
                continue
                
            if (line[0:3] == 'G91') : #relative mode
                mode = 'rel'
                continue
                
            if not ((line[0:3] == 'G00') or (line[0:3] == 'G01')) :
                continue
            
            if (mode == 'abs') : 
                self.data.X.append(parseFloatNumber(line, 'X'))
                self.data.Y.append(parseFloatNumber(line, 'Y'))
                self.data.U.append(parseFloatNumber(line, 'U'))
                self.data.V.append(parseFloatNumber(line, 'V'))
            else :
                integralPosition[0] = integralPosition[0] + parseFloatNumber(line, 'X')
                integralPosition[1] = integralPosition[1] + parseFloatNumber(line, 'Y')
                integralPosition[2] = integralPosition[2] + parseFloatNumber(line, 'U')
                integralPosition[3] = integralPosition[3] + parseFloatNumber(line, 'V')
                self.data.X.append(integralPosition[0])
                self.data.Y.append(integralPosition[1])
                self.data.U.append(integralPosition[2])
                self.data.V.append(integralPosition[3])
                
            #print(self.data.X)
            #print(self.data.Y)
            #print(self.data.U)
            #print(self.data.V)
            
        app = GcodeDisplayApp(self.data)
        app.mainloop() 

#f = open("testFile2.gcode", "r")

#GcodeDisplay(gcode = f.read())

#f.close()
