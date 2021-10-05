from PyQt5.QtWidgets import QMenu, QTableView, QApplication
from PyQt5.QtGui import QCursor


class MyTable(QTableView):
    def __init__(self):
        super(MyTable, self).__init__()

    def contextMenuEvent(self, event) -> None:
        if modelList:= self.selectionModel().selection().indexes():
            try:
                data = modelList[0].sibling(modelList[0].row(),0).data()
                menu = QMenu(self)
                copyAction = menu.addAction("Copy")
                copyAction.triggered.connect(lambda : QApplication.clipboard().setText(str(data)))
                menu.popup(QCursor.pos())
            except Exception as e:
                print(e)

        return super().contextMenuEvent(event)
