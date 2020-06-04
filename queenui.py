from PyQt5 import QtCore, QtWidgets
import configparser


config = configparser.ConfigParser()
config.read(r'data\settings.ini')
backgroundImage = config.get("Theme", "background")


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName('Эгель UI')
        MainWindow.setMinimumSize(QtCore.QSize(424, 424))
        MainWindow.setMaximumSize(QtCore.QSize(424, 424))

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName('centralwidget')

        self.textBrowser = QtWidgets.QLineEdit(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(170, 383, 251, 41))
        self.textBrowser.setReadOnly(False)
        self.textBrowser.setObjectName('textBrowser')

        self.queenBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.queenBrowser.setGeometry(QtCore.QRect(200, 190, 222, 71))
        self.queenBrowser.setReadOnly(True)
        self.queenBrowser.setObjectName('queenBrowser')


        if backgroundImage == 'dark':
            self.textBrowser.setStyleSheet('''
                                    font: 10pt "Montserrat Alternates";
                                    background-color: #414547;
                                    color: #efe2cd;
                                    padding: 5;
                                    border: 1px solid #f09ea3;
                                    border-radius: 10px;
                                        ''')
            self.queenBrowser.setStyleSheet('''
                                    font: 10pt "Montserrat Alternates";
                                    background-color: #414547;
                                    color: #efe2cd;
                                    padding: 5;
                                    border: 1px solid #f09ea3;
                                    border-radius: 10px;
                                        ''')
            self.textBrowser.setGeometry(10, 390, 410, 33)
            self.queenBrowser.setGeometry(160, 300, 250, 60)
        elif backgroundImage == 'default':
            self.textBrowser.setStyleSheet(
                'font: 14pt "Tahoma"; background-color: rgb(240, 255, 255); color: rgb(54, 63, 66);')
            self.queenBrowser.setStyleSheet('font: 11pt "Tahoma";')
            self.textBrowser.setGeometry(170, 383, 251, 41)
            self.queenBrowser.setGeometry(200, 190, 222, 71)

        self.background = QtWidgets.QLabel(self.centralwidget)
        self.background.resize(424, 433)
        if backgroundImage == 'default':
            self.background.setStyleSheet("image: url(data/images/background.png);")
        if backgroundImage == 'dark':
            self.background.setStyleSheet("image: url(data/images/background2.png);")
        if backgroundImage == 'creep':
            self.background.setStyleSheet("image: url(data/images/background3.png);")
        if backgroundImage == 'music':
            self.background.setStyleSheet("image: url(data/images/background4.png);")

        MainWindow.setCentralWidget(self.centralwidget)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)




