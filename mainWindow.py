from PyQt5.QtWidgets import QMessageBox, QWidget, QApplication
from PyQt5 import QtCore, QtWidgets, QtGui, uic
from multimediav1 import VideoPlayer
import matplotlib.pyplot as plt
import serial.tools.list_ports
import numpy as np
import datetime
import serial 
import struct
import time
import sys 
import csv 

def serial_checker():
    port_name = ''
    ports = serial.tools.list_ports.comports()
    for port,desc,hwid in sorted(ports):
        port_name = port
        port_desc = desc
        port_hwid = hwid
    return port_name

def time_now():
    now = datetime.datetime.now().strftime("%H:%M:%S")
    return str(now)

def date_now():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    today = str(today)
    return today

class threading(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = uic.loadUi('/home/bimanjaya/learner/TA/relaxation-chair-GUI/sistem-kursi-relaksasi-v2.ui',self)

        self.thread = {}
        self.tutorialButton.clicked.connect(self.tutorial_worker)
        self.startButton.clicked.connect(self.start_worker)
        self.stopButton.clicked.connect(self.stop_worker)
        self.saveButton.clicked.connect(self.save_worker)
        self.tareButton.clicked.connect(self.tare_worker)
        self.pijatButton.clicked.connect(self.pijat_worker)
        self.vibrationButton.clicked.connect(self.vibration_worker)
        self.heatButton.clicked.connect(self.heat_worker)
        self.pumpButton.clicked.connect(self.pump_worker)
        self.pumpMode_Button.clicked.connect(self.pumpMode_worker)
        self.pumpUp_Button.clicked.connect(self.pumpUp_worker)
        self.pumpDown_Button.clicked.connect(self.pumpDown_worker)
        self.modeBox.activated.connect(self.choosing_mode)

        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.saveButton.setEnabled(False)
        self.tareButton.setEnabled(False)
        self.pijatButton.setEnabled(False)
        self.vibrationButton.setEnabled(False)
        self.heatButton.setEnabled(False)
        self.pumpButton.setEnabled(False)
        self.pumpMode_Button.setEnabled(False)
        self.pumpUp_Button.setEnabled(False)
        self.pumpDown_Button.setEnabled(False)

        self.thread1_state = 0 # tutorial
        self.thread2_state = 0 # video
        self.thread3_state = 0 # getLoadcell
        self.thread4_state = 0 # massage
        self.thread5_state = 0 # EEG
        self.thread6_state = 0 # pump
        self.thread7_state = 0 # timer
        self.thread8_state = 0 # tare
        self.thread9_state = 0 # pijat
        self.thread10_state = 0 # vibration
        self.thread11_state = 0 # heat
        self.thread12_state = 0 # pump
        self.thread13_state = 0 # pumpMode
        self.thread14_state = 0 # pumpUp
        self.thread15_state = 0 # pumpDown

        self.realtimeVol = 0
        self.csv_data = []
        self.csv_data_time = []
        self.csv_data_vol = []
        self.rec_rate = 1
        self.rec_oldtime = 0
        self.rec_newtime = 0
        self.rec_i = 0
        self.x = ''
        self.volumeTarget = 0
        
        self.choosing_mode()
    
### ------------------------- ###

    def show_vol_graph(self):
        self.MplWidget.canvas.axes.clear()
        self.MplWidget.canvas.axes.plot(self.csv_data_time, self.csv_data_vol)
        # self.MplWidget.canvas.axes.set_xticklabels([])
        # self.MplWidget.canvas.axes.pyplot.locator_params(axis='x', nbins=5)
        xmin, xmax = self.MplWidget.canvas.axes.get_xlim()
        self.MplWidget.canvas.axes.set_xticks(np.round(np.linspace(xmin, xmax, 5), 2))
        self.MplWidget.canvas.draw()

    def choosing_mode(self):
        self.x = str(self.modeBox.currentText())
        if self.x == 'Timer':
            self.timeSpinBox.setDisabled(False)
            self.volumeSpinBox.setDisabled(True)
        else:
            self.timeSpinBox.setDisabled(True)
            self.volumeSpinBox.setDisabled(False)    

    def volume_mode(self):
        if self.x == 'Volume':
            if self.realtimeVol >= self.volumeTarget:
                self.stop_worker()

### ------------------------- ###

    def tutorial_worker(self):
        self.thread[1] = tutorial_thread(parent=None)
        self.thread[1].start()
        self.thread1_state = 1
        self.thread[1].any_signal1.connect(self.tutorial_action)

    def start_worker(self):

        if self.x == 'Timer':

            if self.timeSpinBox.value() > 0:
                
                if ((self.thread2_state and self.thread3_state and self.thread4_state 
                and self.thread5_state and self.thread6_state and self.thread7_state) == 0):

                    if serial_checker() == '/dev/ttyUSB0':

                        self.startButton.setEnabled(False)
                        self.stopButton.setEnabled(True)
                        self.saveButton.setEnabled(False)
                        self.tareButton.setEnabled(True)
                        self.pijatButton.setEnabled(True)
                        self.vibrationButton.setEnabled(False)
                        self.heatButton.setEnabled(False)
                        self.pumpButton.setEnabled(True)
                        self.pumpMode_Button.setEnabled(False)
                        self.pumpUp_Button.setEnabled(False)
                        self.pumpDown_Button.setEnabled(False)
                        self.modeBox.setEnabled(False)
                        self.timeSpinBox.setDisabled(True)
                        self.volumeSpinBox.setDisabled(True)
                        self.MplWidget.canvas.axes.clear()
                        self.MplWidget.canvas.draw()

                        # START GET LOADCELL DATA
                        self.thread[3] = start_thread_getLoadcell(parent=None)
                        self.thread[3].start()
                        self.thread[3].any_signal3.connect(self.start_action_getLoadcell)
                        self.thread3_state = 1
                        time.sleep(0.2)

                        # START VIDEO
                        self.thread[2] = start_thread_video(parent=None)
                        self.thread[2].start()
                        self.thread[2].any_signal2.connect(self.start_action_video)
                        self.thread2_state = 1
                        time.sleep(0.2)
                            
                        # START MASSAGE COMMAND
                        self.thread[4] = start_thread_massage(parent=None)
                        self.thread[4].start()
                        self.thread[4].any_signal4.connect(self.start_action_massage)
                        self.thread4_state = 1
                        time.sleep(0.2)

                        # START GET EEG DATA
                        self.thread[5] = start_thread_EEG(parent=None)
                        self.thread[5].start()
                        self.thread[5].any_signal5.connect(self.start_action_EEG)
                        self.thread5_state = 1
                        time.sleep(0.2)

                        # START PUMP COMMAND
                        self.thread[6] = start_thread_pump(parent=None)
                        self.thread[6].start()
                        self.thread[6].any_signal6.connect(self.start_action_pump)
                        self.thread6_state = 1
                        time.sleep(0.2)

                        # if self.x == 'Timer':
                        #     if self.timeSpinBox.value() > 0:
                        
                        # START TIMER
                        self.thread[7] = start_thread_timer(self.timeSpinBox.value(),parent=None)
                        self.thread[7].start()
                        self.thread[7].any_signal7.connect(self.start_action_timer)
                        self.thread7_state = 1
                        time.sleep(0.2)
                        
                        # else:
                        #     self.volumeTarget = self.volumeSpinBox.value()

                        self.csv_data = []
                        self.csv_data_time = []
                        self.csv_data_vol = []
                        self.rec_oldtime = time.time()
                        self.rec_newtime = self.rec_oldtime
                        self.rec_i = 0
                        self.saveLabel.setText('Sistem sedang berjalan')
                        self.saveLabel.adjustSize()
                        self.thread9_state = 0

                    else:
                        msg = QMessageBox()
                        msg.setWindowTitle('PERINGATAN')
                        msg.setText('Mikrokontroller tidak terdeteksi')
                        msg.setIcon(QMessageBox.Warning) # WARNING SIGN ICON
                        x = msg.exec_()

            else:
                msg = QMessageBox()
                msg.setWindowTitle('PERINGATAN')
                msg.setText('Atur timer dengan rentang 1-30 (menit)')
                msg.setIcon(QMessageBox.Warning) # WARNING SIGN ICON
                x = msg.exec_()

        else:
            if self.volumeSpinBox.value() > 0:
                self.volumeTarget = self.volumeSpinBox.value()
                if ((self.thread2_state and self.thread3_state and self.thread4_state 
                    and self.thread5_state and self.thread6_state and self.thread7_state) == 0):

                        if serial_checker() == '/dev/ttyUSB0':

                            self.startButton.setEnabled(False)
                            self.stopButton.setEnabled(True)
                            self.saveButton.setEnabled(False)
                            self.tareButton.setEnabled(True)
                            self.pijatButton.setEnabled(True)
                            self.vibrationButton.setEnabled(False)
                            self.heatButton.setEnabled(False)
                            self.pumpButton.setEnabled(True)
                            self.pumpMode_Button.setEnabled(False)
                            self.pumpUp_Button.setEnabled(False)
                            self.pumpDown_Button.setEnabled(False)
                            self.modeBox.setEnabled(False)
                            self.timeSpinBox.setDisabled(True)
                            self.volumeSpinBox.setDisabled(True)
                            self.MplWidget.canvas.axes.clear()
                            self.MplWidget.canvas.draw()

                            # START GET LOADCELL DATA
                            self.thread[3] = start_thread_getLoadcell(parent=None)
                            self.thread[3].start()
                            self.thread[3].any_signal3.connect(self.start_action_getLoadcell)
                            self.thread3_state = 1
                            time.sleep(0.2)

                            # START VIDEO
                            self.thread[2] = start_thread_video(parent=None)
                            self.thread[2].start()
                            self.thread[2].any_signal2.connect(self.start_action_video)
                            self.thread2_state = 1
                            time.sleep(0.2)
                                
                            # START MASSAGE COMMAND
                            self.thread[4] = start_thread_massage(parent=None)
                            self.thread[4].start()
                            self.thread[4].any_signal4.connect(self.start_action_massage)
                            self.thread4_state = 1
                            time.sleep(0.2)

                            # START GET EEG DATA
                            self.thread[5] = start_thread_EEG(parent=None)
                            self.thread[5].start()
                            self.thread[5].any_signal5.connect(self.start_action_EEG)
                            self.thread5_state = 1
                            time.sleep(0.2)

                            # START PUMP COMMAND
                            self.thread[6] = start_thread_pump(parent=None)
                            self.thread[6].start()
                            self.thread[6].any_signal6.connect(self.start_action_pump)
                            self.thread6_state = 1
                            time.sleep(0.2)

                            # if self.x == 'Timer':
                            #     if self.timeSpinBox.value() > 0:
                            
                            # # START TIMER
                            # self.thread[7] = start_thread_timer(self.timeSpinBox.value(),parent=None)
                            # self.thread[7].start()
                            # self.thread[7].any_signal7.connect(self.start_action_timer)
                            # self.thread7_state = 1
                            # time.sleep(0.2)
                            
                            # else:
                            #     self.volumeTarget = self.volumeSpinBox.value()

                            self.csv_data = []
                            self.csv_data_time = []
                            self.csv_data_vol = []
                            self.rec_oldtime = time.time()
                            self.rec_newtime = self.rec_oldtime
                            self.rec_i = 0
                            self.saveLabel.setText('Sistem sedang berjalan')
                            self.saveLabel.adjustSize()
                            self.thread9_state = 0

                            self.pump_worker()
                            self.pumpButton.setEnabled(False)

                        else:
                            msg = QMessageBox()
                            msg.setWindowTitle('PERINGATAN')
                            msg.setText('Mikrokontroller tidak terdeteksi')
                            msg.setIcon(QMessageBox.Warning) # WARNING SIGN ICON
                            x = msg.exec_()
            else:
                msg = QMessageBox()
                msg.setWindowTitle('PERINGATAN')
                msg.setText('Atur volume dengan maksimal 150 (ml)')
                msg.setIcon(QMessageBox.Warning) # WARNING SIGN ICON
                x = msg.exec_()

    def tare_worker(self):
        if self.thread3_state == 1:
            self.thread[8] = tare_thread(parent=None)
            self.thread[8].start()
            self.thread[8].any_signal8.connect(self.tare_action)

    def stop_worker(self):

        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.tareButton.setEnabled(False)
        self.saveButton.setEnabled(True)
        self.pijatButton.setEnabled(False)
        self.vibrationButton.setEnabled(False)
        self.heatButton.setEnabled(False)
        self.pumpButton.setEnabled(False)
        self.pumpMode_Button.setEnabled(False)
        self.pumpUp_Button.setEnabled(False)
        self.pumpDown_Button.setEnabled(False)
        self.modeBox.setEnabled(True)
        self.choosing_mode()

        if self.thread9_state % 2 == 1:
            self.pijat_worker()
        if self.thread12_state % 2 == 1:
            self.pump_worker()

        if self.thread2_state == 1:
            self.thread[2].stop()
            self.thread2_state = 0
        if self.thread3_state == 1:
            self.thread[3].stop()
            self.thread3_state = 0
        if self.thread4_state == 1:
            self.thread[4].stop()
            self.thread4_state = 0
        if self.thread5_state == 1:
            self.thread[5].stop()
            self.thread5_state = 0
        if self.thread6_state == 1:
            self.thread[6].stop()
            self.thread6_state = 0
        if self.thread7_state == 1:
            self.thread[7].stop()
            self.thread7_state = 0

        self.saveLabel.setText('Ada data belum tersimpan')
        self.saveLabel.adjustSize()
        self.realtimeASI.setText('0')
        self.realtimeASI.adjustSize()
        self.show_vol_graph()

    def save_worker(self):
        for i in self.csv_data_time:
            self.csv_data.append([i])
        for j in self.csv_data_vol:
            self.csv_data[self.rec_i].append(j)
            self.rec_i += 1
        print(self.csv_data)
        file = open('/home/bimanjaya/learner/TA/relaxation-chair-GUI/data_logger/load_cell/'+date_now()+'_'+time_now()+'.csv', 'w', newline ='')
        with file:
            header = ['Waktu', 'Nilai']
            writer = csv.DictWriter(file, fieldnames = header)
            writer.writeheader()
        file.close()
        file = open('/home/bimanjaya/learner/TA/relaxation-chair-GUI/data_logger/load_cell/'+date_now()+'_'+time_now()+'.csv', 'a+', newline ='')
        with file:   
            write = csv.writer(file)
            write.writerows(self.csv_data)
        file.close()
        self.saveLabel.setText('Data baru sudah tersimpan')
        self.saveLabel.adjustSize()

    def pijat_worker(self):
        if self.thread3_state == 1:
            self.thread9_state += 1
            self.thread[9] = pijat_thread(self.thread9_state,parent=None)
            self.thread[9].start()
            self.thread[9].any_signal9.connect(self.pijat_action)

    def vibration_worker(self):
        if self.thread9_state % 2 == 1:
            self.thread[10] = vibration_thread(parent=None)
            self.thread[10].start()
            self.thread[10].any_signal10.connect(self.vibration_action)

    def heat_worker(self):
        if self.thread9_state % 2 == 1:
            self.thread[11] = heat_thread(parent=None)
            self.thread[11].start()
            self.thread[11].any_signal11.connect(self.heat_action)

    def pump_worker(self):
        if self.thread3_state == 1:
            self.thread12_state += 1
            self.thread[12] = pump_thread(self.thread12_state,parent=None)
            self.thread[12].start()
            self.thread[12].any_signal12.connect(self.pump_action)

    def pumpMode_worker(self):
        if self.thread12_state % 2 == 1:
            self.thread[13] = pumpMode_thread(parent=None)
            self.thread[13].start()
            self.thread[13].any_signal13.connect(self.pumpMode_action)

    def pumpUp_worker(self):
        if self.thread12_state % 2 == 1:
            self.thread[14] = pumpUp_thread(parent=None)
            self.thread[14].start()
            self.thread[14].any_signal14.connect(self.pumpUp_action)

    def pumpDown_worker(self):
        if self.thread12_state % 2 == 1:
            self.thread[15] = pumpDown_thread(parent=None)
            self.thread[15].start()
            self.thread[15].any_signal15.connect(self.pumpDown_action)

### ------------------------- ###

    def tutorial_action(self,var1):
        if var1 == 1:
            msg = QMessageBox()
            msg.setWindowTitle('Tutorial Window')
            msg.setText('Tutorial Main Text')
            msg.setInformativeText("Tutorial Informative Text!")
            msg.setDetailedText("Tutorial Details/Hidden Text")
            x = msg.exec_()

    def start_action_video(self,var2):
        self.window = QWidget()
        self.ui = VideoPlayer()
        self.ui.__init__(self.window)
        self.ui.resize(800,600)
        if var2 == 1:
            self.window.show()
        if var2 == 0:
            self.window.close()

    def start_action_getLoadcell(self,var2_1):
        self.realtimeASI.setText(str(var2_1))
        self.realtimeASI.adjustSize()
        self.realtimeVol = var2_1
        self.rec_newtime = time.time()
        if ((self.rec_newtime - self.rec_oldtime) >= self.rec_rate):
            self.csv_data_time.append(time_now())
            self.csv_data_vol.append(var2_1)
            self.rec_oldtime = self.rec_newtime
            self.volume_mode()
        # self.volume_mode()

    def start_action_massage(self,var2_2):
        print(var2_2)

    def start_action_EEG(self,var2_3):
        print(var2_3)

    def start_action_pump(self,var2_4):
        print(var2_4)

    def start_action_timer(self,var2_5):
        self.stop_worker()

    def tare_action(self,var3):
        pass

    def pijat_action(self,var4):
        if var4 == 1:
            self.vibrationButton.setEnabled(True)
            self.heatButton.setEnabled(True)
        else:
            self.vibrationButton.setEnabled(False)
            self.heatButton.setEnabled(False)

    def vibration_action(self,var5):
        pass

    def heat_action(self,var6):
        pass

    def pump_action(self,var7):
        print(var7)
        if var7 == 1:
            self.pumpMode_Button.setEnabled(True)
            self.pumpUp_Button.setEnabled(True)
            self.pumpDown_Button.setEnabled(True)
        else:
            self.pumpMode_Button.setEnabled(False)
            self.pumpUp_Button.setEnabled(False)
            self.pumpDown_Button.setEnabled(False)

    def pumpMode_action(self,var8):
        pass

    def pumpUp_action(self,var9):
        pass

    def pumpDown_action(Self,var10):
        pass

### ------------------------- ###

class tutorial_thread(QtCore.QThread):
    any_signal1 = QtCore.pyqtSignal(int)
    def __init__(self,parent=None):
        super(tutorial_thread,self).__init__(parent)
        self.is_running = True
    def run(self):
        print('Starting tutorial_thread...')
        self.any_signal1.emit(1)
    def stop(self):
        print('Stopping tutorial_thread...')
        self.is_running = False
        self.terminate()

class start_thread_video(QtCore.QThread):
    any_signal2 = QtCore.pyqtSignal(int)
    def __init__(self,parent=None):
        super(start_thread_video,self).__init__(parent)
        self.is_running = True
    def run(self):
        print('Starting start_thread_video...')
        self.any_signal2.emit(1)
    def stop(self):
        print('Stopping start_thread_video...')
        self.is_running = False
        self.any_signal2.emit(0)

class start_thread_getLoadcell(QtCore.QThread):
    any_signal3 = QtCore.pyqtSignal(int)
    def __init__(self,parent=None):
        super(start_thread_getLoadcell,self).__init__(parent)
        self.is_running = True
    def run(self):
        print('Starting start_thread_getLoadcell...')
        mass = 0
        vol = 0
        ser = serial.Serial('/dev/ttyUSB0',57600,timeout=1.5)
        ser.flush()
        ser.write(b't')
        time.sleep(0.1)
        while (True):
            if ser.in_waiting > 0:
                data = ser.read(9)
                data1 = data[1:5]
                data2 = data[5:9]
                mass = struct.unpack('<f', data1)[0]
                vol = struct.unpack('<f',data2)[0]
            time.sleep(0.01)
            self.any_signal3.emit(vol)
    def stop(self):
        print('Stopping start_thread_getLoadcell...')
        self.is_running = False
        self.terminate()

class start_thread_massage(QtCore.QThread):
    any_signal4 = QtCore.pyqtSignal(int)
    def __init__(self,parent=None):
        super(start_thread_massage,self).__init__(parent)
        self.is_running = True
    def run(self):
        self.any_signal4.emit(3)
    def stop(self):
        pass

class start_thread_EEG(QtCore.QThread):
    any_signal5 = QtCore.pyqtSignal(int)
    def __init__(self,parent=None):
        super(start_thread_EEG,self).__init__(parent)
        self.is_running = True
    def run(self):
        self.any_signal5.emit(4)
    def stop(self):
        pass

class start_thread_pump(QtCore.QThread):
    any_signal6 = QtCore.pyqtSignal(int)
    def __init__(self,parent=None):
        super(start_thread_pump,self).__init__(parent)
        self.is_running = True
    def run(self):
        self.any_signal6.emit(5)
    def stop(self):
        pass

class start_thread_timer(QtCore.QThread):
    any_signal7 = QtCore.pyqtSignal(int)
    def __init__(self,timer,parent=None):
        super(start_thread_timer,self).__init__(parent)
        self.is_running = True
        self.timer = timer
    def run(self):
        print('Starting start_thread_timer...')
        time.sleep(self.timer*60) # BISA
        self.any_signal7.emit(0) # index untuk nanti ngestop
    def stop(self):
        print('Stopping start_thread_timer...')
        self.is_running = False

class tare_thread(QtCore.QThread):
    any_signal8 = QtCore.pyqtSignal(int)
    def __init__(self, parent=None):
        super(tare_thread, self).__init__(parent)
        self.is_running = True
    def run(self):
        print('Starting tareLoadcell_thread...')
        mass = 0
        vol = 0
        ser = serial.Serial('/dev/ttyUSB0',57600,timeout=1.5)
        ser.reset_input_buffer()
        ser.write(b't')
        time.sleep(0.01)
        self.any_signal8.emit(vol)
    def stop(self):
        pass

class pijat_thread(QtCore.QThread):
    any_signal9 = QtCore.pyqtSignal(int)
    def __init__(self,state, parent=None):
        super(pijat_thread, self).__init__(parent)
        self.is_running = True
        self.state = state
    def run(self):
        print('Starting pijat_thread...')
        ser = serial.Serial('/dev/ttyUSB0',57600,timeout=1.5)
        ser.reset_input_buffer()
        if self.state % 2 == 1:
            ser.write(b's')
            self.any_signal9.emit(1)
        if self.state % 2 == 0:
            ser.write(b'p')
            self.any_signal9.emit(0)
        time.sleep(0.01)
    def stop(self):
        pass

class vibration_thread(QtCore.QThread):
    any_signal10 = QtCore.pyqtSignal(int)
    def __init__(self, parent=None):
        super(vibration_thread, self).__init__(parent)
        self.is_running = True
    def run(self):
        print('Starting vibration_thread...')
        ser = serial.Serial('/dev/ttyUSB0',57600,timeout=1.5)
        ser.reset_input_buffer()
        ser.write(b'v')
        time.sleep(0.01)
        self.any_signal10.emit(1)
    def stop(self):
        pass

class heat_thread(QtCore.QThread):
    any_signal11 = QtCore.pyqtSignal(int)
    def __init__(self, parent=None):
        super(heat_thread, self).__init__(parent)
        self.is_running = True
    def run(self):
        print('Starting heat_thread...')
        ser = serial.Serial('/dev/ttyUSB0',57600,timeout=1.5)
        ser.reset_input_buffer()
        ser.write(b'h')
        time.sleep(0.01)
        self.any_signal11.emit(1)
    def stop(self):
        pass

class pump_thread(QtCore.QThread):
    any_signal12 = QtCore.pyqtSignal(int)
    def __init__(self,state, parent=None):
        super(pump_thread, self).__init__(parent)
        self.is_running = True
        self.state = state
    def run(self):
        print('Starting pump_thread...')
        ser = serial.Serial('/dev/ttyUSB0',57600,timeout=1.5)
        ser.reset_input_buffer()
        ser.write(b'n')
        if self.state % 2 == 1:
            self.any_signal12.emit(1)
        if self.state % 2 == 0:
            self.any_signal12.emit(0) 
        time.sleep(0.01)
        # self.any_signal12.emit(1)
    def stop(self):
        pass

class pumpMode_thread(QtCore.QThread):
    any_signal13 = QtCore.pyqtSignal(int)
    def __init__(self,parent=None):
        super(pumpMode_thread, self).__init__(parent)
        self.is_running = True
    def run(self):
        print('Starting pumpMode_thread...')
        ser = serial.Serial('/dev/ttyUSB0',57600,timeout=1.5)
        ser.reset_input_buffer()
        ser.write(b'm') 
        time.sleep(0.01)
        self.any_signal13.emit(1)
    def stop(self):
        pass

class pumpUp_thread(QtCore.QThread):
    any_signal14 = QtCore.pyqtSignal(int)
    def __init__(self,parent=None):
        super(pumpUp_thread, self).__init__(parent)
        self.is_running = True
    def run(self):
        print('Starting pumpUp_thread...')
        ser = serial.Serial('/dev/ttyUSB0',57600,timeout=1.5)
        ser.reset_input_buffer()
        ser.write(b'u') 
        time.sleep(0.01)
        self.any_signal14.emit(1)
    def stop(self):
        pass

class pumpDown_thread(QtCore.QThread):
    any_signal15 = QtCore.pyqtSignal(int)
    def __init__(self,parent=None):
        super(pumpDown_thread, self).__init__(parent)
        self.is_running = True
    def run(self):
        print('Starting pumpDown_thread...')
        ser = serial.Serial('/dev/ttyUSB0',57600,timeout=1.5)
        ser.reset_input_buffer()
        ser.write(b'd') 
        time.sleep(0.01)
        self.any_signal15.emit(1)
    def stop(self):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen_res = app.desktop().screenGeometry()
    width, height = screen_res.width(), screen_res.height()
    print(width,height)

    MainWindow = threading()
    MainWindow.show()
    sys.exit(app.exec_())

def TODO_LOG():

# 1. Bikin data logger CSV untuk volume ASI, dan ditampilin secara
#    grafik di GUI
#       STEP:
#       ...
# 2. Bikin command button mesin pijat:
#    - Power
#    - Seat Vibration
#    - Heat
#    - Timer(?)  
# 3. Bikin command button mesin pompa:
#    - Power
#    - Mode
#    - Increase
#    - Decrease
# 4. Bikin multimedia window fullscreen

    pass

def PROBLEM_LOG():

# ------------------------------------------------------------------------
# 5
# PROBLEM:
#     Kadang muncul error begini:
#         Traceback (most recent call last):
#         File "/home/bimanjaya/learner/TA/main/mainWindow.py", line 272, in run
#         mass = struct.unpack('<f', data1)[0]
#         struct.error: unpack requires a buffer of 4 bytes
# IDE:
#     (PUZZLED)
# HASIL:
# ------------------------------------------------------------------------
# 6
# PROBLEM:
#     Kadang muncul error begini:
#         Starting tareLoadcell_thread...
#         Traceback (most recent call last):
#         File "/home/bimanjaya/learner/TA/main/mainWindow.py", line 269, in run
#             data = ser.read(9)
#         File "/home/bimanjaya/.conda/envs/selebor/lib/python3.6/site-packages/serial/serialposix.py", line 596, in read
#             'device reports readiness to read but returned no data '
#         serial.serialutil.SerialException: device reports readiness to read but returned no data (device disconnected or multiple access on port?)
#         Aborted (core dumped)
# IDE:
#     (PUZZLED)
# HASIL:
# ------------------------------------------------------------------------
# 7
# PROBLEM:
#     Kadang muncul error begini kalau nge-resize window videoplayer, dan
#     setelah selesai ngeklik 'STOP':
#         ...
#         QWidget::paintEngine: Should no longer be called
#         QWidget::paintEngine: Should no longer be called
#         QWidget::paintEngine: Should no longer be called
#         QWidget::paintEngine: Should no longer be called
#         Stopping start_thread_video...
#         Segmentation fault (core dumped)
# IDE:
#     (PUZZLED)
# HASIL:
# ------------------------------------------------------------------------
# 9
# PROBLEM:
#     Kalau videoplayer di close pake tanda silang window biasa, videoplayer
#     ga nge-close, tapi malah nge-hide doang (suaranya masih ada)
# IDE:
#     (PUZZLED)
# HASIL:
# ------------------------------------------------------------------------
# 10
# PROBLEM:
#     Kalau videoplayer window diresize (dengan cara drag), ukuran video
#     tidak berubah/tidak mengikuti ukuran resize window. Jadinya tetap
#     sesuai setting ukuran di kodingan. Dan kalau di-resize bisa2 muncul
#     PROBLEM no.7
# IDE:
#     (PUZZLED)
# HASIL:
# ------------------------------------------------------------------------
# 11
# PROBLEM:
#      Kalau sistem kelar ("STOP"), keterangan realtime volume ga balik ke 0
# IDE:
#      Ketika "STOP", labelnya ganti balik ke 0
# HASIL:
# ------------------------------------------------------------------------
# 12
# PROBLEM:
#     Ketika relay dimasukin ke sistem, ketika start (dimana ketika start relay 
#     sistem akan mengirimkan 'r' ke arduino), relay ga jalan, dan untuk bisa akuisisi
#     data load-cell, delaynya lama banget. bisa2 sampai 12 detik. tapi ketika sistem stop
#     relay mau gerak.
# IDE:
# HASIL:
# ------------------------------------------------------------------------

    pass

def PROBLEM_LOG_ARCHIEVED():

# ------------------------------------------------------------------------
# 1 - DONE
# PROBLEM:
#   Ketika 'START' diklik, ada beberapa section yang jalan bersamaan
#   tapi fungsi tiap thread hanya menjalankan satu thread
# IDE:
#   Dalam satu worker, buat 2/multiple thread
# HASIL:
#   - Sepertinya bisa
#       PROBLEM:
#           Ketika multiple worker dijalankan, kadang ada worker yang
#           -- entah kenapa -- tidak bisa menginisiasi fungsi action.
#           Entah worker yang nggak jalan atau action yg ga jalan
#       IDE:
#           Tambah time.sleep() tiap pemanggilan worker
#       HASIL:
#           BISA!
#   - BISA!
# ------------------------------------------------------------------------
# 2 - DONE
# PROBLEM:
#   Ketika diklik 'START' dan proses belum berhenti
#   tetapi diklik 'START' lagi. Window crash
# IDE:
#   Bikin filter biar ketika 'START' dah diklik
#   gabisa diklik lagi sebelum 'STOP'
# HASIL:
#   - Logika masih belum jalan dengan benar
#   - BISA! - Lupa ngasih kurung()
# ------------------------------------------------------------------------
# 3 - DONE
# PROBLEM:
#     Ketika /dev/ttyUSB0 ga terdeteksi maka window crash
# IDE:
#     Sebelum ngerun 'START', deteksi dulu ada 
#     /dev/ttyUSB0 ato ga. Kalo gaada, muncul pop-up peringatan 
#     "mikrokontroller tidak terdeteksi"
# HASIL:
#    BISA!
# ------------------------------------------------------------------------
# 4 - DONE
# PROBLEM:
#     Fitur timer belum berjalan
# IDE:
#     Bikin worker baru di start_worker yg bakal menjalankan timer_thread,
#     dimana timer_thread akan memberi feedback ke timer_action yang
#     akan menjalankan stop_worker
# HASIL:
#     BISA!
# ------------------------------------------------------------------------
# 8 - DONE
# PROBLEM:
#     'KALIBRASI' error kalau /dev/ttyUSB0 tidak terdeteksi
# IDE:
#     Sebelum ngerun 'KALIBRASI', deteksi dulu ada 
#     /dev/ttyUSB0 ato ga. Kalo gaada, muncul pop-up peringatan 
#     "mikrokontroller tidak terdeteksi"
#      eh
#      Gini aja, kalo udah 'START', 'KALIBRASI' kan ga masalah, jadi
#      sebelum 'KALIBRASI' detect dulu aja udah 'START' apa belum
# HASIL:
#      BISA!
# ------------------------------------------------------------------------
# 12 - DONE
# PROBLEM:
#      Ketika dah ditambahi fitur button setEnabled on atau off.. ketika sistem
#      distop manual melalui tombol "STOP", sistem crash. Kalau stop secara otomatis
#      melalui timer, sistem normal
# IDE:
#      Ada masalah di looping while timer. Kalo pake while trus di fungsi stop dikasi
#      self.terminate(), error. Kalo ga dikasi self.terminate(), ga error tapi loop fungsi run()
#      gabisa stop.
#
#      Timer utama sistem pake sistem time.sleep() aja
#      Nanti timer data_logger pake sistem (NEWTIME - OLDTIME) >= RATE
# HASIL:
#      BISA!

    pass

def FEATUREIDEA_LOG():

# 1. Kasih keterangan sisa waktu berjalan
# 2. Bisa custom nama file csv. Jadi ada popup dialog buat input string nama
# 3. Kasih docstring di tiap fungsi / class
    pass









