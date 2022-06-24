from PyQt5 import QtCore, QtWidgets, QtGui, uic
from PyQt5.QtWidgets import QMessageBox, QWidget, QApplication
from multimediav1 import VideoPlayer
import serial.tools.list_ports
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
    now = str(now)
    return now

def date_now():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    today = str(today)
    return today

class threading(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = uic.loadUi('/home/bimanjaya/learner/TA/relaxation-chair-GUI/sistem-kursi-relaksasi.ui',self)

        self.thread = {}
        self.tutorialButton.clicked.connect(self.tutorial_worker)
        self.startButton.clicked.connect(self.start_worker)
        self.stopButton.clicked.connect(self.stop_worker)
        self.saveButton.clicked.connect(self.save_worker)
        self.tareButton.clicked.connect(self.tare_worker)

        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.saveButton.setEnabled(False)
        self.tareButton.setEnabled(False)

        self.thread1_state = 0
        self.thread2_state = 0
        self.thread3_state = 0
        self.thread4_state = 0
        self.thread5_state = 0
        self.thread6_state = 0
        self.thread7_state = 0

    def tutorial_worker(self):
        self.thread[1] = tutorial_thread(parent=None)
        self.thread[1].start()
        self.thread1_state = 1
        self.thread[1].any_signal1.connect(self.tutorial_action)

    def start_worker(self):

        # Bikin fungsi if buat ngecek adanya timer
        if self.timeSpinBox.value() > 0:
            
            if ((self.thread2_state and self.thread3_state and self.thread4_state 
            and self.thread5_state and self.thread6_state and self.thread7_state) == 0):

                if serial_checker() == '/dev/ttyUSB0':

                    self.startButton.setEnabled(False)
                    self.stopButton.setEnabled(True)
                    self.saveButton.setEnabled(False)
                    self.tareButton.setEnabled(True)

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

    def save_worker(self):
        pass

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

    def stop_action(self,var4):
        pass

    def save_action(self,var5):
        pass

class tutorial_thread(QtCore.QThread):
    any_signal1 = QtCore.pyqtSignal(int)
    def __init__(self,parent=None):
        super(tutorial_thread,self).__init__(parent)
        self.is_running = True
    def run(self):
        print('starting tutorial_thread')
        self.any_signal1.emit(1)
    def stop(self):
        print('stopping tutorial_thread')
        self.is_running = False
        self.terminate()

class start_thread_video(QtCore.QThread):
    any_signal2 = QtCore.pyqtSignal(int)
    def __init__(self,parent=None):
        super(start_thread_video,self).__init__(parent)
        self.is_running = True
        self.state = 0
    def run(self):
        print('Starting start_thread_video...')
        self.any_signal2.emit(1)
        self.state = 1
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
        # self.time_old = time.perf_counter()
        # timing = self.time_old + (self.timer*60)
        # while (time.perf_counter() < timing):
        #     remain = round(timing - time.perf_counter())
        # time.sleep(0.01)
        # time.sleep(self.timer*60) # BISA

        # self.time_old = time.time()
        # timing = self.time_old + (self.timer*60)
        # while (time.time() < timing):
        #     remain = round(timing - time.time())
        #     print(remain)

        self.time_old = time.time()
        timing = self.time_old + (self.timer*60)
        while (True):
            if (time.time() < timing):
                remain = round(timing - time.time())
                print(remain)
            else:
                self.any_signal7.emit(0) # index untuk nanti ngestop        

        # self.any_signal7.emit(0) # index untuk nanti ngestop
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
#      Ketika dah ditambahi fitur button setEnabled on atau off.. ketika sistem
#      distop manual melalui tombol "STOP", sistem crash. Kalau stop secara otomatis
#      melalui timer, sistem normal
# IDE:
#      Ada masalah di looping while timer. Kalo pake while trus di fungsi stop dikasi
#      self.terminate(), error. Kalo ga dikasi self.terminate(), ga error tapi loop fungsi run()
#      gabisa stop.
# HASIL:
# ------------------------------------------------------------------------
#      


    pass

def FEATUREIDEA_LOG():

# 1. Kasih keterangan sisa waktu berjalan

    pass




