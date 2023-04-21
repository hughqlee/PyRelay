import sys

from pyrelay import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lib = loadLib()
        self.dev = None
        self.numch = None
        self.channels = []
        self.labels = []

        self.status_label = QLabel('Closed')

        btn_find = QPushButton('findDevice')
        btn_find.clicked.connect(self.click_btn_find)

        self.combo_box = QComboBox()
        self.combo_box.currentIndexChanged.connect(self.change_combo)

        self.channel_1 = QPushButton('Relay Channel 1')
        self.channel_2 = QPushButton('Relay Channel 2')
        self.channel_3 = QPushButton('Relay Channel 3')
        self.channel_4 = QPushButton('Relay Channel 4')
        self.channel_5 = QPushButton('Relay Channel 5')
        self.channel_6 = QPushButton('Relay Channel 6')
        self.channel_7 = QPushButton('Relay Channel 7')
        self.channel_8 = QPushButton('Relay Channel 8')
        self.channel_1.clicked.connect(lambda: self.click_btn_channel(1))
        self.channel_2.clicked.connect(lambda: self.click_btn_channel(2))
        self.channel_2.clicked.connect(lambda: self.click_btn_channel(3))
        self.channel_2.clicked.connect(lambda: self.click_btn_channel(4))
        self.channel_2.clicked.connect(lambda: self.click_btn_channel(5))
        self.channel_2.clicked.connect(lambda: self.click_btn_channel(6))
        self.channel_2.clicked.connect(lambda: self.click_btn_channel(7))
        self.channel_2.clicked.connect(lambda: self.click_btn_channel(8))
        self.channels.append(self.channel_1)
        self.channels.append(self.channel_2)
        self.channels.append(self.channel_3)
        self.channels.append(self.channel_4)
        self.channels.append(self.channel_5)
        self.channels.append(self.channel_6)
        self.channels.append(self.channel_7)
        self.channels.append(self.channel_8)

        self.label_1 = QLabel('off')
        self.label_2 = QLabel('off')
        self.label_3 = QLabel('off')
        self.label_4 = QLabel('off')
        self.label_5 = QLabel('off')
        self.label_6 = QLabel('off')
        self.label_7 = QLabel('off')
        self.label_8 = QLabel('off')
        self.labels.append(self.label_1)
        self.labels.append(self.label_2)
        self.labels.append(self.label_3)
        self.labels.append(self.label_4)
        self.labels.append(self.label_5)
        self.labels.append(self.label_6)
        self.labels.append(self.label_7)
        self.labels.append(self.label_8)


        btn_all = QPushButton('All channels off')
        btn_all.clicked.connect(self.click_btn_all)

        btn_close = QPushButton('closeDevice')
        btn_close.clicked.connect(self.click_btn_close)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(btn_find)
        layout.addWidget(self.combo_box)
        for idx, (channel, label) in enumerate(zip(self.channels, self.labels)):
            channel.setEnabled(False)

            status_layout = QHBoxLayout()
            status_layout.addWidget(channel)
            status_layout.addWidget(label)
            layout.addLayout(status_layout)
        layout.addWidget(btn_all)
        layout.addWidget(btn_close)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)
        self.setWindowTitle('PyRelay')
        self.setMinimumSize(240,360)
        self.show()

    def click_btn_find(self):
        if self.lib:
            for dev_id in enumDevs(self.lib):
                self.combo_box.addItem(dev_id)

    def change_combo(self):
        if self.lib:
            if self.dev:
                closeDev(self.lib, self.dev)
            dev_id = self.combo_box.currentText()
            if dev_id:
                self.numch, self.dev = openDevById(dev_id, self.lib)
                self.status_label.setText('Opened')
                for idx in range(self.numch):
                    self.channels[idx].setEnabled(True)

    def click_btn_close(self):
        if self.lib and self.dev:
            closeDev(self.lib, self.dev)
            self.dev = None

            for channel in self.channels:
                channel.setEnabled(False)

            self.combo_box.clear()
            self.status_label.setText('Closed')

    def click_btn_channel(self, num=1):
        if self.lib and self.dev:
            status = toggleSwitch(self.lib, self.dev, num)
            self.labels[num-1].setText(ret[status])
            
    def click_btn_all(self):
        if self.lib and self.dev:
            self.lib.usb_relay_device_close_all_relay_channel(self.dev)
            for label in self.labels:
                label.setText('off')

if __name__ == '__main__':
   app = QApplication(sys.argv)
   main_window = MyApp()
   sys.exit(app.exec_())