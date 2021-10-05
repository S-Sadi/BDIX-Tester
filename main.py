import os
os.chdir(sys._MEIPASS) #this line for the pyinstaller to make onfile with data

import sys, webbrowser
from PyQt5.QtWidgets import QHeaderView, QPushButton, QWidget
from PyQt5.QtWidgets import QGridLayout, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtGui import QIcon, QStandardItem
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import QSortFilterProxyModel, Qt, pyqtSignal
from PyQt5.QtCore import QThread
from MyWidgets import MyTable
import urlTester


class MyApp(QWidget):
    __appRunning = True
    def __init__(self):
        super().__init__()
        self.resize(800,500)
        self.setWindowIcon(QIcon('Files/icon.ico'))
        self.setWindowIconText("BDIX Tester")
        self.setWindowTitle("BDIX Tester")

        self.mainLayout = QVBoxLayout(self)
        self.headLayout = QHBoxLayout()
        self.subLeftLayout = QGridLayout()
        self.subRightLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.headLayout)
        self.headLayout.addLayout(self.subLeftLayout)
        self.headLayout.addLayout(self.subRightLayout)

        self.btn = QPushButton(text="Start")
        self.btn.setMinimumHeight(100)
        self.subRightLayout.addWidget(self.btn)
        self.btn.clicked.connect(self.methodcaller)

        self.combo = QComboBox()
        self.combo.addItems(["FTP", "TV", "Torrent", "International"])
        self.subLeftLayout.addWidget(self.combo,0,0)
        
        self.co = QComboBox()
        self.co.addItems(['Socket Tester', 'Request Tester'])
        self.subLeftLayout.addWidget(self.co,0,1)

        self.proBar = QProgressBar()
        self.proBar.setMinimum(0)
        self.proBar.setMaximum(100*100)
        self.proBar.setAlignment(Qt.AlignCenter)
        self.subLeftLayout.addWidget(self.proBar,1,0,1,2)

        self.entry = QLineEdit()
        self.entry.setMinimumHeight(30)
        self.entry.setPlaceholderText("Search your link")
        self.mainLayout.addWidget(self.entry)

        self.table = MyTable()
        self.mainLayout.addWidget(self.table)

        self.model = QStandardItemModel()                               # creating model for tableView
        self.model.setHorizontalHeaderLabels(["Url", "Time"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().sectionClicked.connect(self.sorter) # when click the header

        self.filter = QSortFilterProxyModel()                           # when you search anything it will filter your
        self.filter.setSourceModel(self.model)                          # search data in runtime
        self.filter.setFilterKeyColumn(0)                               # 60-> which column you want to filter
        self.filter.setFilterCaseSensitivity(Qt.CaseInsensitive)        # caseInsensitive filter
        self.table.setModel(self.filter)
        self.table.doubleClicked.connect(self.open_browser)

        self.entry.textChanged.connect(self.filter.setFilterRegExp)     # search text in searchBox it will filter your result automaticaly

        self.ascending = False                                          # it is for ascending or descending sort the table by time
        # self.entry.returnPressed.connect(self.adder)

        # self.model.dataChanged.connect(self.sorter)                     # every time when item appen in the table it make sort the data by function

    def sorter(self, event):        
        if event.real == 1:
            if self.ascending:
                self.table.sortByColumn(1,Qt.SortOrder.DescendingOrder)
                self.ascending = False
            else:
                self.table.sortByColumn(1, Qt.SortOrder.AscendingOrder)
                self.ascending = True
        elif event.real == 0:
            if self.ascending:
                self.table.sortByColumn(0, Qt.SortOrder.AscendingOrder)
                self.ascending = False
            else:
                self.table.sortByColumn(0, Qt.SortOrder.DescendingOrder)
                self.ascending = True

    
    def open_browser(self, event):
        webbrowser.WindowsDefault().open_new(self.model.index(event.row(), 0).data())
        

    def adder(self, tpl):
        url = QStandardItem(str(tpl[0]))
        url.setEditable(False)
        time = QStandardItem(str(tpl[1]))
        time.setEditable(False)
        LAST_ROW_INDEX = self.model.rowCount()
        self.model.setItem(LAST_ROW_INDEX,0, url)
        self.model.setItem(LAST_ROW_INDEX,1, time)

    def methodcaller(self):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(["Url", "Time"])
        thread = ThreadClass(parent=self, threaded_func=self.combo.currentText(), tester_index=self.co.currentIndex())
        thread.start()
        thread.any_signal.connect(self.adder)
        thread.progress_signal.connect(self.progress_updater)


    def progress_updater(self, value):
        v = self.proBar.value()+value
        if v>10000:
            v = 10000
        if value == 0:
            self.proBar.setValue(0)
            return
        self.proBar.setValue(v)
        self.proBar.setFormat("%.02f %%"%(v/100))

class ThreadClass(QThread):
    '''
    It Handel MultiThread and Working with same
    variable(res_url) in two thread
    '''
    any_signal = pyqtSignal(tuple)      # any_signal connect with a function and pass the function argument is tuple (very very useful)
    progress_signal = pyqtSignal(int)   # progress_signal connect with a progress_updater function it supply the value of the progressbar

    def __init__(self, threaded_func:str,tester_index:int,parent=None):
        super(ThreadClass,self).__init__(parent)
        self.is_running = True
        self.threaded_func = threaded_func
        self.tester = getattr(urlTester,"req_tester") if tester_index else getattr(urlTester,"sock_tester")

    def run(self):                     # thread start call this method
        self.progress_signal.emit(0)
        getattr(self,self.threaded_func)()

    def TV(self):
        with open("Files/tv_servers", 'r') as rf:
            lines = list(rf.readlines())
            line_count = len(lines)
            step_size = round(100/line_count*100) # it is for progress bar increment
            for line in lines:
                url = line.strip()
                res_url = self.tester(url,2)
                if res_url:
                    self.any_signal.emit(res_url)       # passing the argument to the other theard function

                self.progress_signal.emit(int(step_size))

    def FTP(self):
        with open("Files/ftp_servers", 'r') as rf:
            lines = rf.readlines()
            line_count = len(lines)
            step_size = round(100/line_count*100) # it is for progress bar increment
            for line in lines:
                url = line.strip()
                res_url = self.tester(url,2)
                if res_url:
                    self.any_signal.emit(res_url)       # passing the argument to the other theard function

                self.progress_signal.emit(step_size)

    def International(self):
        with open("Files/international_servers", 'r') as rf:
            lines = rf.readlines()
            line_count = len(lines)
            step_size = round(100/line_count*100) # it is for progress bar increment
            for line in lines:
                url = line.strip()
                res_url = self.tester(url,2)
                if res_url:
                    self.any_signal.emit(res_url)       # passing the argument to the other theard function

                self.progress_signal.emit(step_size)

    def Torrent(self):
        with open("Files/torrent_servers", 'r') as rf:
            lines = rf.readlines()
            line_count = len(lines)
            step_size = round(100/line_count*100) # it is for progress bar increment
            for line in lines:
                url = line.strip()
                res_url = self.tester(url,2)
                if res_url:
                    self.any_signal.emit(res_url)       # passing the argument to the other theard function

                self.progress_signal.emit(int(step_size))

    def stop(self):
        self.is_running = False
        self.terminate()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = MyApp()
    demo.show()
    sys.exit(app.exec_())
