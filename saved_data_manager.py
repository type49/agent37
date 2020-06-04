# -*- coding: utf-8 -*-
from PIL import Image
import sys, os
import configparser
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon, QPixmap, QMovie, QCursor
from PyQt5.QtCore import QEventLoop, QTimer, pyqtSlot, pyqtSignal, Qt
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QSystemTrayIcon, QMenu, QAction, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QScrollArea
from queenui import Ui_MainWindow
import random
import webbrowser
from threading import Thread
from telegram.ext import Updater, MessageHandler, Filters
from settingsui import Ui_SettingsWindow
from youtube_search import YoutubeSearch
import clipboard
import re
import requests
import time
from bs4 import BeautifulSoup as bs
import socket
import json


def network_connection_check(link):
    try:
        socket.gethostbyaddr(link)
    except socket.gaierror:
        return False
    return True

url_regex = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

class DataManagerWindow(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()
        self.background_pixmap = QPixmap(r'data\images\mindsbackground.png')

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self._old_pos = None


        with open(r'data\data\saved_data.json', encoding='utf-8') as data_file:
            self.data_text = json.load(data_file)



        self.vbox = QVBoxLayout(self)
        self.vbox.addStretch(1)
        self.vbox.setSpacing(15)

        self.button = QPushButton('restart')
        self.button.clicked.connect(self.reverse_data_foo)


        self.exit_button = QPushButton("х")
        self.exit_button.setStyleSheet('''QPushButton
                                    {font: 12pt "Montserrat Alternates";
                                    background-color: #292f32;
                                    color: #efe2cd;
                                    padding: 5;
                                    border: 1px solid #f4726e;
                                    border-radius: 10px;
                                    }
                                    QPushButton:pressed
                                    {font: 11pt "Montserrat Alternates";
                                    background-color: #323335;
                                    color: #efe2cd;
                                    padding: 5;
                                    border: 1px solid #f4726e;
                                    border-radius: 10px;
                                    }''')
        self.exit_button.clicked.connect(self.close_app)

        self.show_max_button = QPushButton("↓↓")
        self.show_max_button.setStyleSheet('''QPushButton
                                    {font: 12pt "Montserrat Alternates";
                                    background-color: #292f32;
                                    color: #efe2cd;
                                    padding: 5;
                                    border: 1px solid #f4726e;
                                    border-radius: 10px;
                                    }
                                    QPushButton:pressed
                                    {font: 11pt "Montserrat Alternates";
                                    background-color: #323335;
                                    color: #efe2cd;
                                    padding: 5;
                                    border: 1px solid #f4726e;
                                    border-radius: 10px;
                                    }''')
        self.show_max_button.clicked.connect(self.reverse_data_foo)

        self.hide_button = QPushButton("-")
        self.hide_button.setStyleSheet('''QPushButton
                                    {font: 15pt "Montserrat Alternates";
                                    background-color: #292f32;
                                    color: #efe2cd;
                                    padding: 5;
                                    border: 1px solid #f4726e;
                                    border-radius: 10px;
                                    }
                                    QPushButton:pressed
                                    {font: 11pt "Montserrat Alternates";
                                    background-color: #323335;
                                    color: #efe2cd;
                                    padding: 5;
                                    border: 1px solid #f4726e;
                                    border-radius: 10px;
                                    }''')
        self.hide_button.clicked.connect(self.showMinimized)

        self.vbox.addWidget(self.page_init())
        self.show()


    def page_init(self):

        page_widget = QtWidgets.QWidget()

        self.main_layout = QtWidgets.QVBoxLayout(page_widget)


        self.main_box = QVBoxLayout()
        self.scrollarea = QScrollArea()
        self.scrollarea.setWidgetResizable(True)
        self.area = QWidget()
        self.labels_box = QVBoxLayout()



        for data_line in self.data_text:
            if 'text' in data_line:
                data_item = data_line['text'][0]['item']
                data_time = data_line['text'][0]['time']

                text_label = QLabel(self)
                text_label.setWordWrap(True)
                text_label.adjustSize()
                text_label.setOpenExternalLinks(True)
                text_label.setContextMenuPolicy(Qt.ActionsContextMenu)
                text_label.setFixedWidth(self.background_pixmap.width() - 30)
                text_label.setStyleSheet('''
                                                                    font: 13pt "Montserrat Alternates";
                                                                    background-color: #414547;
                                                                    color: #efe2cd;
                                                                    padding: 5;
                                                                    border: 1px solid #f09ea3;
                                                                    border-radius: 10px;
                                                                        ''')
                text_label.setText(f'''
                                    <p>{data_item}&nbsp;</p>
                                    <p style="text-align: right; font-size: 10px; color: #95a68b">{data_time}</p>
                                    ''')

                copy_action = QAction('Копировать текст', self)
                copy_action.triggered.connect(lambda ch, text=data_item: self.clipboard_copy(text))
                delete_text_action = QAction('Удалить текст', self)
                delete_text_action.triggered.connect(
                    lambda ch, x_data_line=data_line: self.delete_data_foo(x_data_line, None))

                text_label.addAction(copy_action)
                text_label.addAction(QAction('---', self))
                text_label.addAction(delete_text_action)
                text_label.addAction(QAction('---', self))

                self.labels_box.addWidget(text_label)

            if 'html' in data_line:
                data_item = data_line['html'][0]['item']
                data_time = data_line['html'][0]['time']

                global html_label
                html_label = HtmlLabel('')
                html_label.setOpenExternalLinks(True)
                html_label.setWordWrap(True)
                html_label.setFixedWidth(self.background_pixmap.width() - 30)
                html_label.setStyleSheet('''
                                                                    font: 13pt "Montserrat Alternates";
                                                                    background-color: #414547;
                                                                    color: #e0b88b;
                                                                    padding: 2;
                                                                    border: 1px solid #f09ea3;
                                                                    border-radius: 10px;
                                                                        ''')
                html_label.setText(f'''
                                    <p>{data_item}</p>
                                    <p style="text-align: right; font-size: 10px; color: #95a68b">{data_time}</p>
                                    ''')

                if network_connection_check('www.google.com') is True:
                    html_thread = Thread(target=self.html_title_parser, args=(data_item, html_label, data_time))
                    html_thread.daemon = True
                    html_thread.start()

                html_label.setContextMenuPolicy(Qt.ActionsContextMenu)
                html_open_action = QAction('Перейти по ссылке', self)
                html_open_action.triggered.connect(lambda ch, url=data_item: self.html_open(url))
                html_copy_action = QAction('Скопировать ссылку', self)
                html_copy_action.triggered.connect(lambda ch, text=data_item: self.clipboard_copy(text))
                delete_html_action = QAction('Удалить ссылку', self)
                delete_html_action.triggered.connect(
                    lambda ch, item=data_line: self.delete_data_foo(item, None))

                html_label.addAction(html_open_action)
                html_label.addAction(html_copy_action)
                html_label.addAction(QAction('---', self))
                html_label.addAction(delete_html_action)
                html_label.addAction(QAction('---', self))


                self.labels_box.addWidget(html_label)

            if 'image' in data_line:
                data_item = data_line['image'][0]['item']
                data_time = data_line['image'][0]['time']

                if os.path.exists(data_item):
                    image_label = QLabel()
                    image_label.setContextMenuPolicy(Qt.ActionsContextMenu)
                    image_label.setFixedWidth(self.background_pixmap.width() - 30)
                    image_label.setStyleSheet('''
                                                                        font: 13pt "Montserrat Alternates";
                                                                        background-color: #414547;
                                                                        color: #efe2cd;
                                                                        padding: 5;
                                                                        border: 1px solid #f09ea3;
                                                                        border-radius: 10px;
                                                                            ''')
                    image_label.setText(f'''
                                        <p><img src="{data_item}" alt="" width="{self.background_pixmap.width()-60}" /></p>
                                        <p style="text-align: right; font-size: 10px; color: #95a68b">{data_time}</p>
                                        ''')
                    delete_image_action = QAction('Удалить изображение.', self)
                    delete_image_action.triggered.connect(
                        lambda ch, x_data_line=data_line: self.delete_data_foo(x_data_line, None))
                    image_label.addAction(delete_image_action)
                    self.labels_box.addWidget(image_label)
                else:
                    self.delete_data_foo(data_line, 'x_flag')

            if 'gif' in data_line:
                data_item = data_line['gif'][0]['item']
                data_time = data_line['gif'][0]['time']

                gif_label = QLabel()
                gif_label.setContextMenuPolicy(Qt.ActionsContextMenu)
                gif_label.setFixedWidth(self.background_pixmap.width() - 30)
                gif_label.setStyleSheet('''
                                                                    font: 13pt "Montserrat Alternates";
                                                                    background-color: #414547;
                                                                    color: #efe2cd;
                                                                    padding: 5;
                                                                    border: 1px solid #f09ea3;
                                                                    border-radius: 10px;
                                                                        ''')

                if os.path.exists(data_item):
                    self.gif_item = QMovie(data_item)
                    gif_label.setMovie(self.gif_item)

                    im = Image.open(data_item)
                    w, h = im.size
                    w2, h2 = self.background_pixmap.width() - 50, self.background_pixmap.height()

                    if int(w2 / h2 * 100) < int(w / h * 100):  # +++ !!!
                        w_new = w2
                        h_new = int(w2 * h / w)
                        self.gif_item.setScaledSize(QtCore.QSize(w_new, h_new))
                        self.gif_item.start()
                        self.gif_item.stop()
                        self.labels_box.addWidget(gif_label)
                    else:
                        h_new = h2
                        w_new = int(h2 * w / h)
                        self.gif_item.setScaledSize(QtCore.QSize(w_new, h_new))
                        self.gif_item.start()
                        self.gif_item.stop()
                        self.labels_box.addWidget(gif_label)

                    gif_start_action = QAction('Запустить', self)
                    gif_start_action.triggered.connect(self.gif_item.start)
                    gif_label.addAction(gif_start_action)
                    gif_stop_action = QAction('Остановить', self)
                    gif_stop_action.triggered.connect(self.gif_item.stop)
                    gif_label.addAction(gif_stop_action)
                    gif_delete_action = QAction('Удалить гифку', self)
                    gif_delete_action.triggered.connect(lambda ch, x_data_line = data_line, gif_label = gif_label: self.delete_gif_foo(x_data_line, gif_label))
                    gif_label.addAction(gif_delete_action)
                else:
                    self.delete_data_foo(data_line, 'x_flag')







        self.button_box = QHBoxLayout()
        self.button_box.addWidget(self.show_max_button)
        self.button_box.addWidget(self.hide_button)
        self.button_box.addWidget(self.exit_button)

        self.main_box.addLayout(self.button_box)

        self.area.setLayout(self.labels_box)
        self.scrollarea.setWidget(self.area)
        if self.scrollarea.viewportSizeHint().height() < self.background_pixmap.height():
            self.scrollarea.setFixedHeight(self.scrollarea.viewportSizeHint().height())
        else:
            self.scrollarea.setFixedHeight(self.background_pixmap.height())
        self.scrollarea.setStyleSheet("""
                                                QScrollBar:vertical {
                                                    width: 14px;
                                                    margin: 16px 2px 16px 2px;       
                                                    border: 1px solid #f09ea3;
                                                    border-radius: 4px;
                                                }


                                                QScrollBar::handle:vertical {
                                                    background-color: #f1c1bf;     
                                                    border: 0px solid #31363B;
                                                    min-height: 8px;
                                                    border-radius: 4px;
                                                }

                                                QScrollBar::handle:vertical:hover {
                                                    background-color: #f4726e;      
                                                    border: 0px solid #179AE0;
                                                    border-radius: 4px;
                                                    min-height: 8px;
                                                }

                                                QScrollBar::sub-line:vertical {
                                                    margin: 3px 0px 3px 0px;
                                                    border-image: url(icons/up_arrow_disabled.png);
                                                    height: 10px;
                                                    width: 10px;
                                                    subcontrol-position: top;
                                                    subcontrol-origin: margin;
                                                }

                                                QScrollBar::add-line:vertical {
                                                    margin: 3px 0px 3px 0px;
                                                    border-image: url(icons/down_arrow_disabled.png);
                                                    height: 10px;
                                                    width: 10px;
                                                    subcontrol-position: bottom;
                                                    subcontrol-origin: margin;
                                                }

                                                QScrollBar::sub-line:vertical:hover,
                                                QScrollBar::sub-line:vertical:on {
                                                    border-image: url(icons/up_arrow.png);
                                                    height: 10px;
                                                    width: 10px;
                                                    subcontrol-position: top;
                                                    subcontrol-origin: margin;
                                                }

                                                QScrollBar::add-line:vertical:hover,
                                                QScrollBar::add-line:vertical:on {
                                                    border-image: url(/icons/down_arrow.png);
                                                    height: 10px;
                                                    width: 10px;
                                                    subcontrol-position: bottom;
                                                    subcontrol-origin: margin;
                                                }

                                                QScrollBar::up-arrow:vertical,
                                                QScrollBar::down-arrow:vertical {
                                                    background: none;                   
                                                }

                                                QScrollBar::add-page:vertical,
                                                QScrollBar::sub-page:vertical {
                                                    background: none;                
                                                }
                                            """)
        self.scrollarea.setFixedWidth(self.background_pixmap.width() + 10)
        self.setStyleSheet('''
                                background-color: transparent;
                                border:none;
                                   ''')
        self.main_box.addWidget(self.scrollarea)
        self.main_layout.addLayout(self.main_box)
        return page_widget

    def clipboard_copy(self, text):
        clipboard.copy(text)


    def html_open(self, url):
        webbrowser.open_new_tab(url)

    def html_show_all_link(self, url, label):
        text1 = label.text()
        link = text1.split('p>')[1][:-2]
        text = text1.split('p>')[5][:-2]
        reg = r'[>]{1}[0-9]{4}[-]{1}[0-9]{2}[-]{1}[0-9]{2} [|]{1} [0-9]{2}[.]{1}[0-9]{2}[<]{1}'
        time = str(str(re.findall(reg, text1)).split('\'')[1]).strip('<>')

        label.setText(f'''
                        <p>{url}</p>
                        <p>---</p>
                        <p>{text}</p>
                        <p style="text-align: right; font-size: 10px; color: #95a68b">{time}</p>
                        ''')


    def html_title_parser(self, url, html_label, data_time):
        try:
            page = requests.get(url, timeout=3)
            soup = bs(page.text, "html.parser")
            news = soup.find("title")
            news = str(news).replace('<title>', '')
            news = news.replace('</title>', '').lower()
            if len(url) < 30:
                html_label.setText(f'''
                                    <p>{url}</p>
                                    <p>---</p>
                                    <p>{news}</p>
                                    <p style="text-align: right; font-size: 10px; color: #95a68b">{data_time}</p>
                                    ''')
            else:
                html_label.setText(f'''
                                    <p>{url[:31]}... </p>
                                    <p>---</p>
                                    <p>{news}</p>
                                    <p style="text-align: right; font-size: 10px; color: #95a68b">{data_time}</p>
                                    ''')
                html_label.params(url, news)
        except:
            print(f'Error connection to {url}')
            html_label.setText(url + '\n---\n' + 'Ошибка соединения.')

    def delete_data_foo(self, x_data_line, x_flag):
        print(x_data_line)
        print(123)
        if 'image' in x_data_line:
            try:
                os.remove(x_data_line['image'][0]['item'])
            except:
                print(f'Не получилось удалить изображение')

        new_data = []

        for i in self.data_text:
            if i != x_data_line:
                new_data.append(i)

        self.write_data_to_json(new_data)

        if not x_flag:
            self.update_page_foo()

    def delete_gif_foo(self, x_data_line, gif_label):
        gif_label.close()
        a = x_data_line['gif'][0]['item']
        with open('delete_items.txt', 'a') as file:
            file.write(a)

        new_data = []

        for i in self.data_text:
            if i != x_data_line:
                new_data.append(i)


    def write_data_to_json(self, data_line):
        with open(r'data\data\saved_data.json', 'w', encoding='utf-8') as data_file:
            json.dump(data_line, data_file, indent=2, ensure_ascii=False)
        self.data_text = data_line

    def reverse_data_foo(self):
        a = self.data_text
        a.reverse()
        self.write_data_to_json(a)
        self.update_page_foo()

    def update_page_foo(self):
        widget = self.vbox.takeAt(1).widget()
        widget.hide()
        w = self.page_init()
        self.vbox.insertWidget(1, w)
        w.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._old_pos = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._old_pos = None

    def mouseMoveEvent(self, event):
        if not self._old_pos:
            return
        delta = event.pos() - self._old_pos
        self.move(self.pos() + delta)

    def close_app(self):
        self.close()
        import subprocess
        program = "python gif_delete.py"
        subprocess.Popen(program)

class HtmlLabel(QLabel):
    def __init__(self, text, parent=None):
        super(HtmlLabel, self).__init__(parent)

        self.url = ''
        self.setText(text)


    def params(self, url, news):
        self.url = url
        self.news = news
        self.show_action = QAction('Показать всю ссылку.', self)
        self.show_action.triggered.connect(self.html_show_all_link_foo)
        self.addAction(self.show_action)

    def html_show_all_link_foo(self):
        self.window().html_show_all_link(self.url, self)

def move_right_bottom_corner(win):
    screen_geometry = QApplication.desktop().availableGeometry()
    screen_size = (screen_geometry.width(), screen_geometry.height())
    win_size = (win.frameSize().width(), win.frameSize().height())
    x = screen_size[0] - win_size[0]
    y = screen_size[1] - win_size[1]
    win.move(x, y)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = DataManagerWindow()
    move_right_bottom_corner(w)
    w.show()
    sys.exit(app.exec_())