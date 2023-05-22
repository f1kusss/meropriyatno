
import sys
import os
import platform
import sqlite3

from PySide6.QtSql import QSqlDatabase, QSqlTableModel
from modules import *
from modules.ui_registration import Ui_Registration
from widgets.custom_grips import *
os.environ["QT_FONT_DPI"] = "96" # FIX Problem for High DPI and Scale above 100%

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QFrame,
    QGridLayout, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QMainWindow, QPushButton, QSizePolicy,
    QStackedWidget, QTableView, QTextEdit, QVBoxLayout,
    QWidget)
widgets = None

class MainWindow(QMainWindow):
    def __init__(self, id):
        QMainWindow.__init__(self)
        global con, curs, cur,conn, user_id,widgets
        self.user_id = id
        con = sqlite3.connect('my_database.db')
        conn = sqlite3.connect('events.db')
        cur = conn.cursor()
        curs = con.cursor()
        self.ui = ui_main.Ui_MainWindow()
        self.ui.setupUi(self)
        self.model = self.create_model()
        self.useCustomTheme = False
        self.lightThemeFile = "themes\py_dracula_light.qss"
        self.blackThemeFile = "themes\py_dracula_dark.qss"
        self.ui.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        widgets = self.ui
        widgets.helper_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        widgets.member_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        Settings.ENABLE_CUSTOM_TITLE_BAR = True
        title = "Мероприятно"
        description = "Мероприятно! Все мероприятия под рукой"
        self.setWindowTitle(title)
        widgets.titleRightInfo.setText(description)
        event_photo = QPixmap('images/icons/frame.png')
        profile_photo = QPixmap('images/icons/profile.png')
        widgets.photo.setPixmap(profile_photo)
        widgets.event_photo.setPixmap(event_photo)
        widgets.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))
        UIFunctions.uiDefinitions(self)
        widgets.btn_home.clicked.connect(self.buttonClick)
        widgets.btn_widgets.clicked.connect(self.buttonClick)
        widgets.btn_new.clicked.connect(self.buttonClick)
        widgets.btn_save.clicked.connect(self.buttonClick)
        widgets.save_profile.clicked.connect(self.buttonClick)
        widgets.btn_exit.clicked.connect(self.buttonClick)
        widgets.btn_theme.clicked.connect(self.buttonClick)
        widgets.save_event.clicked.connect(self.buttonClick)
        widgets.submit_help.clicked.connect(self.buttonClick)
        widgets.submit_mem.clicked.connect(self.buttonClick)
        info = curs.execute("select name, second_name, surname,date from users where id = ?",(self.user_id,)).fetchall()[0]
        widgets.name.setText(f"Имя: {info[0]}")
        widgets.familia.setText(f"Фамилия: {info[1]}")
        widgets.second_name.setText(f"Отчество: {info[2]}")
        widgets.date.setText(f"Дата рождения: {info[3]}")
        self.set_profile()

        def openCloseLeftBox():
            UIFunctions.toggleLeftBox(self, True)
        widgets.extraCloseColumnBtn.clicked.connect(openCloseLeftBox)
        widgets.stackedWidget.setCurrentWidget(widgets.home)
        widgets.btn_home.setStyleSheet(UIFunctions.selectMenu(widgets.btn_home.styleSheet()))

    def buttonClick(self):
        btn = self.sender()
        btnName = btn.objectName()

        if btnName == 'submit_help':
            event_id = self.get_selected_data()[0]
            prom = f"insert into id_{str(event_id)} (user_id, org) values (?,1)"
            try:
                cur.execute(prom, (self.user_id,))
                conn.commit()
            except:
                pass

        if btnName == 'submit_mem':
            event_id = self.get_selected_data()[0]
            prom = f"insert into id_{str(event_id)} (user_id, mem) values (?,1)"
            try:
                cur.execute(prom, (self.user_id,))
                conn.commit()
            except:
                pass

        if btnName == 'btn_save':
            widgets.stackedWidget.setCurrentWidget(widgets.page)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))
            tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()[1:]
            data = []
            data2 = []
            org = []
            mem = []
            for i in tables:
                print(i[0])
                promt = f"select * from {str(i[0])} where user_id = {self.user_id} and org = 1"
                promt2 = f"select * from {str(i[0])} where user_id = {self.user_id} and mem = 1"
                orgs = cur.execute(promt).fetchall()
                members = cur.execute(promt2).fetchall()
                if len(orgs) != 0:
                   data.append(i[0])
                if len(members) != 0:
                   data2.append(i[0])
            for strings in data:
                t = str(strings)[3:]
                promt_2 = f"select * from events where id = {t}"
                inf = curs.execute(promt_2).fetchone()
                org.append(inf)
            for strings in data2:
                a = str(strings)[3:]
                promt_2 = f"select * from events where id = {a}"
                inf = curs.execute(promt_2).fetchone()
                mem.append(inf)
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(["id", "Название", "Тип", 'Дата', 'Описание'])
            model2 = QStandardItemModel()
            model2.setHorizontalHeaderLabels(["id", "Название", "Тип", 'Дата', 'Описание'])
            for row, row_data in enumerate(mem):
                for column, value in enumerate(row_data):
                    item = QStandardItem(str(value))
                    model.setItem(row, column, item)
            for row, row_data in enumerate(org):
                for column, value in enumerate(row_data):
                    item = QStandardItem(str(value))
                    model2.setItem(row, column, item)
            widgets.helper_list.setModel(model2)
            widgets.member_list.setModel(model)
            widgets.helper_list.hideColumn(0)
            widgets.helper_list.hideColumn(5)
            widgets.member_list.hideColumn(0)
            widgets.member_list.hideColumn(5)

        if btnName == "save_profile":
            print('hello')
            link = widgets.telegram.text()
            soft = widgets.skills.text()
            copywriter = 0
            photograph = 0
            shorts = 0
            designer = 0
            videograph = 0
            if widgets.copywriter.isChecked():
                copywriter = 1
            if widgets.photograph.isChecked():
                photograph = 1
            if widgets.shorts.isChecked():
                shorts = 1
            if widgets.designer.isChecked():
                designer = 1
            if widgets.videograph.isChecked():
                videograph = 1

            curs.execute('update users set tg_link = ?, softskills = ?, short = ?, photo = ?, video = ?, copy = ?, design = ?'
                         'where id = ?',(link,soft,shorts,photograph,videograph,copywriter,designer,self.user_id))
            con.commit()

        if btnName == "btn_exit":
            self.close()
            window = LoginWindow()
            window.show()

        if btnName == "btn_home":
            self.set_profile()
            widgets.stackedWidget.setCurrentWidget(widgets.home)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        if btnName == "btn_widgets":
            widgets.stackedWidget.setCurrentWidget(widgets.widgets)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))
            self.model = self.create_model()
            self.ui.tableView.setModel(self.model)
            self.model.setHeaderData(1, Qt.Horizontal, "Название")
            self.model.setHeaderData(2, Qt.Horizontal, "Тип")
            self.model.setHeaderData(3, Qt.Horizontal, "Дата проведения")
            self.model.setHeaderData(4, Qt.Horizontal, "Описание")
            self.ui.tableView.hideColumn(0)
            self.ui.tableView.hideColumn(5)

        if btnName == "save_event":
            vol = 0
            vid = 0
            ph = 0
            shrt = 0
            cop = 0
            des = 0
            if widgets.vol.isChecked():
                vol = 1
            if widgets.vid.isChecked():
                vid = 1
            if widgets.ph.isChecked():
                ph = 1
            if widgets.shrt.isChecked():
                shrt = 1
            if widgets.cop.isChecked():
                cop = 1
            if widgets.des.isChecked():
                des = 1
            name_event = widgets.name_event.text()
            description = widgets.description_event.text()
            date = widgets.dateTimeEdit.text()
            if widgets.radioButton.isChecked():
                type_event = widgets.radioButton.text()
            elif widgets.radioButton_2.isChecked():
                type_event = widgets.radioButton_2.text()
            elif widgets.radioButton_3.isChecked():
                type_event = widgets.radioButton_3.text()
            elif widgets.radioButton_4.isChecked():
                type_event = widgets.radioButton_4.text()
            else:
                type_event = ''
            if ((vol != 0 or vid != 0 or shrt != 0 or cop != 0 or ph != 0 or des != 0) and name_event != '' and description != ''\
                    and date != '' and type_event != ''):
                print('hello')
                try:
                    curs.execute('insert into events (name, type, date, description, owner_id) values (?,?,?,?,?)',\
                                 (name_event,type_event,date,description,self.user_id))
                    con.commit()
                    event_id = curs.execute('select id from events where name = ? and date = ?',
                                            (name_event, date,)).fetchone()
                    prom = f"CREATE TABLE id_{str(event_id[0])}(\
                                                id      INTEGER PRIMARY KEY,\
                                                user_id INTEGER UNIQUE,\
                                                org     INTEGER DEFAULT (0),\
                                                mem     INTEGER DEFAULT (0) \
                                                );"
                    cur.execute(prom)
                    prom2 = f"insert into id_{str(event_id[0])} (user_id, org) values (?,1)"
                    try:
                        cur.execute(prom2, (self.user_id,))
                    except:
                        pass
                    conn.commit()
                except:
                    widgets.error_event.setText('Такое мероприятие уже есть')

                widgets.radioButton.setChecked(False)
                widgets.radioButton_2.setChecked(False)
                widgets.radioButton_3.setChecked(False)
                widgets.radioButton_4.setChecked(False)
                widgets.vol.setChecked(False)
                widgets.vid.setChecked(False)
                widgets.ph.setChecked(False)
                widgets.shrt.setChecked(False)
                widgets.cop.setChecked(False)
                widgets.des.setChecked(False)
                widgets.name_event.setText('')
                widgets.description_event.setText('')
            else:
                widgets.error_event.setText('Введены не все поля')

        if btnName == "btn_new":
            widgets.stackedWidget.setCurrentWidget(widgets.new_page) # SET PAGE
            UIFunctions.resetStyle(self, btnName) # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet())) # SELECT MENU

        if btnName == "btn_theme":
            print("Сменить тему")
            self.useCustomTheme = not self.useCustomTheme
            if self.useCustomTheme:
                UIFunctions.theme(self, self.lightThemeFile, True)
            else:
                UIFunctions.theme(self, self.blackThemeFile, True)
        print(f'Button "{btnName}" pressed!')

    def set_profile(self):
        widgets.telegram.setText(curs.execute('select tg_link from users where id = ?', (self.user_id,)).fetchone()[0])
        widgets.skills.setText(
            curs.execute('select softskills from users where id = ?', (self.user_id,)).fetchone()[0])
        res = curs.execute('select short,video,photo,copy,design from users where id = ?', (self.user_id,)).fetchone()
        print(res)
        if res[0] == 1:
            widgets.shorts.setChecked(True)
        if res[1] == 1:
            widgets.videograph.setChecked(True)
        if res[2] == 1:
            widgets.photograph.setChecked(True)
        if res[3] == 1:
            widgets.copywriter.setChecked(True)
        if res[4] == 1:
            widgets.designer.setChecked(True)

    def create_model(self):
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName("my_database.db")
        if not db.open():
            print("Ошибка открытия базы данных")
            return None
        model = QSqlTableModel()
        model.setTable("events")
        model.select()

        return model

    def get_selected_data(self):
        selected_row = widgets.tableView.currentIndex().row()
        if selected_row >= 0:
            data = []
            for column in range(self.create_model().columnCount()):
                value = self.create_model().data(self.create_model().index(selected_row, column), Qt.DisplayRole)
                data.append(value)
        return data

    def resizeEvent(self, event):
        UIFunctions.resize_grips(self)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()
        if event.buttons() == Qt.LeftButton:
            print('Mouse click: LEFT CLICK')
        if event.buttons() == Qt.RightButton:
            print('Mouse click: RIGHT CLICK')


class LoginWindow(QMainWindow):
    def __init__(self):
        global con, curs, user_id,widgets
        con = sqlite3.connect('my_database.db')
        curs = con.cursor()
        QMainWindow.__init__(self)
        self.ui = Ui_Registration()
        self.ui.setupUi(self)
        widgets = self.ui
        Settings.ENABLE_CUSTOM_TITLE_BAR = True
        title = "Мероприятно"
        description = "Мероприятно! Все мероприятия под рукой"
        self.setWindowTitle(title)
        widgets.titleRightInfo.setText(description)
        UIFunctions.uiDefinitions(self)
        widgets.reg_btn.clicked.connect(self.buttonClick)
        widgets.log_btn_reg.clicked.connect(self.buttonClick)
        widgets.reg_btn_reg.clicked.connect(self.buttonClick)
        widgets.login_btn.clicked.connect(self.buttonClick)
        widgets.stackedWidget.setCurrentWidget(widgets.login)

    def buttonClick(self):
        btn = self.sender()
        btnName = btn.objectName()
        if btnName == "login_btn":
            log = self.ui.login_ent.text()
            pas = self.ui.password_ent.text()
            if (log != '' and pas != ''):
                res = curs.execute('select id from users where login = ? and password = ?',(log,pas,)).fetchone()
                if (len(res) != 0):
                    self.close()
                    window = MainWindow(res[0])
                    window.show()
                else:
                    widgets.error.setText('Неправильный логин или пароль')


        if btnName == "reg_btn":
            widgets.stackedWidget.setCurrentWidget(widgets.registration)

        if btnName == "log_btn_reg":
            widgets.stackedWidget.setCurrentWidget(widgets.login)

        if btnName == "reg_btn_reg":
            name = widgets.name_edit.text()
            lastname = widgets.last_name_edit.text()
            surname = widgets.surname_edit.text()
            date = widgets.dateEdit.text()
            login = widgets.login_edit.text()
            password = widgets.password_edit.text()
            password_2 = widgets.password_edit_2.text()
            try:
                if (name != '' and date != '' and surname != '' and lastname != '' and login != '' and password != '' and password_2 != ''):
                    if (password == password_2):
                        curs.execute("insert into users (second_name,name, surname,date, login, password) values (?,?,?,?,?,?)", \
                             (lastname,name,surname,date,login,password))
                        con.commit()
                        widgets.reg_error.setText('Регистрация удалась. В своем профиле вы можете занести данные о себе')
                    else:
                        widgets.reg_error.setText('Пароли не совпадают')
                else:
                    widgets.reg_error.setText('Введены не все поля')
            except:
                widgets.reg_error.setText('Пользователь с таким логином уже есть')

        print(f'Button "{btnName}" pressed!')


    def resizeEvent(self, event):
        UIFunctions.resize_grips(self)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()
        if event.buttons() == Qt.LeftButton:
            print('Mouse click: LEFT CLICK')
        if event.buttons() == Qt.RightButton:
            print('Mouse click: RIGHT CLICK')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
