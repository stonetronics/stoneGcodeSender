#!/usr/bin/python3

# This was built after this tutorial: https://pythonprogramming.net/how-to-embed-matplotlib-graph-tkinter-gui/
# License: http://creativecommons.org/licenses/by-sa/3.0/	

import os

import matplotlib
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg #, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

import tkinter as tk
from tkinter import ttk, filedialog


class FileChooser(tk.Frame):
           
    def __init__(self, parent, labeltext = "File:", types = (("gcode files","*.gcode"), ("all files","*.*")) ):
        tk.Frame.__init__(self, parent)
        self.types = types
        
        self.filepathLabel = tk.Label(self, text = labeltext)
        self.filepathLabel.grid(row = 0, column = 0)
        
        self.filepathEntry = tk.Entry(self)
        self.filepathEntry.grid(row = 0, column = 1)
        
        self.browseButton = tk.Button(self, text = "browse...", command = self.browseFile)
        self.browseButton.grid(row = 0, column = 2)

    def browseFile(self):
        tmp = filedialog.askopenfilename(initialdir = "./", title = "select gcode file", filetypes = self.types)
        self.filepathEntry.delete(0, tk.END) #delete and overwrite the set filename
        self.filepathEntry.insert(tk.INSERT, tmp)     
        self.filepathEntry.xview("end") #scroll to the back so the filename can be read better      
    
    def getFilePath(self):
        return self.filepathEntry.get()

class GcodeDisplayApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)

        #iconpath = str(os.path.dirname(os.path.realpath(__file__)))+os.path.sep+'stonetronicsLogo.png'
        #tk.Tk.iconphoto(True, tk.PhotoImage(file=iconpath))
        tk.Tk.wm_title(self, "Gcode Display")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        filechooserFrame = tk.Frame(container)
        filechooserFrame.pack()
        self.filechooser = FileChooser(filechooserFrame)
        self.filechooser.pack(side = tk.LEFT)
        
        def update():
            gcode = extractGcode(self.filechooser.getFilePath())
            self.diagramFrame.plot(gcode)
        self.plotButton = tk.Button(filechooserFrame, text = "load", command = update)
        self.plotButton.pack(side = tk.RIGHT)

        self.diagramFrame = DiagramFrame(container)
        self.diagramFrame.pack(side="top",fill='both',expand=True)

        
class DiagramFrame(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self,parent)
                
        label = tk.Label(self, text="Gcode Diagram", font=("Verdana", 12))
        label.pack(pady=10,padx=10)


        self.f = Figure(figsize=(8,8), dpi=100)
        self.a = self.f.add_subplot(111)
        self.a.plot(0, 0, 'r')
        self.a.plot(0, 0, 'g')  
        self.a.axis("equal")    
        self.a.grid(color='grey', linestyle='-', linewidth=0.5)
        self.a.legend(["XY", "UV"])  

        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        #toolbar = NavigationToolbar2TkAgg(canvas, self)
        #toolbar.update()
        #canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    def plot(self, data):
        self.a.clear()
        self.a.plot(data.X, data.Y, 'r')
        self.a.plot(data.U, data.V, 'g')  
        self.a.axis("equal")    
        self.a.grid(color='grey', linestyle='-', linewidth=0.5)
        self.a.legend(["XY", "UV"])  

        self.canvas.draw()
        

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
    

    
def extractGcode(gcodeFile):
    f = open(gcodeFile, "r")
    
    data = Data()
    
    #extract positions out of gcode
    integralPosition = [0.0,0.0,0.0,0.0]
    mode = 'abs'
    for line in f.readlines() :

        if (line[0:3] == 'G28') : #home
            integralPosition = [0,0,0,0]
            data.X.append(integralPosition[0])
            data.Y.append(integralPosition[1])
            data.U.append(integralPosition[2])
            data.V.append(integralPosition[3])
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
            data.X.append(parseFloatNumber(line, 'X'))
            data.Y.append(parseFloatNumber(line, 'Y'))
            data.U.append(parseFloatNumber(line, 'U'))
            data.V.append(parseFloatNumber(line, 'V'))
        else :
            integralPosition[0] = integralPosition[0] + parseFloatNumber(line, 'X')
            integralPosition[1] = integralPosition[1] + parseFloatNumber(line, 'Y')
            integralPosition[2] = integralPosition[2] + parseFloatNumber(line, 'U')
            integralPosition[3] = integralPosition[3] + parseFloatNumber(line, 'V')
            data.X.append(integralPosition[0])
            data.Y.append(integralPosition[1])
            data.U.append(integralPosition[2])
            data.V.append(integralPosition[3])
            
        #print(self.data.X)
        #print(self.data.Y)
        #print(self.data.U)
        #print(self.data.V)
    f.close()
    
    return data
        
app = GcodeDisplayApp()
app.mainloop() 


