import sys
from PyQt5.QtWidgets import *
from PyQt5.QtSerialPort import QSerialPortInfo, QSerialPort
from PyQt5.QtCore import QIODevice, QTimer
from gui import Ui_MainWindow
import cv2
from PyQt5.QtGui import QImage, QPixmap
import struct
import csv
import pyqtgraph as pg
from PyQt5.QtGui import QOpenGLVersionProfile
from OpenGL import GL, GLU


#rotX : roll
#rotY : pitch
#rotZ : yaw


class GLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)

        self.rotX = 0.0
        self.rotY = 0.0
        self.rotZ = 0.0

        self.vertices =[]
        self.colors = []
        self.indices = []

    def read_obj(self):
        file_path = 'cubeObje.obj'
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith('v '):
                    self.vertices.extend(map(float, line.split()[1:4]))
                    #print(line.split()[1:4])

                elif line.startswith('c '):
                    self.colors.extend(map(float, line.split()[1:4]))
                    #print(line.split()[1:4])

                elif line.startswith('f '):
                    self.indices.extend(map(int, line.split()[1:]))
                    #print(line.split()[1:])

    def initializeGL(self):

        GL.glClearColor(0, 0, 0, 1)  # arkaplan rengi: siyah
        # Derinlik testini etkinleştirir, yani z-buffer'ı kullanarak nesnelerin birbirini engellemesini sağlar
        GL.glEnable(GL.GL_DEPTH_TEST)

        # Aydınlatmayı etkinleştirir
        GL.glEnable(GL.GL_LIGHTING)

        # Birinci Işık Kaynağı
        light0_position = [1.0, 1.0, 1.0, 0.0]  # X, Y, Z, 0.0: Sonsuz uzaklıkta bir ışık
        light0_ambient = [1.0, 1.0, 1.0, 1.0]  # R, G, B, A
        """
        ambient_intensity = 0.3  # Örnek: 0 ile 1 arasında bir değer
        ambient_light_color = [ambient_intensity, ambient_intensity, ambient_intensity, 1.0]
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_AMBIENT, ambient_light_color)
        """
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, light0_position)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_AMBIENT, light0_ambient)
        GL.glEnable(GL.GL_LIGHT0)

        # Renk malzemesini etkinleştirir. Renk malzemesi, nesnenin ışığa tepkisini kontrol eder.
        GL.glEnable(GL.GL_COLOR_MATERIAL)

        # Malzemenin ön ve arka yüzleri için hem yansıyan hem de yayılan ışığı etkinleştirir.
        GL.glColorMaterial(GL.GL_FRONT_AND_BACK, GL.GL_AMBIENT_AND_DIFFUSE)

        # Gouraud gölgelendirme modelini etkinleştirir. renk geçişlerini yumuşatır
        GL.glShadeModel(GL.GL_SMOOTH)

    def resizeGL(self, width, height):
        # OpenGL penceresinin boyutunu ayarla
        GL.glViewport(0, 0, width, height)

        # Projection matrisini ayarla
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()

        GLU.gluPerspective(45.0, width / float(height), 1.0, 100.0) #Görüş açısı,Genişlik / Yükseklik oranı,Kamera tarafından görülebilecek en yakın nesne,en uzak nesne

        # Modelview matrisine geçiş yap (nesnelerin dünyadaki konumlarını ve yönelimlerini tanımlar)
        GL.glMatrixMode(GL.GL_MODELVIEW)

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        GL.glLoadIdentity() ## Modelview matrisini sıfırlar

        GL.glPushMatrix() # mevcut matrisin bir kopyasını yığında saklar

        GL.glTranslatef(0.0, 0.0, -6.0)  # Kamerayı geri çek
        GL.glRotatef(self.rotX, 1.0, 0.0, 0.0)
        GL.glRotatef(self.rotY, 0.0, 1.0, 0.0)
        GL.glRotatef(self.rotZ, 0.0, 0.0, 1.0)

        # Eksenleri çiz
        GL.glLineWidth(2.0)  # Çizgi kalınlığını ayarla
        GL.glBegin(GL.GL_LINES)

        # X Ekseni (Kırmızı)
        GL.glColor3f(1.0, 0.0, 0.0)
        GL.glVertex3f(-5.0, 0.0, 0.0)
        GL.glVertex3f(5.0, 0.0, 0.0)

        # Y Ekseni (Yeşil)
        GL.glColor3f(0.0, 1.0, 0.0)
        GL.glVertex3f(0.0, -5.0, 0.0)
        GL.glVertex3f(0.0, 5.0, 0.0)

        # Z Ekseni (Mavi)
        GL.glColor3f(0.0, 0.0, 1.0)
        GL.glVertex3f(0.0, 0.0, -5.0)
        GL.glVertex3f(0.0, 0.0, 5.0)

        GL.glEnd()

        #çiz
        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        GL.glEnableClientState(GL.GL_COLOR_ARRAY)

        self.read_obj()

        GL.glVertexPointer(3, GL.GL_FLOAT, 0, self.vertices)
        GL.glColorPointer(3, GL.GL_FLOAT, 0, self.colors)

        GL.glDrawElements(GL.GL_QUADS, len(self.indices), GL.GL_UNSIGNED_INT, self.indices)

        GL.glDisableClientState(GL.GL_VERTEX_ARRAY)
        GL.glDisableClientState(GL.GL_COLOR_ARRAY)

        GL.glPopMatrix() #mevcut matrisin bir kopyasını yığında saklanan daha sonra yapı kullanılarak bu kopyaya geri dönülebilir


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.unitUI = Ui_MainWindow()
        self.unitUI.setupUi(self)

        self.serialPort = QSerialPort()
        self.serial_Port_List()

        self.unitUI.buttonConnect.clicked.connect(self.fonk_connect)
        self.unitUI.buttonDisconnect.clicked.connect(self.fonk_disconnect)

        self.vbox1 = QVBoxLayout()
        self.gl_widget = GLWidget()
        self.vbox1.addWidget(self.gl_widget)
        self.unitUI.tab_3.setLayout(self.vbox1)

        self.videoCapture = cv2.VideoCapture(0)
        self.videoLabel = QLabel(self)
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.videoLabel)
        self.unitUI.tab.setLayout(self.hbox)

        self.tableWidget = QTableWidget()
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.tableWidget)
        self.unitUI.tab_2.setLayout(self.vbox)

        self.init_graph()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        self.timer1 = QTimer(self)
        self.timer1.timeout.connect(self.update_simulation)

        self.yukseklik = 0
        self.sicaklik = 0
        self.IOTData = 0

        self.timer2 = QTimer(self)
        self.timer2.timeout.connect(self.graph_fonk)

        """
        self.timer = QtCore.QTimer()
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.graph_fonk)
        self.timer.start()
        """

        self.values = 0
        self.tableWidget.setRowCount(self.values +1)
        self.tableWidget.setColumnCount(6)
        header_list = ["yükseklik","sıcaklık","nem","roll","pitch","yaw"]
        self.tableWidget.setHorizontalHeaderItem(0,QTableWidgetItem(header_list[0]))
        self.tableWidget.setHorizontalHeaderItem(1,QTableWidgetItem(header_list[1]))
        self.tableWidget.setHorizontalHeaderItem(2,QTableWidgetItem(header_list[2]))
        self.tableWidget.setHorizontalHeaderItem(3, QTableWidgetItem(header_list[3]))
        self.tableWidget.setHorizontalHeaderItem(4, QTableWidgetItem(header_list[4]))
        self.tableWidget.setHorizontalHeaderItem(5, QTableWidgetItem(header_list[5]))
        #self.tableWidget.verticalHeader().hide() #satır isimlerini gizle

        csv_dosyasi = 'veri.csv'
        with open(csv_dosyasi, 'a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["yukseklik", "sicaklik", "nem","roll","pitch","yaw"])

        self.serialPort.readyRead.connect(self.data_received)

        ################################################
        self.serialPort1 = QSerialPort()
        self.serialPortList()

        self.t = 0
        self.yukseklik1 = 0
        self.sicaklik1 = 42
        self.IOTData1 = 35

        self.roll = 0
        self.pitch = 0
        self.yaw = 0
        self.unitUI.connectButton.clicked.connect(self.fonkConnect)
        self.unitUI.disconnectButton.clicked.connect(self.fonkDisconnect)
        self.unitUI.sendButton.clicked.connect(self.fonkButtonPush)

        self.unitUI.connectButton.setEnabled(True)
        self.unitUI.disconnectButton.setEnabled(False)
        self.unitUI.sendButton.setEnabled(False)
        ##################################################

    def update_simulation(self):
        self.gl_widget.update()

    def table_fonk(self,data1,data2,data3,data4,data5,data6):

        table_list = [str(data1), str(data2), str(data3), str(data4), str(data5), str(data6)]

        self.tableWidget.setItem(self.values, 0, QTableWidgetItem(table_list[0]))
        self.tableWidget.setItem(self.values, 1, QTableWidgetItem(table_list[1]))
        self.tableWidget.setItem(self.values, 2, QTableWidgetItem(table_list[2]))
        self.tableWidget.setItem(self.values, 3, QTableWidgetItem(table_list[3]))
        self.tableWidget.setItem(self.values, 4, QTableWidgetItem(table_list[4]))
        self.tableWidget.setItem(self.values, 5, QTableWidgetItem(table_list[5]))
        self.values += 1
        self.tableWidget.setRowCount(self.values +1)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def csv_file(self, data1, data2, data3,data4,data5,data6):
        csv_dosyasi = 'veri.csv'
        veri_paketi = [data1, data2, data3,data4,data5,data6]

        with open(csv_dosyasi, 'a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(veri_paketi)

    def init_graph(self):
        self.plot_item1 = pg.PlotItem()
        self.plot_item2 = pg.PlotItem()
        self.plot_item3 = pg.PlotItem()

        self.plot_widget1 = pg.GraphicsLayoutWidget()
        self.plot_widget2 = pg.GraphicsLayoutWidget()
        self.plot_widget3 = pg.GraphicsLayoutWidget()
        #self.plot_widget.setBackground('w')  # Beyaz arka plan

        self.plot_data_item1 = self.plot_item1.plot(pen='b')  # Mavi çizgi
        self.plot_data_item2 = self.plot_item2.plot(pen='g')
        self.plot_data_item3 = self.plot_item3.plot(pen='r')

        #self.plot_item.setTitle("Gerçek Zamanlı Grafik")
        #self.plot_item.setLabel('bottom', text='Zaman', units='s')
        #self.plot_item.setLabel('left', text='Değer')

        # X ve Y eksenlerinin rengi
        #self.plot_item.getAxis('bottom').setPen(pg.mkPen(color='black'))  # X eksen
        #self.plot_item.getAxis('left').setPen(pg.mkPen(color='black'))  # Y eksen

        self.x_values1 = []
        self.y_values1 = []
        self.x_values2 = []
        self.y_values2 = []
        self.x_values3 = []
        self.y_values3 = []

        self.plot_widget1.addItem(self.plot_item1)
        self.plot_widget2.addItem(self.plot_item2)
        self.plot_widget3.addItem(self.plot_item3)

        self.unitUI.vbox.addWidget(self.plot_widget1)
        self.unitUI.vbox.addWidget(self.plot_widget2)
        self.unitUI.vbox.addWidget(self.plot_widget3)


    def graph_fonk(self):
        self.x_values1.append(len(self.x_values1))
        self.y_values1.append(float(self.yukseklik))
        self.x_values2.append(len(self.x_values2))
        self.y_values2.append(float(self.sicaklik))
        self.x_values3.append(len(self.x_values3))
        self.y_values3.append(float(self.IOTData))

        self.plot_data_item1.setData(x=self.x_values1, y=self.y_values1)
        self.plot_data_item2.setData(x=self.x_values2, y=self.y_values2)
        self.plot_data_item3.setData(x=self.x_values3, y=self.y_values3)


    def update_frame(self):
        ret, frame = self.videoCapture.read()
        if ret:
            height, width, channel = frame.shape
            bytesPerLine = 3 * width
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            qImage = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)

            pixmap = QPixmap.fromImage(qImage)
            self.videoLabel.setPixmap(pixmap)

    def closeEvent(self, event):
        self.videoCapture.release()

    def fonk_connect(self):
        self.serialPort.setPortName(self.unitUI.comboBox.currentText())
        self.serialPort.setBaudRate(QSerialPort.Baud9600)
        self.serialPort.setDataBits(QSerialPort.Data8)
        self.serialPort.setParity(QSerialPort.EvenParity)
        self.serialPort.setStopBits(QSerialPort.OneStop)

        if not self.serialPort.isOpen():
            self.serialPort.open(QIODevice.ReadWrite)

            self.unitUI.buttonConnect.setEnabled(False)
            self.unitUI.buttonDisconnect.setEnabled(True)

            self.unitUI.comboBox.setEnabled(False)

            self.timer.start(24)
            self.timer1.start(1000)
            self.timer2.start(1000)

    def fonk_disconnect(self):
        if self.serialPort.isOpen():
            self.serialPort.close()

            self.unitUI.buttonConnect.setEnabled(True)
            self.unitUI.buttonDisconnect.setEnabled(False)

            self.unitUI.comboBox.setEnabled(True)

            self.timer.stop()
            self.timer1.stop()
            self.timer2.stop()

    def data_received(self):
        raw_data = self.serialPort.read(24)
        self.yukseklik, self.sicaklik, self.IOTData, self.gl_widget.rotX, self.gl_widget.rotY, self.gl_widget.rotZ = struct.unpack('!ffffff', raw_data)
        #map(float, raw_data.split(',')))
        print("Yükseklik:", self.yukseklik, "Sıcaklık:", self.sicaklik, "IOT Data:", self.IOTData, "roll:", self.gl_widget.rotX, "pitch:", self.gl_widget.rotY, "yaw:", self.gl_widget.rotZ)
        self.csv_file(self.yukseklik,self.sicaklik,self.IOTData,self.gl_widget.rotX,self.gl_widget.rotY,self.gl_widget.rotZ)
        self.table_fonk(self.yukseklik,self.sicaklik,self.IOTData,self.gl_widget.rotX,self.gl_widget.rotY,self.gl_widget.rotZ)

    def serial_Port_List(self):
        serialPortInfo = QSerialPortInfo()
        for serialPort in serialPortInfo.availablePorts():
            self.unitUI.comboBox.addItem(serialPort.portName())

    ############################################################
    def serialPortList(self):
        serialPortInfo = QSerialPortInfo()
        for serialPort in serialPortInfo.availablePorts():
            self.unitUI.comboBox1.addItem(serialPort.portName())

    def fonkConnect(self):
        self.serialPort1.setPortName(self.unitUI.comboBox1.currentText())

        self.serialPort1.setBaudRate(QSerialPort.Baud9600)
        self.serialPort1.setDataBits(QSerialPort.Data8)
        self.serialPort1.setParity(QSerialPort.EvenParity)
        self.serialPort1.setStopBits(QSerialPort.OneStop)

        if not self.serialPort1.isOpen():
            self.serialPort1.open(QIODevice.WriteOnly)

            self.unitUI.connectButton.setEnabled(False)
            self.unitUI.disconnectButton.setEnabled(True)
            self.unitUI.sendButton.setEnabled(True)

    def fonkDisconnect(self):
        self.timer.stop()

        if self.serialPort1.isOpen():
            self.serialPort1.close()

            self.unitUI.connectButton.setEnabled(True)
            self.unitUI.disconnectButton.setEnabled(False)
            self.unitUI.sendButton.setEnabled(False)

    def fonkButtonPush(self):
        self.unitUI.sendButton.setEnabled(False)
        self.timer = QTimer()
        self.timer.timeout.connect(self.fonkValues)
        self.timer.start(1000)

    def fonkSendData(self):
        self.veriPaketi = struct.pack('!ffffff', self.yukseklik1, self.sicaklik1, self.IOTData1, self.roll, self.pitch, self.yaw)
        print(self.veriPaketi)
        self.serialPort1.write(self.veriPaketi)

        self.unitUI.connectButton.setEnabled(False)
        self.unitUI.disconnectButton.setEnabled(True)

    def fonkValues(self):
        self.sicaklik1 = self.sicaklik1 - 0.2
        self.yukseklik1 = 4.9 * self.t * self.t
        self.IOTData1 = self.IOTData1 - 0.1

        self.roll = self.roll + 1
        self.pitch = self.pitch + 1
        self.yaw = self.yaw + 1

        self.t = self.t + 1

        self.fonkSendData()
    #################################3

def main():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()