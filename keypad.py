############################################################################
#
# keypad.py - Rev 1.0
# Copyright (C) 2021-5 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Portion of Gui for programming Yaesu key pad.
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

if True:
    # Dynamic importing - this works!
    from widgets_qt import QTLIB
    #exec('from '+QTLIB+'.QtWidgets import *')
    #exec('from '+QTLIB+'.QtCore import Qt')
elif False:
    from PyQt6.QtWidgets import *
elif False:
    from PySide6.QtWidgets import *
else:
    #from PyQt5.QtCore import * 
    from PyQt5.QtWidgets import *
from rig_io.socket_io import *
#from widgets_qt import *
from rig_io.ft_tables import *
import functools

################################################################################

class KEY_PAD():
    def __init__(self,parent,P):
        self.P=P

        print('Creating key pad ...')
        self.tab = QWidget()
        print('hhhheeey')
        parent.addTab(self.tab,"Key Pad")
        
        self.grid = QGridLayout()
        self.tab.setLayout(self.grid)
        
        print("\nProgramming keypad ...")

        # CW keyer messages for various contests
        MY_CALL     = self.P.SETTINGS['MY_CALL']
        MY_NAME     = self.P.SETTINGS['MY_NAME']
        MY_STATE    = self.P.SETTINGS['MY_STATE']
        MY_SEC      = self.P.SETTINGS['MY_SEC']
        MY_CAT      = self.P.SETTINGS['MY_CAT']
        MY_CQ_ZONE  = self.P.SETTINGS['MY_CQ_ZONE']
        MY_ITU_ZONE = self.P.SETTINGS['MY_ITU_ZONE']
        MY_GRID     = self.P.SETTINGS['MY_GRID']
        
        self.KEYER_MSGS = OrderedDict()
        self.KEYER_MSGS["Defaults"]  = [MY_CALL,'TU 5NN '+MY_STATE,'OP '+MY_NAME,'73','BK','0001']
        self.KEYER_MSGS["ARRL DX"]   = [MY_CALL,'TU 5NN '+MY_STATE,MY_STATE+' '+MY_STATE,'73','AGN?','0001']
        self.KEYER_MSGS["NAQP"]      = [MY_CALL,'TU '+MY_NAME+' '+MY_STATE,MY_NAME+' '+MY_NAME,MY_STATE+' '+MY_STATE,'AGN?','0001']
        self.KEYER_MSGS["IARU"]      = [MY_CALL,'TU 5NN '+MY_ITU_ZONE,'T6 T6','73','AGN?','0001']
        self.KEYER_MSGS["CQ WW"]     = [MY_CALL,'TU 5NN '+MY_CQ_ZONE,'T3 T3','73','AGN?','GL']
        self.KEYER_MSGS["CQ WPX"]    = [MY_CALL,'TU 5NN 1','001 001','73','AGN?','0001']
        self.KEYER_MSGS["ARRL VHF"]  = [MY_CALL,'TU '+MY_GRID,MY_GRID+' '+MY_GRID,'73','AGN?','0001']
        self.KEYER_MSGS["ARRL 160m"] = [MY_CALL,'TU 5NN '+MY_SEC,MY_SEC+' '+MY_SEC,'73','AGN?','0001']
        self.KEYER_MSGS["Field Day"] = [MY_CALL,'TU '+MY_CAT+' '+MY_SEC,MY_CAT+' '+MY_CAT,MY_SEC+' '+MY_SEC,'AGN?','0001']
        #self.KEYER_MSGS["Test"]      = ['TEST1','2','3','4','5','0001']

        # Let's see what's in the keypad
        self.Keyer = self.GetKeyerMemory()
        print( self.Keyer )

        # Put up entry boxes
        self.entry=[];
        for i in range(6):
            if i<5:
                txt=str(i+1)+":"
            else:
                txt="#:"

            lab = QLabel(txt)
            self.grid.addWidget(lab,i,0)
            entry=QLineEdit()
            self.grid.addWidget(entry,i,1)
            entry.setText(self.Keyer[i])
            self.entry.append(entry)

        row=6
        col=0
        self.btns=[]
        for b in self.KEYER_MSGS.keys():
            print(b)
            btn = QPushButton(b)
            #btn.clicked.connect(lambda: self.KeyerMemoryDefaults(b) )
            btn.clicked.connect( functools.partial( self.KeyerMemoryDefaults,b ))
            self.grid.addWidget(btn,row,col)
            self.btns.append(btn)
            col+=1
            if col>=5:
                row+=1
                col =0

        self.btn1 = QPushButton('Update')
        self.btn1.setToolTip('Update Keyer Memory')
        self.btn1.clicked.connect(self.UpdateKeyerMemory)
        self.grid.addWidget(self.btn1,row,col)
        return

    def KeyerMemoryDefaults(self,arg):
        print("\nSetting Keypad Defaults ",arg)
        #print('Keyer Msgs:',self.KEYER_MSGS)
        #print(self.KEYER_MSGS[arg])
        self.Keyer = self.KEYER_MSGS[arg]

        for i in range(6):
            self.entry[i].setText(self.Keyer[i])
        print("Done.")
        
        
    def UpdateKeyerMemory(self):
        s=self.P.sock;

        print("\nUpdating keypad ...")
        for i in range(6):
            self.Keyer[i] = self.entry[i].text()
            if i<5:
                if s.connection=='HAMLIB':
                    #cmd='w BY;KM'+str(i+1)+self.Keyer[i]+'}\n'          # Old style b4 4.6.2
                    cmd='W KM'+str(i+1)+self.Keyer[i]+'}; 0'               
                else:
                    cmd='KM'+str(i+1)+self.Keyer[i]+'};'
            else:
                if s.connection=='HAMLIB':
                    #cmd='w BY;EX025'+self.Keyer[i]+'\n'          # Old style b4 4.6.2
                    cmd='W EX025'+self.Keyer[i]+'; 0' 
                else:
                    cmd='EX025'+self.Keyer[i]+';'
            print("cmd=",cmd)
            buf=s.get_response(cmd)

        print("Done.")
        

    def GetKeyerMemory(self):
        s=self.P.sock
        Keyer = []

        print("\nReading Keyer Memory ...")
        for i in range(6):
            print("GetKeyerMemory: i=",i)
            if i<5:
                if s.connection=='HAMLIB' and False:
                    cmd='w KM'+str(i+1)+'\n'
                else:
                    cmd='KM'+str(i+1)+';'
            else:
                if s.connection=='HAMLIB' and False:
                    cmd='w EX025\n'
                else:
                    cmd='EX025;'

            ntries=0
            while ntries<5:
                ntries+=1
                buf=s.get_response(cmd)
                if len(buf)>0:
                    break
            
            print("GetKeyerMemory: buf=",buf)
            if i<5:
                j=buf.index('}')
                Keyer.append(buf[3:j])
            else:
                j=buf.index(';')
                Keyer.append(buf[5:j])

        return Keyer


