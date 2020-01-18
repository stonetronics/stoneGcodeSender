# stoneGcodeSender
A very basic gcode editing and sending tool, written in python3, using tkinter for a gui

tested on ubuntu 18, but 'should' run on all os

This is a gcode sender utility. As i suprisingly couldn't find a tool that just sends gcode files line by line over a serial port, i wrote this python script that helps with the process.

The script basically just takes a gcode file and sends it, but with fancy gui and gcode editing capabilities.

make sure to install the tkinter library for using this tool

A serial port for usage can be selected and opened.
The gcode file that is to be sent can be opened, viewed and edited before sending
A "ready" character can be specified. this is the character or string the machine sends when it is ready to accept input
By pushing the send button, the gcode in the edit window will be sent to the machine and the output will be displayed in an output field.

There is also a gcode viewer script that displays the gcode in the specified file. (needs matplotlib to work). edit the path in the python file to select a gcode file

feel free to edit
