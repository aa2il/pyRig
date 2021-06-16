############################################################################
#
# Watch Dog - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Watch dog timer for pyRig
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
if False:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import QTimer
else:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import QTimer

import rig_io.socket_io as socket_io
    
################################################################################

# Watch Dog Timer - Called every msec milliseconds to monitor health of app
class WatchDog:
    def __init__(self,P,msec):

        self.timer = QTimer()
        self.timer.timeout.connect(self.Monitor)
        self.timer.start(msec)
        self.count=0
        self.P = P
        self.VERBOSITY=1

        self.Monitor()

    # Check health of app in here
    def Monitor(self):
        P=self.P
        sock=P.sock
        sock2=P.sock2
        if self.VERBOSITY>0:
            print('Watch Dog ...',end=' ')

        # Read radio status
        #if P.sock.connection!='NONE':
        socket_io.read_radio_status(sock)
        if self.VERBOSITY>0:
            print(sock.freq, sock.band, sock.mode, sock.wpm,sock.filt)

        # First time in, the gui won't be up yet so trap the error
        try:
            # Check freq
            gui=P.gui.rig_common
            f=.001*sock.freq
            if f!=gui.lcd.get():
                gui.lcd.set(f)
        except:
            return

        # Check band
        if False:
            b=gui.band.currentText()
            if self.VERBOSITY>=2:
                print('b=',b)
            if sock.band!=b:
                gui.setRigBand(-1) 

        # Check mode
        m=gui.mode.currentText()
        if self.VERBOSITY>=2:
            print('m=',m)
        if sock.mode!=m:
            gui.setRigMode(-1)

        # Check filters - This was False/True
        if self.P.sock.rig_type2=='FT991a' and True:
            filt1=gui.filt1.currentText()
            if self.VERBOSITY>=2:
                print('Filts:',filt1,sock.filt)
            if [filt1]!=sock.filt:
                try:
                    gui.setRigFilter(-1)
                except:
                    pass
        if sock.rig_type=='Kenwood' or False:
            filt1=gui.filt1.currentText()
            filt2=gui.filt2.currentText()
            #print('Filts:',[filt1,filt2],self.sock.filt)
            if [filt1,filt2]!=sock.filt:
                try:
                    gui.setRigFilter(-1)
                except:
                    pass
                
        # Read S-meter - From newcat.c in hamlib4 for the ft991:
        # value of 0.448 determined by data from W6HN - seems to be pretty linear
        # SMeter, rig answer, fullscale, Rel. Intensity
        # S0       SM0000 0                -54 dB
        # S2       SM0026 10
        # S4       SM0051 20
        # S6       SM0081 30
        # S7.5     SM0105 40
        # S9       SM0130 50                 0 dB
        # +12db    SM0157 60
        # +25db    SM0186 70
        # +35db    SM0203 80
        # +50db    SM0237 90
        # +60db    SM0255 100               60 dB
        # 114dB range over 0-255 referenced to S0 of -54dB
        # val->i = atoi(retlvl) * (114.0 / 255.0) - 54;

        # This is consistent with the accepted definition of S-units but 
        # seems to read a little low on the ft991a - go with it for now
        s=sock.read_meter('S')
        print('s=',s)
        db=s*114./255.-54.
        if self.VERBOSITY>=2:
            print('S=',s,db)
        if db<=0:
            txt="S{:.1f}".format((db+54)/9.)
        else:
            txt="S9+"+"{:.1f}".format(db)
        gui.smeter.setValue(s)
        gui.smeter_txt.setText( txt )

        # Read power
        # Scale on rig runs from 0-150W but isn't linear - appears to be logarithmic below 50W
        # Measurements on ft991a:
        # 5W   =  7 dBW -->  38
        # 10W  = 10 dBW -->  59
        # 20W  = 13 dBW -->  86
        # 50W  = 17 dBW --> 149
        # 100W = 20 dBW --> 207
        # 150W = 21.76 dBW

        # Still needs some refinement
        if self.P.sock.rig_type2=='FTdx3000' or self.P.sock.rig_type2=='FT991a':
            s=sock.read_meter('Power')
            if s>150:
                #watts = s*150./255.
                watts = s*100./208.
                dbw   = -1
            else:
                dbw = s*17./150.
                watts = pow(10.,0.1*dbw)
                #if watts<2:
                #    watts=0
            if self.VERBOSITY>=2 or True:
                print('power=',s,watts,dbw)
            gui.pwr.setValue(s)
            txt="{:.1f}W".format(watts)
            gui.pwr_txt.setText( txt )
            
        # Read SWR - This causes a BEEP on the ts850 - bx RM1 command
        # Measuremets:
        # 1.1 --> 13
        # 3   --> 128
        s=sock.read_meter('SWR')
        print('swr=',s)
        swr=s*2./128. + 1
        if self.VERBOSITY>=2:
            print('swr=',s,swr)
        gui.swr.setValue(s)
        txt="{:.1f}".format(swr)
        gui.swr_txt.setText( txt )
        if swr>3:
            gui.swr_txt.setStyleSheet("color: rgb(255, 0, 0);")
        elif swr<2:
            gui.swr_txt.setStyleSheet("color: rgb(0,255, 0);")
        else:
            gui.swr_txt.setStyleSheet("color: rgb(200,200, 0);")
            
        if sock.rig_type=='Kenwood':
            return
        
        # Read COMP
        s=sock.read_meter('Comp')
        print('comp=',s)
        gui.comp.setValue(s)
            
        # Read ALC - no markings so use S-meter markings.
        # We're worried about anything above S9 which is about 60 for alc
        s=sock.read_meter('ALC')
        print('alc=',s)
        alc=s/60.
        if self.VERBOSITY>=2 or True:
            print('alc=',s,alc)
        gui.alc.setValue(s)
        txt="{:.1f}".format(alc)
        gui.alc_txt.setText( txt )
        if alc>1:
            gui.alc_txt.setStyleSheet("color: rgb(255, 0, 0);")
        elif alc<.25:
            gui.alc_txt.setStyleSheet("color: rgb(0,255, 0);")
        else:
            gui.alc_txt.setStyleSheet("color: rgb(200,200, 0);")
            #QPalette p = gui.alc.palette();
            #p.setColor(QPalette::Highlight, Qt::red);
            #gui.alc.setPalette(p);

        # Read rotor position
        if sock2.connection!='NONE':
            gui2=P.gui.rotor_ctrl
            pos=sock2.get_position()
            if self.VERBOSITY>=2:
                print('pos:',pos)
            if pos[0]!=None:
                if pos[0]>180:
                    pos[0]-=360
                if pos[0]<-180:
                    pos[0]+=360
                gui2.azlcd1.set(pos[0])
                gui2.ellcd1.set(pos[1])
                gui2.nominalBearing()
