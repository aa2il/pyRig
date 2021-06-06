############################################################################
#
# rotor_control.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Portion of GUI related to rotor controls
#
# To Do - there are other versions of this in this suite - combine them.
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

if False:
    # use Qt4 
    from PyQt4.QtCore import * 
else:
    # use Qt5
    from PyQt5.QtCore import * 
    from PyQt5.QtWidgets import *
from rig_io.socket_io import *
from widgets import *
try:
    from pyhamtools.locator import calculate_heading
    bearing_ok=True
except:
    bearing_ok=False

################################################################################

class ROTOR_CONTROL():
    def __init__(self,parent,P,new_tab=True):
        self.P    = P
        self.sock = P.sock2
        if self.sock.connection == 'NONE':
            return None

        # Create a new tab or window
        self.tab = QWidget()
        if new_tab:
            parent.addTab(self.tab,'Rotor')
            self.visible = True
        else:
            self.tab.hide()
            self.visible = False
            self.tab.setWindowTitle("Rotor")
        self.grid = QGridLayout()
        self.tab.setLayout(self.grid)

        # Add Az controls - top is desired, bottom is actual
        row=0
        col=0
        lb=QLabel("Azimuth:")
        self.grid.addWidget(lb,row,col)
        self.direction = QLineEdit()
        self.direction.setAlignment(Qt.AlignCenter)
        self.grid.addWidget(self.direction,row,col+1,1,3)

        row+=1
        ndigits=3           # -180 to +180
        ndec=0
        self.azlcd1 = MyLCDNumber(self.tab,ndigits,ndec,True,True,wheelCB=None)
        xs=200
        ys=80
        #self.azlcd1.setFixedSize(xs,ys)
        self.azlcd1.adjustSize()
        self.grid.addWidget(self.azlcd1,row,col,2,4)
        #self.grid.addWidget(self.azlcd1,row,col,Qt.AlignRight)
  
        row+=2
        self.azlcd2 = MyLCDNumber(self.tab,ndigits,ndec,True,True,wheelCB=self.setRotorAz)
        #self.azlcd2.setFixedSize(xs,ys)
        self.azlcd2.adjustSize()
        self.grid.addWidget(self.azlcd2,row,col,2,4)
        #self.grid.addWidget(self.azlcd2,row,col,Qt.AlignRight)

        # Add El controls - top is desired, bottom is actual
        row=0
        col=5
        lb=QLabel("Elevation:")
        self.grid.addWidget(lb,row,col)
        self.direction2 = QLineEdit()
        self.direction2.setAlignment(Qt.AlignCenter)
        self.grid.addWidget(self.direction2,row,col+1,1,3)

        row+=1
        self.ellcd1 = MyLCDNumber(self.tab,ndigits,ndec,True,True,wheelCB=None)
        #self.ellcd1.setFixedSize(xs,ys)
        self.ellcd1.adjustSize()
        self.grid.addWidget(self.ellcd1,row,col,2,4)
        #self.grid.addWidget(self.ellcd1,row,col,Qt.AlignRight)

        #lb = QLineEdit()
        #lb=QLabel(":Measured")
        #self.grid.addWidget(lb,row,col+1)

        row+=2
        self.ellcd2 = MyLCDNumber(self.tab,ndigits,ndec,True,True,wheelCB=self.setRotorEl)
        #self.ellcd2.setFixedSize(xs,ys)
        self.ellcd2.adjustSize()
        self.grid.addWidget(self.ellcd2,row,col,2,4)
        #self.grid.addWidget(self.ellcd2,row,col,Qt.AlignRight)
        
        # Initial positions
        pos=self.sock.get_position()
        if pos[0]>180:
            pos[0]-=360
        if pos[0]<-180:
            pos[0]+=360
        self.azlcd1.set(pos[0])
        self.ellcd1.set(pos[1])
        self.azlcd2.set(pos[0])
        self.ellcd2.set(pos[1])

        # Add entry box for input of a grid square
        row+=2
        col=0
        lb=QLabel("Grid:")
        self.grid.addWidget(lb,row,col)
        self.grid_sq = QLineEdit()
        self.grid_sq.setToolTip('Point to a Grid')
        self.grid.addWidget(self.grid_sq,row,col+1,1,3)
        self.grid_sq.returnPressed.connect(self.newGridSquare)
        
        # Add button to zero the rotor
        col=5
        self.btn = QPushButton('Rotor Home') 
        self.btn.setToolTip('Rotor to 0 az/el')
        self.btn.clicked.connect(self.rotorHome)
        self.grid.addWidget(self.btn,row,col,1,4)
        
        
    # Function to update rotor az
    def setRotorAz(self,az):
        print('setRotorAz:',az)
        if False:
            if az>179.9:
                az=179.9
                self.azlcd2.set(az)
            elif az<-179.9:
                az=-179.9
                self.azlcd2.set(az)
        else:
            if az>180:
                az-=360
            elif az<-179.9:
                az+=360
            self.azlcd2.set(az)
            
        pos=self.sock.get_position()
        pos[0]=az
        self.sock.set_position(pos)

    # Function to update rotor el
    def setRotorEl(self,el):
        print('setRotorEl:',el)
        if el>179.9:
            el=179.9
            self.ellcd2.set(el)
        elif el<0:
            el=0
            self.ellcd2.set(el)
        pos=self.sock.get_position()
        pos[1]=el
        self.sock.set_position(pos)

    # Function to send rotor to 0 az and 0 el
    def rotorHome(self):
        pos=[0,0]
        self.sock.set_position(pos)
        self.azlcd2.set(pos[0])
        self.ellcd2.set(pos[1])

    # Function to point rotor toward a user specified grid square
    def newGridSquare(self):
        txt=self.grid_sq.text().upper()
        print('newGridSquare:',txt)
        if bearing_ok:
            try:
                bearing = calculate_heading(MY_GRID,txt)
                print('bearing=',bearing)
                self.azlcd2.set(bearing)
                self.setRotorAz(bearing)
            except:
                print('Problem computing bearing for',MY_GRID,txt)

    # Function to give nominal direction info
    def nominalBearing(self):
        az=self.azlcd1.val
        if az<0:
            az+=360
        if az<15 or az>=345:
            txt='North - Idaho'
        elif az>=15 and az<30:
            txt='N-NE - Chicago'
        elif az>=30 and az<60:
            txt='NE - Minnesota'
        elif az>=60 and az<75:
            txt='E-NE - New York'
        elif az>=75 and az<105:
            txt='E - Georgia/Carribean'
        elif az>=105 and az<120:
            txt='E-SE - Central/South America'
        elif az>=120 and az<150:
            txt='SE - Central/South America'
        elif az>=150 and az<165:
            txt='S-SE - South America'
        elif az>=165 and az<195:
            txt='South - Antartica'
        elif az>=195 and az<210:
            txt='South - SouthWest'
        elif az>=210 and az<240:
            txt='SW - New Zealand'
        elif az>=240 and az<255:
            txt='W-SW - Australia'
        elif az>=255 and az<285:
            txt='West - Hawaii'
        elif az>=285 and az<300:
            txt='West - NorthWest'
        elif az>=300 and az<330:
            txt='NW - San Fransisco/Japan'
        elif az>=330 and az<345:
            txt='N-NW - Alaska/Washington'
        else:
            txt='???????????????????'
            
        #print(az)
        self.direction.setText(txt)
        
        el=self.ellcd1.val
        if el<30 or el>150:
            txt='Horizon'
        elif (el>=30 and el<60) or (el>=120 and el<150):
            txt='Well Above'
        elif el>=60 and el<120:
            txt='Up'

        self.direction2.setText(txt)
            
