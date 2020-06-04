# -*- coding: utf-8 -*-

import sys
import os
import configparser
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QEventLoop, QTimer, pyqtSlot, pyqtSignal, Qt
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QSystemTrayIcon, QMenu, QAction
from queenui import Ui_MainWindow
import random
import webbrowser
from threading import Thread
from telegram.ext import Updater, MessageHandler, Filters
from settingsui import Ui_SettingsWindow
from youtube_search import YoutubeSearch
import re
import requests
import time
import subprocess
import socket
import json
import datetime

def network_connection_check(link):
    try:
        socket.gethostbyaddr(link)
    except socket.gaierror:
        return False
    return True

config = configparser.ConfigParser()
config.read(r'data\settings.ini')

def write_data_to_json(data_line):
    try:
        data = json.load(open(r'data\data\saved_data.json', encoding='utf-8'))
    except:
        data = []

    data.append(data_line)

    with open(r'data\data\saved_data.json', 'w', encoding='utf-8') as data_file:
        json.dump(data, data_file, indent=2, ensure_ascii=False)

botsKeyWord = [
 config['BotCommands']['youtubeSearch'],
 config['BotCommands']['randomVideo'],
 config['BotCommands']['screenshot'],
 config['BotCommands']['saveText'],
 config['BotCommands']['sendText']
]

startKeyWords = [
 config['StartCommands']['ball42']
]

sysKeyWords = [
    'Выход', 'Назад'
              ]

backgroundImage = config.get("Theme", "background")

url_regex = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

PNG_SIGNS = (b'\x89PNG\r\n\x1a\n',)  # Сигнатуры png файлов
JPG_SIGNS = (b'\xff\xd8\xff',)  # Сигнатуры jpg файлов
GIF_SIGNS = (b'GIF87a', b'GIF89a')  # Сигнатуры gif файлов


keySwitcher_49 = 1  # def keyPressEvent switcher(for switch between functions)

# open answers data files for random choosing
with open(r'data\answers\start.txt') as startAnswer:
    startAnswer = startAnswer.readlines()
with open(r'data\answers\exitApp.txt') as exitApp:
    exitApp = exitApp.readlines()
with open(r'data\data\bands.txt') as bandsList:
    bandsList = bandsList.readlines()
with open(r'data\answers\ball42.txt', encoding='utf-8') as ball42:
    ball42 = ball42.readlines()


def youtube_parser(x, x2):
    """
    YouTube search request parser.
    :param x: search request
    :param x2: 'шарманка' = random search from bandsList and don't checking title
    :return: link on random video from list generated links
    """
    x = x.lower()
    b = x.split(' ')
    youtube_search_results = YoutubeSearch(x, max_results=25).to_dict()
    results = []

    for i in youtube_search_results[:]:
        results.append(i.get('id'))

    if results != [] and x2 != 'шарманка':
        for i in youtube_search_results:
            a = str(i.get('title')).lower()
            print(a)
            print(i)
            if all(x in a for x in b) is True and x2 is None:
                a = i.get('id')
                print(a)
                return a
    elif results != [] and x2 == 'шарманка':
        a = random.choice(results)
        print(a)
        return a
    elif not results:
        return


class QueenBot(Thread):

    def __init__(self):
        super().__init__()

    def run(self):
        bot_token = config["Telegram"]["token"]
        updater = Updater(token=str(bot_token))
        dispatcher = updater.dispatcher

        def text_message(bot, update):
            message_text_49 = str(update.message.text)
            print(message_text_49)
            print(len(botsKeyWord[0]))
            if message_text_49.count(botsKeyWord[3], 0, len(botsKeyWord[3])) != 0:
                with open(r'data\data\minds.txt', 'a') as saveMessage:
                    saveMessage.write(message_text_49.replace(botsKeyWord[3], '') + '@@\n@@')
                    bot.send_message(chat_id=update.message.chat_id, text='Схоронила:з')

            elif message_text_49 == botsKeyWord[1]:
                print(message_text_49)
                webbrowser.open_new_tab(youtube_parser(str(random.choice(list(bandsList))).lower(), 'шарманка'))
                bot.send_message(chat_id=update.message.chat_id, text="Надеюсь, понравится.")

            elif message_text_49.count(botsKeyWord[0], 0, len(botsKeyWord[0])) != 0:
                print(123)
                message_text_49 = message_text_49.replace(botsKeyWord[0], '').lower()
                bot.send_message(chat_id=update.message.chat_id, text="Сейчас глянем...")
                a = youtube_parser(message_text_49, None)
                if a is not None:
                    webbrowser.open_new_tab(youtube_parser(message_text_49, None))
                    bot.send_message(chat_id=update.message.chat_id, text="Гляди на здоровье.")
                else:
                    bot.send_message(chat_id=update.message.chat_id,
                                     text="Чот херню какую то задал, ничерта не могу найти.")

            elif message_text_49 == botsKeyWord[4]:
                with open(r'data\data\minds.txt') as saveMessage:
                    a = random.choice(saveMessage.read().split('@@\n@@'))
                    bot.send_message(chat_id=update.message.chat_id, text=a)

            elif message_text_49 == botsKeyWord[2]:
                preview_screen = QApplication.primaryScreen().grabWindow(0)
                path = r'data\images'
                img = "%s/%s.png" % (path, 'screenshot')
                _ = "PNG(*.png)"
                preview_screen.save(img, "png")
                QTimer.singleShot(2000, bot.send_photo(chat_id=update.message.chat_id,
                                                       photo=open(r'data\images\screenshot.png', 'rb')))
                bot.send_message(chat_id=update.message.chat_id, text='123')
                bot.send_photo(chat_id=update.message.chat_id, photo=preview_screen)

            elif message_text_49 == 'Команды':
                bot.send_message(chat_id=update.message.chat_id, text=str(botsKeyWord))

            elif message_text_49 == 'Ты тут?':
                bot.send_message(chat_id=update.message.chat_id, text='Тут я, не кипишуй. ')

        text_message_handler = MessageHandler(Filters.all, text_message)
        dispatcher.add_handler(text_message_handler)
        updater.start_polling(clean=True)


class InactiveHotKey(Thread):
    """
    Activates keyboard listener for show window after her minimized with 'esc' key.
    """
    def __init__(self):
        super().__init__()

    def run(self):
        from pynput.keyboard import Key, Listener

        def on_release(key):
            if key == Key.pause:
                w.showNormal()
                return False

        with Listener(on_release=on_release) as listener:
            listener.join()


class SettingsWin(QtWidgets.QMainWindow, QWidget):

    def __init__(self):
        with open(r'data\settings.ini', 'r') as config_file:
            self.old_config = config_file.read()
        QtWidgets.QWidget.__init__(self, parent=None)
        bot_token = config["Telegram"]["token"]

        self.ui = Ui_SettingsWindow()
        self.ui.setupUi(self)
        self.setWindowOpacity(0.8)
        self.show()
        self.ui.tokenLineEdit.setText(bot_token)
        self.ui.saveButton.clicked.connect(self.save_button)
        self.ui.cancelButton.clicked.connect(self.cancel_button)

        self.ui.themeComboBox.setCurrentText(config.get("Theme", "background"))
        self.ui.themeComboBox.activated.connect(self.set_theme_cb)
        self.ui.themeComboBox.activated.connect(self.set_theme_cb)
        self._old_pos = None

    on_theme_changed = pyqtSignal(str)

    def set_theme_cb(self):
        background_image = config.get("Theme", "background")
        self.on_theme_changed.emit(background_image)
        a = self.ui.themeComboBox.currentIndex()
        if a == 0:
            config.set("Theme", "background", "default")
            with open(r'data\settings.ini', "w") as config_file:
                config.write(config_file)
        elif a == 1:
            config.set("Theme", "background", "dark")
            with open(r'data\settings.ini', "w") as config_file:
                config.write(config_file)

    def save_button(self):
        set_token = self.ui.tokenLineEdit.text()
        config.set("Telegram", "token", set_token)
        with open(r'data\settings.ini', "w") as config_file:
            config.write(config_file)
        self.close()

    def cancel_button(self):
        with open(r'data\settings.ini', 'w') as config_file:
            config_file.write(self.old_config)
        self.close()

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


class MyWin(QtWidgets.QMainWindow, QWidget):

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setAcceptDrops(True)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.queenBrowser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.show()

        self.ui.queenBrowser.setText(str(random.choice(list(startAnswer))))

        if config["Telegram"]["enable"] == '1':
            bot_thread = QueenBot()
            bot_thread.daemon = True
            bot_thread.start()

        if config["Setup"]["tray_icon_enable"] == '1':
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(QIcon(r'data\images\main_icon.png'))
            self.tray_icon.show()
            tray_show_action = QAction("Вытащить на главную.", self)
            tray_hide_action = QAction("Заныкать в трей.", self)
            tray_exit_action = QAction("Выход", self)
            tray_show_action.triggered.connect(self.show)
            tray_hide_action.triggered.connect(self.hide)
            tray_exit_action.triggered.connect(QtWidgets.QApplication.quit)
            tray_menu = QMenu()
            tray_menu.setStyleSheet('''
                                        font: 8pt "Montserrat Alternates";
                                        background-color: #3a3d3e;
                                        color: #efe2cd;
                                        border: 1px solid #f09ea3;
                                            ''')
            tray_menu.addAction(tray_show_action)
            tray_menu.addAction(tray_hide_action)
            tray_menu.addAction(tray_exit_action)
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            mime = str(event.mimeData().text())
            if re.match(url_regex, mime) is not None:
                Thread(target=self.html_save_and_download, args=(mime, None)).start()
            else:
                Thread(target=self.html_save_and_download, args=(mime, 'text')).start()


    def keyPressEvent(self, e):
            if e.key() == QtCore.Qt.Key_Escape:
                self.hide()
                if config["Setup"]["tray_icon_enable"] == '1':
                    self.tray_icon.showMessage(
                        "Эгель UI",
                        "Залегаю на дно, шеф.",
                        QSystemTrayIcon.Information,
                        2000)
                thread2 = InactiveHotKey()
                thread2.start()
            if e.key() == QtCore.Qt.Key_Return and keySwitcher_49 == 1:
                self.SStart()
            if e.key() == QtCore.Qt.Key_Return and keySwitcher_49 == 'ball42':
                self.question42()
            if e.key() == QtCore.Qt.Key_F5:
                program = "python saved_data_manager.py"
                subprocess.Popen(program)
            if e.key() == QtCore.Qt.Key_Return and self.ui.textBrowser.text() == 'Настройки':
                self.ui.textBrowser.clear()
                self.sw = SettingsWin()
                self.sw.show()
                self.sw.on_theme_changed.connect(self.set_theme_foo)

    def SStart(self):
        startAnw = self.ui.textBrowser.text()
        if startAnw == startKeyWords[0]:
            global keySwitcher_49
            self.ui.textBrowser.clear()
            self.question42()
            keySwitcher_49 = 'ball42'
        if startAnw == sysKeyWords[0]:
            self.close_app_foo()

    def question42(self):
        self.ui.queenBrowser.setText('Задавай, чо уж.')
        a = self.ui.textBrowser.text()
        if a not in startKeyWords and a != '' and a not in sysKeyWords:
            self.ui.queenBrowser.setText(random.choice(list(ball42)))
            with open(r'data\data\questions.txt', 'a') as questions:
                questions.write( a + '\n \n')
                self.ui.textBrowser.clear()
        elif a == sysKeyWords[1]:
            self.ui.textBrowser.clear()
            global keySwitcher_49
            keySwitcher_49 = 1
            self.ui.queenBrowser.setText(str(random.choice(list(startAnswer))))
            return
        elif a == sysKeyWords[0]:
            self.close_app_foo()

    def html_save_and_download(self, mime, text_flag):

        if text_flag:
            current_time = datetime.datetime.today().strftime("%Y-%m-%d | %H.%M.%S")
            data_line = {'text': [{'item': mime, 'time': current_time}]}
            write_data_to_json(data_line)
            print(f'Записан текст {mime[:20]}')
        else:
            def image_downloader(url, format):
                current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
                img_name = os.getcwd() + r'\\Downloads\\images\\' + current_time + format
                img_link = requests.get(url)
                load = open(img_name, "wb")
                load.write(img_link.content)
                self.ui.textBrowser.setText('123')
                if config["Setup"]["tray_icon_enable"] == '1':
                    self.tray_icon.showMessage(
                        "Эгель Downloader",
                        f"Загрузка {format} завершена.",
                        QSystemTrayIcon.Information,
                        1)
                load.close()
                if format == '.gif':
                    current_time = datetime.datetime.today().strftime("%Y-%m-%d | %H.%M")
                    data_line = {'gif': [{'item' : img_name, 'time' : current_time}]}
                    write_data_to_json(data_line)
                else:
                    current_time = datetime.datetime.today().strftime("%Y-%m-%d | %H.%M")
                    data_line = {'image': [{'item' : img_name, 'time' : current_time}]}
                    write_data_to_json(data_line)
            try:
                resp = requests.get(mime, timeout=3)
                mime_content = resp.content
                if mime_content.startswith(PNG_SIGNS) or mime_content.startswith(GIF_SIGNS) or mime_content.startswith(JPG_SIGNS):
                    if mime_content.startswith(PNG_SIGNS):
                        print('Началась загрузка пнг')
                        image_downloader(mime, '.png')
                    elif mime_content.startswith(JPG_SIGNS):
                        print('Началась загрузка жпега')
                        image_downloader(mime, '.jpg')
                    elif mime_content.startswith(GIF_SIGNS):
                        print('Началась загрузка гифки')
                        image_downloader(mime, '.gif')
                else:
                    current_time = datetime.datetime.today().strftime("%Y-%m-%d | %H.%M")
                    data_line = {'html': [{'item' : mime, 'time' : current_time}]}
                    write_data_to_json(data_line)
                    print(f'Записана ссылка: {mime}')
            except:
                print('Проблемы с соединением.')

    @pyqtSlot(str)
    def set_theme_foo(self, backgroundImage):
        """
        Change theme from settings.
        """
        if backgroundImage == 'default':
            self.ui.background.setStyleSheet("image: url(data/images/background.png);")
            self.ui.textBrowser.setStyleSheet('font: 14pt "Tahoma";\nbackground-color: rgb(240, 255, 255);\ncolor: rgb(54, 63, 66);')
            self.ui.queenBrowser.setStyleSheet('font: 11pt "Tahoma";')
            self.ui.textBrowser.setGeometry(170, 383, 251, 41)
            self.ui.queenBrowser.setGeometry(200, 190, 222, 71)
        if backgroundImage == 'dark':
            self.ui.background.setStyleSheet("image: url(data/images/background2.png);")
            self.ui.textBrowser.setStyleSheet('''
                                                font: 10pt "Montserrat Alternates";
                                                background-color: #414547;
                                                color: #efe2cd;
                                                padding: 5;
                                                border: 1px solid #f09ea3;
                                                border-radius: 10px;
                                                    ''')
            self.ui.queenBrowser.setStyleSheet('''
                                                font: 10pt "Montserrat Alternates";
                                                background-color: #414547;
                                                color: #efe2cd;
                                                padding: 5;
                                                border: 1px solid #f09ea3;
                                                border-radius: 10px;
                                                    ''')
            self.ui.textBrowser.setGeometry(10, 390, 410, 33)
            self.ui.queenBrowser.setGeometry(160, 300, 250, 60)


    def close_app_foo(self):
        self.ui.textBrowser.clear()
        self.ui.queenBrowser.setText(str(random.choice(list(exitApp))))
        loop = QEventLoop()
        QTimer.singleShot(2000, loop.quit)
        loop.exec()

        if config["Setup"]["tray_icon_enable"] == '1':
            self.tray_icon.hide()

        sys.exit()


def move_right_bottom_corner(win):
    screen_geometry = QApplication.desktop().availableGeometry()
    screen_size = (screen_geometry.width(), screen_geometry.height())
    win_size = (win.frameSize().width(), win.frameSize().height())
    x = screen_size[0] - win_size[0]
    y = screen_size[1] - win_size[1]
    win.move(x, y)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MyWin()
    move_right_bottom_corner(w)
    w.show()
    sys.exit(app.exec_())
