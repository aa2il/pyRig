#! /usr/bin/python3 -u
############################################################################
#
# pyRig.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Gui for remote rig & rotor control.  This is rather primative right now.
# Flrig is much better but I mainly want a rotor controller.  Need to spend
# more time flushing out flrig.
#
############################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
############################################################################

from __future__ import print_function
import sys
if False:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import QTimer
else:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import QTimer
import argparse
from pprint import pprint
import rig_io.socket_io as socket_io
from rig_io.ft_tables import bands
import functools
from rig_common import *
from rig_control import *
from rotor_control import *
from keypad import *
from watchdog import *
from settings import *

################################################################################

# Structure to contain processing params
class PARAMS:
    def __init__(self):

        # Process command line args
        # Can add required=True to anything that is required
        arg_proc = argparse.ArgumentParser()
        arg_proc.add_argument("-rig", help="Rig connection Type",
                      type=str,default="ANY",
                      choices=['FLDIGI','FLRIG','DIRECT','HAMLIB','ANY','NONE'])
        arg_proc.add_argument("-port", help="Rig connection Port",
                              type=int,default=0)
        arg_proc.add_argument("-rotor", help="Rotor connection Type",
                      type=str,default="NONE",
                      choices=['HAMLIB','NONE'])
        arg_proc.add_argument("-port2", help="Rotor onnection Port",
                              type=int,default=0)
        args = arg_proc.parse_args()

        self.RIG_CONNECTION   = args.rig
        self.PORT             = args.port
        self.ROTOR_CONNECTION = args.rotor
        self.PORT2            = args.port2
        if self.ROTOR_CONNECTION=='HAMLIB' and self.PORT2==0:
            self.PORT2        = 4533
        
        self.PANADAPTOR       = False

        # Read config file
        self.RCFILE=os.path.expanduser("~/.pyRigrc")
        self.SETTINGS=None
        try:
            with open(self.RCFILE) as json_data_file:
                self.SETTINGS = json.load(json_data_file)
        except:
            print(self.RCFILE,' not found - need call!\n')
            s=SETTINGS(None,self)
            while not self.SETTINGS:
                try:
                    s.win.update()
                except:
                    pass
                time.sleep(.01)
            print('Settings:',self.SETTINGS)

        #sys,exit(0)

        
################################################################################

# The top-level GUI 
class pyRIG_GUI(QMainWindow):
    def __init__(self,P):
        super(pyRIG_GUI, self).__init__()
        self.P=P

        self.win = QWidget()
        self.win.setWindowTitle("pyRig by AA2IL")
        #self.win.resize(600, 400)
        self.grid = QGridLayout()
        self.win.setLayout(self.grid)
        self.win.show()
        
        # Create holder for tabs
        row=0
        col=0
        self.tabs = QTabWidget()
        self.grid.addWidget(self.tabs, row,col)

        # Add button to exit
        row+=1
        col=0
        self.btn2 = QPushButton('Quit') 
        self.btn2.setToolTip('Click to Quit')
        self.btn2.clicked.connect(exit)
        self.grid.addWidget(self.btn2,row,col,1,1)
        
        # Tab for most common rig function
        self.rig_common = RIG_COMMON(self.tabs,P)
        
        # Tab to control rig in more detail
        self.rig_ctrl = RIG_CONTROL(self.tabs,P)

        # Tab to control vfos in more detail
        self.rig_vfos = RIG_VFOS(self.tabs,P)

        # Tab for the key pad
        if self.P.sock.rig_type2=='FTdx3000' or self.P.sock.rig_type2=='FT991a':
            self.key_pad = KEY_PAD(self.tabs,P)

        # Tab to control rotor
        self.rotor_ctrl = ROTOR_CONTROL(self.tabs,P)
        if not P.sock.active:
            self.tabs.setCurrentIndex(self.tabs.count()-1)

################################################################################

if __name__ == '__main__':
    print("\n\n***********************************************************************************")
    print("\nStarting pyRig  ...")
    P=PARAMS()
    print("\nP=",end=' ')
    pprint(vars(P))

    # Open connection to rig
    P.sock = socket_io.open_rig_connection(P.RIG_CONNECTION,0,P.PORT,0,'RIG')
    if not P.sock.active and P.sock.connection!='NONE':
        print('*** No connection available to rig ***')
        sys.exit(0)
    else:
        print('Opened socket to:',P.sock.rig_type,P.sock.rig_type1,P.sock.rig_type2)

    # Open connection to rotor
    P.sock2 = socket_io.open_rig_connection(P.ROTOR_CONNECTION,0,P.PORT2,0,'ROTOR')
    if not P.sock2.active and P.sock2.connection!='NONE':
        print('*** No connection available to rotor ***')
        sys.exit(0)

    # Create application and gui
    P.app     = QApplication(sys.argv)
    P.monitor = WatchDog(P,2000)
    P.gui     = pyRIG_GUI(P)

    # Event loop
    sys.exit(P.app.exec_())

