############################################################################
#
# rig_common.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Gui for controlling the most common rig functions
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
import functools

################################################################################

class RIG_COMMON():
    def __init__(self,parent,P):
        self.P=P

        if True:
            print('RIG_COMMN INIT:',P.sock.rig_type,P.sock.rig_type1,P.sock.rig_type2)

        self.tab1 = QWidget()
        parent.addTab(self.tab1,"Common")
        
        self.grid = QGridLayout()
        self.tab1.setLayout(self.grid)

        # Add VFO A control
        row=0
        col=0
        self.lcd = MyLCDNumber(self.tab1,7,1,ival=.001*P.sock.freq,wheelCB=self.setRigFreq)
        self.lcd.setFixedSize(400, 80)
        self.grid.addWidget(self.lcd,row,col,2,4)
        row+=2

        # Add band selector
        if self.P.sock.rig_type2=='FTdx3000' or self.P.sock.rig_type2=='FT991a':
            #row+=1
            self.bands = []
            for b in bands.keys():
                if bands[b]['Code']>=0:
                    self.bands.append(b)
            #print('bands=',self.bands)
            lb=QLabel("Band:")
            self.grid.addWidget(lb,row,col)
            self.band = QComboBox()
            self.band.addItems(self.bands)
            self.band.currentIndexChanged.connect(self.setRigBand)
            self.grid.addWidget(self.band,row,col+1)
            self.setRigBand(-1)

        # Add memory channel selector
        if self.P.sock.rig_type2=='FTdx3000' or self.P.sock.rig_type2=='FT991a':
            col+=2
            self.memchans = [str(x) for x in range(117)]
            #print('chans=',self.memchans)
            lb=QLabel("Mem Chan:")
            self.grid.addWidget(lb,row,col)
            self.memchan = QComboBox()
            self.memchan.addItems(self.memchans)
            self.memchan.currentIndexChanged.connect(self.setMemChan)
            self.grid.addWidget(self.memchan,row,col+1)

        # Add split on/off selector
        if self.P.sock.rig_type2=='FTdx3000' or self.P.sock.rig_type2=='FT991a':
            col+=2
            self.split = QPushButton('Split') 
            self.split.setToolTip('Split On/Off')
            self.split.clicked.connect(self.toggle_split)
            self.grid.addWidget(self.split,row,col)
            self.split.setCheckable( True )

            split = self.P.sock.split_mode(-1)
            self.split.setChecked( split )
            print('Split is ',split,self.P.sock.rig_type)
            if split and self.P.sock.rig_type=='Hamlib':
                # For some reason, Hamlib needs this for things to work properly
                split = self.P.sock.split_mode(1)
            
        
        # Add Mode selector
        row+=1
        col=0
        self.modes = ['LSB','USB','CW','FM','AM','RTTY','PKTUSB']
        lb=QLabel("Mode:")
        self.grid.addWidget(lb,row,col)
        self.mode = QComboBox()
        self.mode.addItems(self.modes)
        self.mode.currentIndexChanged.connect(self.setRigMode)
        self.grid.addWidget(self.mode,row,col+1)
        self.setRigMode(-1)

        # Ant Tuner buttons
        col+=2
        self.tuner_btn1 = QPushButton('Tuner') 
        self.tuner_btn1.setToolTip('Tuner On/Off')
        self.tuner_btn1.clicked.connect(self.toggle_tuner)
        self.grid.addWidget(self.tuner_btn1,row,col)
        self.tuner_btn1.setCheckable( True )
        print( self.P.sock.tuner(-1) )
        if self.P.sock.tuner(-1):
            print('Tuner is on')
            self.tuner_btn1.setChecked( True )
        else:
            print('Tuner is off')
            self.tuner_btn1.setChecked( False )

        col+=1
        self.tuner_btn2 = QPushButton('Tune') 
        self.tuner_btn2.setToolTip('Run Tuner')
        self.tuner_btn2.clicked.connect(self.tune)
        self.grid.addWidget(self.tuner_btn2,row,col)
            
        # Add filter selectors
        col=0
        row+=1
        lb=QLabel("Filters:")
        self.grid.addWidget(lb,row,col)
            
        self.filt1 = QComboBox()
        self.filt2 = QComboBox()
        self.grid.addWidget(self.filt1,row,col+1)
        self.grid.addWidget(self.filt2,row,col+2)
        
        self.change_filters()
        self.filt1.currentIndexChanged.connect( functools.partial( self.setRigFilter,1 ) )
        self.filt2.currentIndexChanged.connect( functools.partial( self.setRigFilter,2 ) )
        self.setRigFilter(-1)
        
        # Add S-meter
        if self.P.sock.rig_type=='Kenwood':
            MAX_METER=30
        else:
            MAX_METER=255
        row+=1
        lb=QLabel("S-meter:")
        self.grid.addWidget(lb,row,col)
        self.smeter = QProgressBar()
        self.smeter.setMaximum(MAX_METER)
        self.grid.addWidget(self.smeter,row,col+1,1,3)
        self.smeter.setTextVisible(False)
        self.smeter_txt = QLineEdit()
        self.grid.addWidget(self.smeter_txt,row,col+4)

        # Add Power meter
        if self.P.sock.rig_type2=='FTdx3000' or self.P.sock.rig_type2=='FT991a':
            row+=1
            lb=QLabel("Power:")
            self.grid.addWidget(lb,row,col)
            self.pwr = QProgressBar()
            self.pwr.setMaximum(MAX_METER)
            self.grid.addWidget(self.pwr,row,col+1,1,3)
            self.pwr.setTextVisible(False)
            self.pwr_txt = QLineEdit()
            self.grid.addWidget(self.pwr_txt,row,col+4)

            # Slider to adjust output power
            if False:
                col += 2
                ncol  =3
                lab = QLabel("TX Power:")
                self.grid.addWidget(lab,row,col)
                self.pwr_slider = QSlider(Qt.Horizontal)
                self.pwr_slider.setMinimum(0)
                self.pwr_slider.setMaximum(100)
                self.pwr_slider.setTickPosition(QSlider.TicksBelow)
                self.pwr_slider.setTickInterval(25)
                self.pwr_slider.valueChanged.connect(self.setRigPower)
                self.grid.addWidget(self.pwr_slider,row,col+1,1,ncol-1)
                self.setRigPower()
            
        # Add SWR meter
        row+=1
        col =0
        lb=QLabel("SWR:")
        self.grid.addWidget(lb,row,col)
        self.swr = QProgressBar()
        self.swr.setMaximum(MAX_METER)
        self.grid.addWidget(self.swr,row,col+1,1,3)
        self.swr.setTextVisible(False)
        self.swr_txt = QLineEdit()
        self.grid.addWidget(self.swr_txt,row,col+4)

        # Add COMP meter
        row+=1
        lb=QLabel("COMP:")
        self.grid.addWidget(lb,row,col)
        self.comp = QProgressBar()
        self.comp.setMaximum(MAX_METER)
        self.grid.addWidget(self.comp,row,col+1,1,3)
        self.comp.setTextVisible(False)
        
        # Add ALC meter
        row+=1
        lb=QLabel("ALC:")
        self.grid.addWidget(lb,row,col)
        self.alc = QProgressBar()
        self.alc.setMaximum(MAX_METER)
        self.grid.addWidget(self.alc,row,col+1,1,3)
        self.alc.setTextVisible(False)
        self.alc_txt = QLineEdit()
        self.grid.addWidget(self.alc_txt,row,col+4)
        
        # Buttons to select audio port
        row+=1
        col=0
        if self.P.sock.rig_type2=='FTdx3000' or self.P.sock.rig_type2=='FT991a':
            self.btn_group=QButtonGroup() 
            self.btns={}
            for src in ['Front','Rear']:
                self.btns[src] = QRadioButton(src)
                self.btns[src].toggled.connect(self.front_rear)
                self.btn_group.addButton(self.btns[src])
                self.grid.addWidget(self.btns[src] ,row,col)
                col += 1

            # Make sure source is from front 
            self.btns['Front'].setChecked(True)
            
        # PTT button
        self.ptt_btn = QPushButton('PTT') 
        self.ptt_btn.setToolTip('Push-to-Talk')
        self.ptt_btn.setCheckable(True)
        self.ptt_btn.clicked.connect(self.ptt)
        self.ptt_btn.resize(self.ptt_btn.sizeHint())
        self.grid.addWidget(self.ptt_btn,row,col)

        # Key-down button - asserts DTR
        col+=1
        self.dtr_btn = QPushButton('Key-Down') 
        self.dtr_btn.setToolTip('Assert DTR')
        self.dtr_btn.setCheckable(True)
        self.dtr_btn.clicked.connect(self.dtr)
        self.dtr_btn.resize(self.dtr_btn.sizeHint())
        self.grid.addWidget(self.dtr_btn,row,col)


    # Routine to change list of filters
    def change_filters(self):

        if self.P.sock.rig_type=='Kenwood':
            self.filters1 = TS850_FILTERS
            self.filters2 = TS850_FILTERS
        else:
            self.filters1 = ['Wide','Narrow']
            
            m=self.P.sock.mode
            wide=self.P.sock.filt[0]
            if m=='RTTY' or m=='PKTUSB' or m=='DATA-U':
                if wide=='Wide':
                    filts=FT991A_DATA_FILTERS2
                else:
                    filts=FT991A_DATA_FILTERS1
            elif m=='USB' or m=='LSB':
                if wide=='Wide':
                    filts=FT991A_SSB_FILTERS2
                else:
                    filts=FT991A_SSB_FILTERS1
            elif m=='CW':
                if wide=='Wide':
                    filts=FT991A_CW_FILTERS2
                else:
                    filts=FT991A_CW_FILTERS1
            elif m=='AM':
                # idx=0
                if wide=='Wide':
                    filts=FT991A_AM_FILTERS2
                else:
                    filts=FT991A_AM_FILTERS1
            elif m=='FM':
                # idx=0
                if wide=='Wide':
                    filts=FT991A_AM_FILTERS2
                else:
                    filts=FT991A_AM_FILTERS1
            else:
                print('CHANGE_FILTS - Unknown mode',m)
                sys,exit(0)

            self.filters2=[]
            self.filts=filts
            for f in filts:
                if f>0:
                    self.filters2.append(str(f)+' Hz')

        # Before we can update the list in the combo box,
        # we need to disable any signals, otherwise, we get
        # stuck in an infinite loop
        #self.filt1.setEnabled(False)
        #self.filt2.setEnabled(False)
        self.filt1.blockSignals(True)
        self.filt2.blockSignals(True)

        self.filt1.clear()
        self.filt1.addItems(self.filters1)
        self.filt2.clear()
        self.filt2.addItems(self.filters2)

        self.filt1.blockSignals(False)
        self.filt2.blockSignals(False)
        #self.filt1.setEnabled(True)
        #self.filt2.setEnabled(True)
            
    # Callback to toggle split mode
    def toggle_split(self):
        splt = self.P.sock.split_mode(-1)
        print('Toggle split',splt)
        if splt:
            print('Split is on - turning off')
            self.P.sock.split_mode(0)
            self.split.setChecked( False )
        else:
            print('Split is off - turning on')
            self.P.sock.split_mode(1)
            self.split.setChecked( True )

    # Callback to toggle antenna tuner
    def toggle_tuner(self):
        print('Toggle tuner')
        if self.tuner_btn1.isChecked():
            self.P.sock.tuner(1)
        else:
            self.P.sock.tuner(0)

    # Callback to run antenna tuner
    def tune(self):
        print('Tune')
        self.P.sock.tuner(2)
        self.tuner_btn1.setChecked( True )

    # Callback for front/rear source buttons
    def front_rear(self):
        #b = self.clicked(self.btns)
        b = self.btn_group.sender()
        print('btn=',b.text())
        if b.isChecked():
            print( b.text()+" is checked" )
            m=self.P.sock.mode
            if b.text()=='Front':
                src=0
                prt=0
            else:
                src=1
                prt=1
            self.P.sock.mic_setting(m,1,src=src,prt=prt)

    # Function to update rig freq
    def setRigFreq(self,f):
        print('setRigFreq:',f)
        self.P.sock.set_freq(f)

    # Function to set memory channel
    def setMemChan(self,ch):
        print('setMemChan:',ch)
        self.P.sock.set_mem_chan(ch)

    # Function to update rig band
    def setRigBand(self,idx):
        print('setRigBand: %d %s' % (idx,self.bands[idx]))
        if idx==-1:
            # Set combo box from rig mode
            print('band=',self.P.sock.band)
            idx=self.bands.index(self.P.sock.band)
            self.band.setCurrentIndex(idx)
        else:
            # Set rig from combo box selection
            if self.P.sock.band!=self.bands[idx]:
                self.P.sock.set_band(self.bands[idx])

    # Function to update rig mode
    def setRigMode(self,idx):
        print('\n--------- setRigMode: %d %s' % (idx,self.modes[idx]))
        if idx==-1:
            # Set combo box from rig mode
            mode=self.P.sock.mode
            if mode=='CW-U' or mode=='CW-L' or mode=='CW-R':
                mode='CW'
            elif mode=='DATA-U':
                mode='PKTUSB'
            idx=self.modes.index(mode)
            self.mode.setCurrentIndex(idx)
        else:
            # Set rig from combo box selection
            if self.P.sock.mode!=self.modes[idx]:
                mode1=self.modes[idx]
                self.P.sock.set_mode(mode1)

                # Check Split & set VFO B if necessary
                # Assume inverting transponder for now, fix this later
                splt = self.P.sock.split_mode(-1)
                if splt:
                    if mode1=='CW':
                        mode2='CW-LSB'
                    elif mode1=='USB':
                        mode2='LSB'
                    elif mode1=='LSB':
                        mode2='USB'
                    else:
                        mode2=mode1
                    print('setRigMode: Split is on',mode1,mode2,'\n')
                    self.P.sock.set_mode(mode2,VFO='B')
                    
                

    # Function to update rig filters
    def setRigFilter(self,ifilt,idx=0):
        print('\nsetRigFilter: %d %d' % (ifilt,idx))
        if ifilt==-1:

            self.change_filters()

            # Set combo boxes from rig filters
            print('Current filter:',self.P.sock.filt)
            if self.P.sock.filt[0]!=None:
                idx1=self.filters1.index(self.P.sock.filt[0])
                print('idx1=',idx1)
                self.filt1.setCurrentIndex(idx1)
            
            if self.P.sock.filt[1]!=None:
                try:
                    idx2=self.filters2.index(self.P.sock.filt[1])
                    print('idx2=',idx2)
                    self.filt2.setCurrentIndex(idx2)
                except:
                    print('RIG_COMMON: setRigFilter - failure')
                    
        else:
            # Set rig from combo box selection
            if ifilt==1:
                filt=self.filters1[idx]
            else:
                filt=self.filters2[idx]
            if filt != self.P.sock.filt[ifilt-1]:
                new_filts = self.P.sock.filt.copy()
                new_filts[ifilt-1] = filt
                try:
                    if not self.P.sock.set_filter(new_filts):
                        self.setRigFilter(-1)
                except:
                    pass
        print('setRigFilter: Done\n')

                    
    # Function to handle PTT
    def ptt(self):
        print('PTT:')
        self.P.sock.ptt(self.ptt_btn.isChecked())

    # Function to handle DTR
    def dtr(self):
        print('DTR:')
        self.P.sock.s.setDTR( self.dtr_btn.isChecked() )

    # Callback for tx power slider
    def setRigPower(self):
        p = self.pwr_slider.value()
        if p==0:
            p=self.P.sock.get_power()
        self.P.sock.set_power(p)
        self.pwr_txt.setText( "{0:,d} W".format(p) )

################################################################################

class RIG_VFOS():
    def __init__(self,parent,P):
        self.P=P
        #self.sock=P.sock

        self.tab1 = QWidget()
        parent.addTab(self.tab1,"VFO Control")
        
        self.grid = QGridLayout()
        self.tab1.setLayout(self.grid)

        self.MODE_LIST = ['FM','USB','LSB','CW','CW-R','PKTUSB','PKTLSB','AM']
     
        # Add VFO A control
        row=0
        col=0
        lb=QLabel("VFO A:")
        self.grid.addWidget(lb,row,col)
        self.vfoA = QComboBox()
        self.vfoA.addItems(self.MODE_LIST)
        self.grid.addWidget(self.vfoA,row,col+1)
        self.vfoA.currentIndexChanged.connect( functools.partial(self.set_vfo_mode,'A',1) )
        self.set_vfo_mode('A',-1)

        # Add VFO B control
        row+=1
        lb=QLabel("VFO B:")
        self.grid.addWidget(lb,row,col)
        self.vfoB = QComboBox()
        self.vfoB.addItems(self.MODE_LIST)
        self.grid.addWidget(self.vfoB,row,col+1)
        self.vfoB.currentIndexChanged.connect( functools.partial(self.set_vfo_mode,'B',1) )
        self.set_vfo_mode('B',-1)

        # Satellites
        row+=2
        lb=QLabel('Satellites:')
        self.grid.addWidget(lb,row,col)
        for mode in ['FM','USB-INV','USB','LSB-INV','LSB','CW','CW-INV','CW/USB', \
                     'PKT-INV','PKT-USB','PKT-FM']:

            # Align buttons according to voice, CW and packet modes
            if mode=='FM' or mode=='CW' or mode=='PKT-INV':
                row+=1
                col=0
            else:
                col+=1
                
            btn = QPushButton(mode) 
            self.grid.addWidget(btn,row,col)
            btn.clicked.connect( functools.partial(self.SetSatMode,mode) )

            
    # Callback for VFO Mode list spinner
    def set_vfo_mode(self,vfo,iopt,mode=None):

        print('\nRIG_VFOS: SET_VFO_MODE Spinner callback:',vfo,iopt,mode)
        
        if iopt==-1 or mode==None:
            
            # Set spin box according to rig
            mode = self.P.sock.get_mode(VFO=vfo)
            if mode=='DATA-U':
                mode='PKTUSB'
            idx=self.MODE_LIST.index(mode)
            if vfo=='A':
                self.vfoA.setCurrentIndex(idx)
            else:
                self.vfoB.setCurrentIndex(idx)

        else:

            # Set radio according to specified mode
            split = self.P.sock.split_mode(-1)
            if isinstance(mode, int):
                mode=self.MODE_LIST[mode]
            print('SET_VFO_MODE: Setting radio vfo ...',vfo,iopt,mode,'\tsplit=',split)
            if vfo in 'AM' or split:
                self.P.sock.set_mode(mode,VFO=vfo)

             
    def SetSatMode(self,mode):

        # Init
        print("\nRIG_VFOS: Set Sat Mode ...",mode)

        # Split mode
        self.P.sock.split_mode(1)

        mode1=mode
        if mode=='FM':
            #cmd='rigctl -m 2 -r localhost:4532 M FM 0 X FM 0'
            mode2='FM'
        elif mode=='USB-INV':
            #cmd='rigctl -m 2 -r localhost:4532 M USB 0 X LSB 0'
            mode1='USB'
            mode2='LSB'
        elif mode=='USB':
            #cmd='rigctl -m 2 -r localhost:4532 M USB 0 X USB 0'
            mode2='USB'
        elif mode=='LSB':
            #cmd='rigctl -m 2 -r localhost:4532 M LSB 0 X LSB 0'
            mode2='LSB'
        elif mode=='LSB-INV':
            #cmd='rigctl -m 2 -r localhost:4532 M LSB 0 X USB 0'
            mode1='LSB'
            mode2='USB'
        elif mode=='CW':
            #cmd='rigctl -m 2 -r localhost:4532 M CW 0 X CW 0'
            mode2='CW'
        elif mode=='CW-INV':
            #cmd='rigctl -m 2 -r localhost:4532 M CW 0 X CW 0'
            mode1='CW'
            mode2='CW-R'
        elif mode=='CW/USB':
            # Not sure what this all about?
            #cmd='rigctl -m 2 -r localhost:4532 M USB 0 X CW 0'
            mode1='USB'
            mode2='CW'
        elif mode=='PKT-INV':
            #cmd='rigctl -m 2 -r localhost:4532 M PKTUSB 0 X PKTLSB 0'
            mode1='PKTUSB'
            mode2='PKTLSB'
        elif mode=='PKT-USB':
            #cmd='rigctl -m 2 -r localhost:4532 M PKTUSB 0 X PKTUSB 0'
            mode1='PKTUSB'
            mode2='PKTUSB'
        elif mode=='PKT-FM':
            cmd='rigctl -m 2 -r localhost:4532 M PKTFM 0 X PKTFM 0'
            mode1='PKTFM'
            mode2='PKTFM'
        else:
            print('SET SAT MODE: Unknwon mode',mode)
            return

        print('SET SAT MODE: ',mode1,mode2)
        self.set_vfo_mode('A',1,mode1)
        self.set_vfo_mode('B',1,mode2)
   
