from brainflow.ml_model import MLModel, BrainFlowMetrics, BrainFlowClassifiers, BrainFlowModelParams
from brainflow.data_filter import DataFilter, WindowOperations, DetrendOperations, FilterTypes
from brainflow.data_filter import DataFilter, WindowOperations, DetrendOperations, FilterTypes
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from sklearn.model_selection import train_test_split, cross_val_score
from PyQt5.QtWidgets import QMessageBox, QWidget, QApplication
from sklearn.metrics import classification_report
from PyQt5 import QtCore, QtWidgets, QtGui, uic
from multimediav2 import VideoPlayer
from joblib import dump,load
from sklearn.svm import SVC
import matplotlib.pyplot as plt ####
import serial.tools.list_ports
import seaborn as sns ###
import pandas as pd ###
import numpy as np
import argparse 
import datetime
import serial 
import struct
import time
import sys 
import csv 

x = 0
eegRealtime = 0
volRealtime = 0
volRealtime_old = 0
eegRealtime2 = 0
csv_data_time = []
csv_data_vol = []
csv_data_eeg = []
csv_data_relax = []

def serial_checker():
    port_name = ''
    ports = serial.tools.list_ports.comports()
    # for port,desc,hwid in sorted(ports)[1]:
    #     port_name = port
    #     port_desc = desc
    #     port_hwid = hwid
    # print(sorted(ports)[0][0])
    # print(sorted(ports)[1][0])
    # print(sorted(ports)[2][0])
    # print(port_name)
    # return port_name
    return sorted(ports)[1][0]

def time_now():
    now = datetime.datetime.now().strftime("%H:%M:%S")
    return str(now)

def date_now():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    today = str(today)
    return today

def initialize_eeg():
    global loaded,params,board,keep_alive,sampling_rate,delay,eeg_channel1,eeg_channel2,eeg_channel3,eeg_channel4,master_board_id,nfft,eeg_channelss

    loaded = load('/home/bimanjaya/learner/TA/brainflow/EEG-projects/src/model1.joblib')
    # loaded = load('/home/san/Downloads/EEG-projects-backup-main/src/model1.joblib') 
    delay = 5

    BoardShim.enable_board_logger()
    DataFilter.enable_data_logger()

    params = BrainFlowInputParams()
    params.serial_port = '/dev/ttyACM0'
    params.timeout = 15

    board = BoardShim(BoardIds.GANGLION_BOARD.value, params)
    master_board_id = board.get_board_id()
    sampling_rate = BoardShim.get_sampling_rate(master_board_id)
    nfft = DataFilter.get_nearest_power_of_two(sampling_rate)
    timestamp = BoardShim.get_timestamp_channel(master_board_id)
    board_descr = BoardShim.get_board_descr(master_board_id)
    eeg_channelss = BoardShim.get_eeg_channels(int(master_board_id))

    eeg_channels = board_descr['eeg_channels']
    eeg_channel1 = eeg_channels[0]
    eeg_channel2 = eeg_channels[1]
    eeg_channel3 = eeg_channels[2]
    eeg_channel4 = eeg_channels[3]

    keep_alive = True

class plotWindow(QtWidgets.QMainWindow):
    def __init__(self):
        global csv_data_time,csv_data_eeg,csv_data_vol
        QtWidgets.QMainWindow.__init__(self)
        self.ui = uic.loadUi('/home/bimanjaya/learner/TA/relaxation-chair-GUI/plot-pc.ui',self)
        # self.ui = uic.loadUi('/home/san/Downloads/relaxation-chair-GUI-main/plot.ui',self)

        # mainWindow = threading()

        self.MplWidget.canvas.axes.clear()
        self.MplWidget.canvas.axes.plot(csv_data_time, csv_data_vol)
        xmin, xmax = self.MplWidget.canvas.axes.get_xlim()
        self.MplWidget.canvas.axes.set_xticks(np.round(np.linspace(xmin, xmax, 5), 2))
        self.MplWidget.canvas.draw()

        self.MplWidget2.canvas.axes.clear()
        self.MplWidget2.canvas.axes.plot(csv_data_time, csv_data_eeg)
        xmin, xmax = self.MplWidget2.canvas.axes.get_xlim()
        self.MplWidget2.canvas.axes.set_xticks(np.round(np.linspace(xmin, xmax, 5), 2))
        self.MplWidget2.canvas.draw()

        self.MplWidget3.canvas.axes.clear()
        self.MplWidget3.canvas.axes.plot(csv_data_time, csv_data_relax)
        xmin, xmax = self.MplWidget3.canvas.axes.get_xlim()
        self.MplWidget3.canvas.axes.set_xticks(np.round(np.linspace(xmin, xmax, 5), 2))
        self.MplWidget3.canvas.draw()

class threading(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = uic.loadUi('/home/bimanjaya/learner/TA/relaxation-chair-GUI/sistem-kursi-relaksasi-v6-pc.ui',self)
        # self.ui = uic.loadUi('/home/san/Downloads/relaxation-chair-GUI-main/sistem-kursi-relaksasi-v6-pc.ui',self)

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
        self.plotButton.clicked.connect(self.newWindow_plot)

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
        self.plotButton.setEnabled(False)

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
        self.thread16_state = 0 # eeg 2
        self.thread17_state = 0 # batt

        self.realtimeVol = 0
        self.eegData = 0.0
        self.eegData2 = 0.0
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

        initialize_eeg()

        # self.batt_worker()

        board.prepare_session()
        board.start_stream()
        BoardShim.log_message(LogLevels.LEVEL_INFO.value, 'start sleeping in the main thread')
    
### ------------------------- ###

    def show_vol_graph(self):
        self.MplWidget.canvas.axes.clear()
        self.MplWidget.canvas.axes.plot(self.csv_data_time, self.csv_data_vol)
        xmin, xmax = self.MplWidget.canvas.axes.get_xlim()
        self.MplWidget.canvas.axes.set_xticks(np.round(np.linspace(xmin, xmax, 5), 2))
        self.MplWidget.canvas.draw()

        self.MplWidget2.canvas.axes.clear()
        self.MplWidget2.canvas.axes.plot(self.csv_data_time, self.csv_data_eeg)
        xmin, xmax = self.MplWidget2.canvas.axes.get_xlim()
        self.MplWidget2.canvas.axes.set_xticks(np.round(np.linspace(xmin, xmax, 5), 2))
        self.MplWidget2.canvas.draw()

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
    
    def newWindow_plot(self):
        window2 = plotWindow()
        window2.show()

### ------------------------- ###

    def tutorial_worker(self):
        self.thread[1] = tutorial_thread(parent=None)
        self.thread[1].start()
        self.thread1_state = 1
        self.thread[1].any_signal1.connect(self.tutorial_action)

    def start_default(self):

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
        self.plotButton.setEnabled(False)
        # self.MplWidget.canvas.axes.clear()
        # self.MplWidget.canvas.draw()
        # self.MplWidget2.canvas.axes.clear()
        # self.MplWidget2.canvas.draw()

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

        # # START GET EEG DATA
        # self.thread[16] = start_thread_EEG2(parent=None)
        # self.thread[16].start()
        # self.thread[16].any_signal16.connect(self.start_action_EEG2)
        # self.thread16_state = 1
        # time.sleep(0.2)

        self.csv_data = []
        self.csv_data_time = []
        self.csv_data_vol = []
        self.csv_data_eeg = []
        self.csv_data_relax = []
        self.rec_oldtime = time.time()
        self.rec_newtime = self.rec_oldtime
        self.rec_i = 0
        self.saveLabel.setText('Sistem sedang berjalan')
        self.saveLabel.adjustSize()
        self.thread9_state = 0

    def start_worker(self):

        if self.x == 'Timer':

            if self.timeSpinBox.value() > 0:
                
                if ((self.thread2_state and self.thread3_state and self.thread4_state 
                and self.thread5_state and self.thread6_state and self.thread7_state) == 0):

                    if serial_checker() == '/dev/ttyUSB0':

                        self.start_default()
                        
                        # START TIMER
                        self.thread[7] = start_thread_timer(self.timeSpinBox.value(),parent=None)
                        self.thread[7].start()
                        self.thread[7].any_signal7.connect(self.start_action_timer)
                        self.thread7_state = 1
                        time.sleep(0.2)

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

                            self.start_default()                            

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
        global csv_data_time,csv_data_vol,csv_data_eeg,csv_data_relax

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
        self.plotButton.setEnabled(True)
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
        if self.thread16_state == 1:
            self.thread[16].stop()
            self.thread16_state = 0
        # if self.thread17_state == 1:
        #     self.thread[17].stop()
        #     self.thread17_state = 0

        self.saveLabel.setText('Ada data belum tersimpan')
        self.saveLabel.adjustSize()
        self.realtimeASI.setText('0')
        self.realtimeASI.adjustSize()
        # self.show_vol_graph()

        csv_data_time = self.csv_data_time
        csv_data_vol = self.csv_data_vol
        csv_data_eeg = self.csv_data_eeg
        csv_data_relax = self.csv_data_relax

    def save_worker(self):
        for i in self.csv_data_time:
            self.csv_data.append([i])
        j = 0.0
        for j in self.csv_data_vol:
            self.csv_data[self.rec_i].append(j)
            self.rec_i += 1
        self.rec_i = 0
        k=0.0
        for k in self.csv_data_eeg:
            self.csv_data[self.rec_i].append(k)
            self.rec_i += 1
        self.rec_i = 0
        l = 0.0
        for l in self.csv_data_relax:
            self.csv_data[self.rec_i].append(l)
            self.rec_i += 1

        print(self.csv_data)
        # file = open('/home/san/load_cell/'+date_now()+'_'+time_now()+'.csv', 'w', newline ='')
        file = open('/home/bimanjaya/learner/TA/relaxation-chair-GUI/data_logger/load_cell/'+date_now()+'_'+time_now()+'.csv', 'w', newline ='')
        with file:
            header = ['Waktu', 'Vol ASI', 'Relaksasi EEG', 'Relaksasi User']
            writer = csv.DictWriter(file, fieldnames = header)
            writer.writeheader()
        file.close()
        # file = open('/home/san/load_cell/'+date_now()+'_'+time_now()+'.csv', 'a+', newline ='')
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

    def batt_worker(self):
        self.thread[17] = start_thread_getBatt(parent=None)
        self.thread[17].start()
        self.thread[17].any_signal17.connect(self.start_action_getBatt)
        self.thread17_state = 1
        time.sleep(0.2)

    def relaxState_worker(self):
        global x
        if x % 2 == 0:
            x = 1
        else:
            x = 0
        # print(x)

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
        global x
        x = 0
        self.window = QWidget()
        self.ui = VideoPlayer()
        self.ui.__init__(self.window)
        self.ui.resize(1875,1000)
        self.ui.relaxButton.clicked.connect(self.relaxState_worker)
        if var2 == 1:
            self.window.show()
        if var2 == 0:
            self.window.close()

    def start_action_getLoadcell(self,var2_1):
        # print(f'vol sent : {var2_1}')
        global volRealtime, x
        self.realtimeVol = volRealtime
        self.realtimeASI.setText(str(self.realtimeVol))
        self.realtimeASI.adjustSize()
        self.rec_newtime = time.time()
        if ((self.rec_newtime - self.rec_oldtime) >= self.rec_rate):
            self.csv_data_time.append(time_now())
            self.csv_data_vol.append(self.realtimeVol)
            self.csv_data_eeg.append(self.eegData)
            self.csv_data_relax.append(x)
            self.rec_oldtime = self.rec_newtime
            self.volume_mode()

    def start_action_massage(self,var2_2):
        print(var2_2)

    def start_action_EEG(self,var2_3=0.0):
        global eegRealtime
        self.eegData = eegRealtime
        # print(f'EEG sent : {self.eegData}')
        self.realtimeEEG.setText(str(self.eegData))

    def start_action_EEG2(self,var16=0.0):
        global eegRealtime2
        self.eegData2 = eegRealtime2
        self.realtimeEEG2.setText(str(eegRealtime2))

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

    def pumpDown_action(self,var10):
        pass

    def start_action_getBatt(self,var11):
        # print(var11)
        self.battSOC.setText(str(var11[0]))
        if var11[1] == 0.0:
            self.battStatus.setText('Charging')
        else:
            self.battStatus.setText('Discharging')

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
        global volRealtime,volRealtime_old
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
            volRealtime = round(vol)
            if volRealtime < volRealtime_old:
                volRealtime = volRealtime_old
            volRealtime_old = volRealtime
            # print(f'vol : {vol}')
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
        self.keep_alive = keep_alive
    def run(self):
        global eegRealtime
        while self.keep_alive == True:
            while board.get_board_data_count() < 1000:pass
                # print('waiting 5 seconds')
            data = board.get_current_board_data(1000)
            total_iterate = data.shape[1] // (sampling_rate*delay)

            # dict = {'alpha1':[],'alpha2':[],'alpha3':[],'alpha4':[],
            # 'beta1':[],'beta2':[],'beta3':[],'beta4':[]}
            # df = pd.DataFrame(dict)

            # print('')
            # print('---------- start iteration ----------')
            # print('')
            for x in range(total_iterate):
                ch1_iter = data[eeg_channel1][(x*1000):((x+1)*1000)]
                ch2_iter = data[eeg_channel2][(x*1000):((x+1)*1000)]
                ch3_iter = data[eeg_channel3][(x*1000):((x+1)*1000)]
                ch4_iter = data[eeg_channel4][(x*1000):((x+1)*1000)]
                
                DataFilter.detrend(ch1_iter, DetrendOperations.LINEAR.value)
                DataFilter.detrend(ch2_iter, DetrendOperations.LINEAR.value)
                DataFilter.detrend(ch3_iter, DetrendOperations.LINEAR.value)
                DataFilter.detrend(ch4_iter, DetrendOperations.LINEAR.value)
                
                DataFilter.perform_bandpass(ch1_iter, BoardShim.get_sampling_rate(master_board_id), 5.0, 35.0, 4,
                                                    FilterTypes.BUTTERWORTH.value, 0)
                DataFilter.perform_bandpass(ch2_iter, BoardShim.get_sampling_rate(master_board_id), 5.0, 35.0, 4,
                                                    FilterTypes.BUTTERWORTH.value, 0)
                DataFilter.perform_bandpass(ch3_iter, BoardShim.get_sampling_rate(master_board_id), 5.0, 35.0, 4,
                                                    FilterTypes.BUTTERWORTH.value, 0)
                DataFilter.perform_bandpass(ch4_iter, BoardShim.get_sampling_rate(master_board_id), 5.0, 35.0, 4,
                                                    FilterTypes.BUTTERWORTH.value, 0)
                
                psd1 = DataFilter.get_psd_welch(ch1_iter, nfft, nfft // 2, sampling_rate,
                                            WindowOperations.HAMMING.value)
                psd2 = DataFilter.get_psd_welch(ch2_iter, nfft, nfft // 2, sampling_rate,
                                            WindowOperations.HAMMING.value)
                psd3 = DataFilter.get_psd_welch(ch3_iter, nfft, nfft // 2, sampling_rate,
                                            WindowOperations.HAMMING.value)
                psd4 = DataFilter.get_psd_welch(ch4_iter, nfft, nfft // 2, sampling_rate,
                                            WindowOperations.HAMMING.value)
                
                band_power_total1 = DataFilter.get_band_power(psd1, psd1[1][0], psd1[1][-1])
                band_power_total2 = DataFilter.get_band_power(psd2, psd2[1][0], psd2[1][-1])
                band_power_total3 = DataFilter.get_band_power(psd3, psd3[1][0], psd3[1][-1])
                band_power_total4 = DataFilter.get_band_power(psd4, psd4[1][0], psd4[1][-1])
                
                band_power_alpha1 = DataFilter.get_band_power(psd1, 8.0, 13.0)
                band_power_alpha2 = DataFilter.get_band_power(psd2, 8.0, 13.0)
                band_power_alpha3 = DataFilter.get_band_power(psd3, 8.0, 13.0)
                band_power_alpha4 = DataFilter.get_band_power(psd4, 8.0, 13.0)
                
                alpha_relative1 = band_power_alpha1/band_power_total1
                alpha_relative2 = band_power_alpha2/band_power_total2
                alpha_relative3 = band_power_alpha3/band_power_total3
                alpha_relative4 = band_power_alpha4/band_power_total4
                
                band_power_beta1 = DataFilter.get_band_power(psd1, 13.0, 32.0)
                band_power_beta2 = DataFilter.get_band_power(psd2, 13.0, 32.0)
                band_power_beta3 = DataFilter.get_band_power(psd3, 13.0, 32.0)
                band_power_beta4 = DataFilter.get_band_power(psd4, 13.0, 32.0)
                
                beta_relative1 = band_power_beta1/band_power_total1
                beta_relative2 = band_power_beta2/band_power_total2
                beta_relative3 = band_power_beta3/band_power_total3
                beta_relative4 = band_power_beta4/band_power_total4
                
                dataset = [alpha_relative1,alpha_relative2,
                            alpha_relative3,alpha_relative4,
                            beta_relative1,beta_relative2,
                            beta_relative3,beta_relative4]

            # print(f'EEG : {loaded.predict_proba([dataset])[0][0]}')
            eegRealtime = round(loaded.predict_proba([dataset])[0][0],3)
            self.any_signal5.emit(loaded.predict_proba([dataset])[0][0]*100)
        
    def stop(self):
        self.keep_alive = False

class start_thread_EEG2(QtCore.QThread):
    any_signal16 = QtCore.pyqtSignal(int)
    def __init__(self,parent=None):
        super(start_thread_EEG2,self).__init__(parent)
        self.is_running = True
        self.keep_alive = keep_alive
    def run(self):
        global eeg_channelss,eegRealtime2
        while self.keep_alive == True:
            while board.get_board_data_count() < 1000:pass
                # print('waiting 5 seconds')
            data = board.get_current_board_data(1000)
            bands = DataFilter.get_avg_band_powers(data, eeg_channelss, sampling_rate, True)
            feature_vector = bands[0]

            restfulness_params = BrainFlowModelParams(BrainFlowMetrics.RESTFULNESS.value,
                                                BrainFlowClassifiers.DEFAULT_CLASSIFIER.value)
            restfulness = MLModel(restfulness_params)
            restfulness.prepare()
            result = round(restfulness.predict(feature_vector)[0],3)
            # print('')
            # print('Restfulness: %s' % str(result))
            # print('')
            restfulness.release()
            eegRealtime2 = result
            self.any_signal16.emit(0)
    def stop(self):
        self.keep_alive = False

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
        global volRealtime,volRealtime_old
        print('Starting tareLoadcell_thread...')
        mass = 0
        vol = 0
        ser = serial.Serial('/dev/ttyUSB0',57600,timeout=1.5)
        ser.reset_input_buffer()
        ser.write(b't')
        time.sleep(0.01)
        volRealtime_old = 0
        volRealtime = 0 
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

class start_thread_getBatt(QtCore.QThread):
    any_signal17 = QtCore.pyqtSignal(list)
    def __init__(self,parent=None):
        super(start_thread_getBatt,self).__init__(parent)
        self.is_running = True
    def run(self):
        print('Starting start_thread_getBatt...')
        soc = 0
        state = 0
        ser = serial.Serial('/dev/ttyUSB1',57600,timeout=1.5)
        ser.flush()
        time.sleep(0.1)
        while (True):
            if ser.in_waiting > 0:
                data = ser.read(9)
                data1 = data[1:5]
                data2 = data[5:9]
                soc = struct.unpack('<f', data1)[0]
                state = struct.unpack('<f', data2)[0]
            time.sleep(0.01)
            # print(soc)
            self.any_signal17.emit([soc,state])
    def stop(self):
        print('Stopping start_thread_getBatt...')
        self.is_running = False
        self.terminate()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen_res = app.desktop().screenGeometry()
    width, height = screen_res.width(), screen_res.height()
    print(width,height)

    MainWindow = threading()
    MainWindow.show()
    sys.exit(app.exec_())

def TODO_LOG():

# 1. Bikin data logger state relaksasi yg manual dari pushButton
#    dan ditampilin juga di grafik

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
# 14
# PROBLEM:
#      Kalau sistem pakai 2 Arduino, seringkali muncul error no 5
#           mass = struct.unpack('<f', data1)[0]
#           struct.error: unpack requires a buffer of 4 bytes
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
# ------------------------------------------------------------------------
# 13
# PROBLEM:
#     Ketika relay dimasukin ke sistem, ketika start (dimana ketika start relay 
#     sistem akan mengirimkan 'r' ke arduino), relay ga jalan, dan untuk bisa akuisisi
#     data load-cell, delaynya lama banget. bisa2 sampai 12 detik. tapi ketika sistem stop
#     relay mau gerak.
# IDE: 
#     (gatau lupa)
# HASIL: 
#     BISA!
# ------------------------------------------------------------------------

    pass

def FEATUREIDEA_LOG():

# 1. Kasih keterangan sisa waktu berjalan
# 2. Bisa custom nama file csv. Jadi ada popup dialog buat input string nama
# 3. Kasih docstring di tiap fungsi / class
    pass









