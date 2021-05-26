############################################################################

# keypad.py - J.B.Attili - 2020

# Gui for controlling Yaesu key pad

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
from rig_io.ft_tables import *
import functools

################################################################################

class KEY_PAD():
    def __init__(self,parent,P):
        self.P=P

        self.tab = QWidget()
        parent.addTab(self.tab,"Key Pad")
        
        self.grid = QGridLayout()
        self.tab.setLayout(self.grid)
        
        print("\nProgramming keypad ...")

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
        for b in KEYER_MSGS.keys():
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
        #print('Keyer Msgs:',KEYER_MSGS)
        #print(KEYER_MSGS[arg])
        self.Keyer = KEYER_MSGS[arg]

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
                    cmd='w BY;KM'+str(i+1)+self.Keyer[i]+'}\n'
                else:
                    cmd='KM'+str(i+1)+self.Keyer[i]+'};'
            else:
                if s.connection=='HAMLIB':
                    cmd='w BY;EX025'+self.Keyer[i]+'\n'
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


