#!/usr/bin/python3

import tkinter # note that module name has changed from Tkinter in Python 2 to tkinter in Python 3
from tkinter import filedialog
import serial
import os
import sys
import glob
from _thread import start_new_thread

#serial ports enlistment
def getSerialPorts():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result     

#print(getSerialPorts())    

#gcode sender program
def gcodeSender(port, toSendString, readyString, outputLineMethod):
    
    readyToSend = False
    
    #get the gcode lines
    toSendLines = toSendString.splitlines()
    #print(toSendLines)
    
    #report and return if the port is not open
    if not port.isOpen():
        outputLineMethod("ERROR: port not open!")
        return
    
    #flush everything    
    port.flushInput()
    port.flushOutput()
    
    #print("ready string: " + readyString)
    
    #send newline to obtain next ready character
    port.write(str.encode('\n'))
    
    def waitForReadyAndOutputLine(lineToSend):
        readString = ""
        readAChar = True
        while (readAChar) :
            readString = readString + port.read().decode()
            readyStringLength = len(readyString)
            #print("read string:" + readString)
            #print("last part of read string: " + readString[-readyStringLength:])
            if (readString[-readyStringLength:] == readyString):
                #print("ready")
                outputLineMethod(readyString, addNewLineChar = False)
                port.write(str.encode(lineToSend + '\n'))
                readAChar = False
            if (readString[-1] == '\n'):
                #do reporting & flushing here
                outputLineMethod(readString[:-1])
                readString = ""
            
    for line in toSendLines :
        waitForReadyAndOutputLine(line)    
        
    waitForReadyAndOutputLine("")
    #print("gcode sending done!")
        

port = ''
connected = False

#create window
top = tkinter.Tk()
top.title("stonetronics gcode sender tool")
iconpath = str(os.path.dirname(os.path.realpath(__file__)))+os.path.sep+'stonetronicsLogo.png'
top.iconphoto(True, tkinter.PhotoImage(file=iconpath))

#header panel

topFrame = tkinter.Frame(top)
topFrame.pack(side=tkinter.TOP)

header = tkinter.Label(topFrame, text="||          stonetronics gcode sender tool          ||", bd =3, bg= 'white')
header.pack(side = tkinter.TOP)

headerEndLine = tkinter.Frame(topFrame, height = 2, width = 400, bg = 'black')
headerEndLine.pack();

middleFrame = tkinter.Frame(top)
middleFrame.pack()

#serial settings panel

serialPortFrame = tkinter.Frame(middleFrame, bd = 1)
serialPortFrame.pack()

#header
serialPortHeader = tkinter.Label(serialPortFrame, text = '======== serial port settings ========', bd = 1, bg ='white')
serialPortHeader.pack()

#chooser for the serial port
serialPortChooserFrame = tkinter.Frame(serialPortFrame)
serialPortChooserFrame.pack()
serialPortChooserLabel = tkinter.Label(serialPortChooserFrame, text = 'serial port:')
serialPortChooserLabel.pack(side = tkinter.LEFT)

serialPortSelection = tkinter.StringVar(top)
serialPortSelection.set('')
def packOptionMenuEntries(optionMenu, *entries):
    menu = optionMenu["menu"]
    menu.delete(0,'end')
    
    for entry in entries:           
        menu.add_command(label=entry, command=lambda entry=entry: serialPortSelection.set(entry))

serialPortOptionMenu = tkinter.OptionMenu(serialPortChooserFrame, serialPortSelection, getSerialPorts())
serialPortOptionMenu.pack()

def updateSerialPortOptionMenu():
    packOptionMenuEntries(serialPortOptionMenu, getSerialPorts())
    if connected:
        port.close()
   
#update ports button
serialPortUpdaterFrame = tkinter.Frame(serialPortFrame)
serialPortUpdaterFrame.pack()
serialPortUpdaterLabel = tkinter.Label(serialPortUpdaterFrame, text ='update serial ports list')
serialPortUpdaterLabel.pack(side=tkinter.LEFT)
serialPortUpdateButton = tkinter.Button(serialPortUpdaterFrame, text = 'update' , command = updateSerialPortOptionMenu)
serialPortUpdateButton.pack(side=tkinter.RIGHT)

#set baudrate
baudRateFrame = tkinter.Frame(serialPortFrame)
baudRateFrame.pack()
baudRateLabel = tkinter.Label(baudRateFrame,text = 'baudrate:')
baudRateLabel.pack(side=tkinter.LEFT)
baudRateEntry = tkinter.Entry(baudRateFrame,bg='white')
baudRateEntry.insert(0, '115200')
baudRateEntry.pack(side=tkinter.RIGHT)

#show connection status
statusFrame =tkinter.Frame(serialPortFrame)
statusFrame.pack()
statusLabel = tkinter.Label(statusFrame,text = 'conntection status:')
statusLabel.pack(side=tkinter.LEFT)
statusIndicator = tkinter.Text(statusFrame,width=14, height = 1)
statusIndicator.insert(tkinter.END,'DISCONNECTED')
statusIndicator.pack(side=tkinter.LEFT)

#have buttons for connect/disconnect
def connect():
    global port
    try:
        port = serial.Serial(serialPortSelection.get()[2:-3], int(baudRateEntry.get())) #crude clean up of the port string
    except IOError:
        port.close()
        port.open()
        print("port was already open, closed and opened again!")
     
    #print(str(port))
    #port.open()  #port is already open by calling the constructor
    port.write(str.encode("e jungu\n"))
    #print("e man135")
    #print(port.read())
    connected = True
    statusIndicator.delete('1.0', tkinter.END)
    statusIndicator.insert(tkinter.END, 'CONNECTED')
    
    
def disconnect():
    global port
    port.close()
    connected = False
    statusIndicator.delete('1.0', tkinter.END)
    statusIndicator.insert(tkinter.END, 'DISCONNECTED')

connectFrame = tkinter.Frame(serialPortFrame)
connectFrame.pack()
connectButton = tkinter.Button(connectFrame, text = "CONNECT", command = connect)
connectButton.pack(side=tkinter.LEFT)
disconnectButton = tkinter.Button(connectFrame, text = "DISCONNECT", command = disconnect)
disconnectButton.pack(side=tkinter.RIGHT)

serialPortEndLine = tkinter.Frame(serialPortFrame, height = 2, width = 400, bg = 'black')
serialPortEndLine.pack();

#gcode settings panel

gcodeSettingsFrame = tkinter.Frame(middleFrame, bd=1, relief = tkinter.FLAT)
gcodeSettingsFrame.pack()

#header
gcodeSettingsLabel = tkinter.Label(gcodeSettingsFrame, bg='white', text = '======== gcode edit ========')
gcodeSettingsLabel.pack()

#file chooser
fileFrame = tkinter.Frame(gcodeSettingsFrame)
fileFrame.pack()
fileLabel = tkinter.Label(fileFrame, text="file:")
fileLabel.pack(side=tkinter.LEFT)
fileChooserFrame = tkinter.Frame(fileFrame)
fileChooserFrame.pack(side=tkinter.RIGHT)
selectedFilePath = ''
fileChooserEntryVar = tkinter.StringVar()
fileChooserEntry = tkinter.Entry(fileChooserFrame, textvariable = fileChooserEntryVar)
fileChooserEntry.pack(side=tkinter.LEFT)
def chooseFile():
    global selectedFilePath
    tmp = filedialog.askopenfilename(initialdir = "./", title = "select gcode file", filetypes = (("gcode files","*.gcode"),("gc files","*.gc"),("nc files","*.nc"), ("all files","*.*")))
    fileChooserEntry.delete(0, tkinter.END)
    fileChooserEntry.insert(tkinter.INSERT, tmp)
    selectedFilePath = tmp #tkinter seems to overwrite the selectedFilePath somehow, so it gets set again here
  
def loadFile():
    global selectedFilePath
    selectedFilePath = fileChooserEntryVar.get()
    fileDisplayText.delete("1.0", tkinter.END)
    gcodeFile = open(selectedFilePath, 'r')
    fileDisplayText.insert(tkinter.INSERT, gcodeFile.read())
    gcodeFile.close()
    
def saveFile():
    global selectedFilePath
    selectedFilePath = fileChooserEntryVar.get()
    gcodeFile = open(selectedFilePath, 'w')
    fileContent = fileDisplayText.get("1.0", "end-1c")
    gcodeFile.write(fileContent)
    gcodeFile.close()
    
#buttons for browse, load and save
fileChooserButtonsFrame = tkinter.Frame(fileChooserFrame)
fileChooserButtonsFrame.pack(side = tkinter.RIGHT)
browseButton = tkinter.Button(fileChooserButtonsFrame, text = 'browse...', command = chooseFile)
browseButton.pack(side=tkinter.LEFT)
fileChooserLoadSaveButtonsFrame = tkinter.Frame(fileChooserButtonsFrame)
fileChooserLoadSaveButtonsFrame.pack(side = tkinter.RIGHT)
loadButton = tkinter.Button(fileChooserLoadSaveButtonsFrame, text = 'load', command = loadFile)
loadButton.pack(side=tkinter.LEFT)
saveButton = tkinter.Button(fileChooserLoadSaveButtonsFrame, text = 'save', command = saveFile)
saveButton.pack(side = tkinter.RIGHT)    

#file display
fileDisplayFrame = tkinter.Frame(gcodeSettingsFrame)
fileDisplayFrame.pack()
fileDisplayLabel = tkinter.Label(fileDisplayFrame, text = "Loaded gcode file: ")
fileDisplayLabel.pack(side = tkinter.TOP)
fileDisplayFieldFrame = tkinter.Frame(fileDisplayFrame)
fileDisplayFieldFrame.pack()
fileDisplayScrollbar = tkinter.Scrollbar(fileDisplayFieldFrame)
fileDisplayText = tkinter.Text(fileDisplayFieldFrame, height = 20, width = 50)
fileDisplayScrollbar.pack(side = tkinter.RIGHT, fill = tkinter.Y)
fileDisplayText.pack(side = tkinter.LEFT, fill = tkinter.Y)
fileDisplayScrollbar.config(command = fileDisplayText.yview)
fileDisplayText.config(yscrollcommand = fileDisplayScrollbar.set)



#gcode sender panel
bottomFrame = tkinter.Frame(top)
bottomFrame.pack()

bottomFrameLine = tkinter.Frame(bottomFrame, height = 2, width = 400, bg = 'black')
bottomFrameLine.pack();

#header
bottomFrameHeader = tkinter.Label(bottomFrame, text = "======= gcode send ========", bg = "white")
bottomFrameHeader.pack()

#select character that indicates ready on th the machine
readyCharacterFrame = tkinter.Frame(bottomFrame)
readyCharacterFrame.pack()
readyCharacterLabel = tkinter.Label(readyCharacterFrame,text = '"ready" character:')
readyCharacterLabel.pack(side=tkinter.LEFT)
readyCharacterEntry = tkinter.Entry(readyCharacterFrame,bg='white')
readyCharacterEntry.insert(0, '>')
readyCharacterEntry.pack(side=tkinter.RIGHT)


#console output update program
def updateConsoleOutput(newLine, addNewLineChar = True):
    autoscroll = autoScrollVar.get()
    consoleOutputText.configure(state='normal')
    consoleOutputText.insert(tkinter.END, newLine + ("","\n")[addNewLineChar] )
    if autoscroll:
        consoleOutputText.see(tkinter.END)
    consoleOutputText.configure(state='disabled')
    
#function call for the button
def sendGcode():
    global port
    fileAsString=str(fileDisplayText.get("1.0", "end-1c"))
    #print("De fayle es a string: " + fileAsString)
    
    start_new_thread(gcodeSender, ( port, fileAsString, readyCharacterEntry.get(), updateConsoleOutput))

#send button
sendButtonFrame = tkinter.Frame(bottomFrame)
sendButtonFrame.pack()
sendButtonLabel = tkinter.Label(sendButtonFrame, text='send gcode to machine ')
sendButtonLabel.pack(side=tkinter.LEFT)
sendButton = tkinter.Button(sendButtonFrame, text = 'send', command = sendGcode)
sendButton.pack(side=tkinter.RIGHT)

#console output
consoleOutputFrame = tkinter.Frame(bottomFrame)
consoleOutputFrame.pack()
consoleOutputHeader = tkinter.Label(consoleOutputFrame, text ='console output:')
consoleOutputHeader.pack(side = tkinter.TOP)
consoleOutputTextFrame = tkinter.Frame(consoleOutputFrame)
consoleOutputTextFrame.pack(side = tkinter.BOTTOM)
consoleOutputText = tkinter.Text(consoleOutputTextFrame, height = 10, width = 50)
consoleOutputText.pack(side = tkinter.LEFT, fill = tkinter.Y)
consoleOutputScrollbar = tkinter.Scrollbar(consoleOutputTextFrame)
consoleOutputScrollbar.pack(side = tkinter.RIGHT, fill = tkinter.Y)
consoleOutputScrollbar.config(command = consoleOutputText.yview)
consoleOutputText.config(yscrollcommand = consoleOutputScrollbar.set)

#autoscroll check button
autoScrollVar = tkinter.IntVar()
autoscrollFrame = tkinter.Frame(bottomFrame)
autoscrollFrame.pack()
autoScrollCheckButton = tkinter.Checkbutton(autoscrollFrame, text ="autoscroll", variable = autoScrollVar)
autoScrollCheckButton.pack()

  
   
#def debugAction():
#    print("The file is " + selectedFilePath)
    
#debugButton = tkinter.Button(top, text = 'DEBUG', command = debugAction)
#debugButton.pack(side=tkinter.BOTTOM)



top.mainloop()
