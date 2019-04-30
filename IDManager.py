import sys
import os
import xml.etree.ElementTree as et
from PySide2 import QtCore, QtGui, QtWidgets

XML_FILE = os.path.join(os.getcwd(), 'kafka_unicode.xml')


class IDData(object):
    def __init__(self, params, parent=None, children=[]):
        """個々のIDのパラメータを格納するクラス
        Args:
            params (dictionary): パラメータ名とその値
        """
        self.__parameters = params
        self.__parent = parent
        self.__children = children
    def headerNames(self):
        return list(self.__parameters.keys())
    def headersCount(self):
        return len(list(self.__parameters.keys()))
    def getValue(self, paramname):
        return self.__parameters.get(paramname)
    @property
    def parent(self):
        return self.__parent
    @parent.setter
    def parent(self, data):
        self.__parent = data
    @property
    def children(self):
        return self.__children
    def addChildren(self, data):
        self.__children.append(data)

class IdmTableItemModel(QtCore.QAbstractItemModel):
    def __init__(self, parent=None):
        super(IdmTableItemModel, self).__init__()
        self.__items = []
        self.__headers = []
    def index(self, row, column, parent=QtCore.QModelIndex()):
        return self.createIndex(row, column, None)
    def parent(self, child):
        return QtCore.QModelIndex()
    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.__items)
    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.__headers)
    def headerData(self, column, orientation, role):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return self.__headers[column]
    def data(self, index, role):
        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            return self.__items[index.row()].getValue(self.__headers[index.column()])

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid() or not 0 <= index.row() < len(self.__items):
            return False
        if role == QtCore.Qt.EditRole and value != '':
            self.__items[index.row()][self.__headers[index.column()]] = value
            self.dataChanged.emit(index, index)
            return True
        else:
            return False
    
    def addData(self, data):
        """IDDataを末尾に追加する
        
        Args:
            data (IDData): 1件のIDData
        """
        if data.headerNames() != self.__headers:
            #パラメータ数が増えた場合に対応
            tmpList = self.__headers + data.headerNames()
            newHeaders = (sorted(set(tmpList),key=tmpList.index))
            self.beginInsertColumns(QtCore.QModelIndex(), self.columnCount(), len(newHeaders) - 1)
            self.__headers = newHeaders
            self.endInsertColumns()
        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())
        self.__items.append(data)
        self.endInsertRows()

    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

    def importXml(self, xmlFile):
        """XMLファイルを読み込み、IDData型として取り込む
        Args:
            xmlFile (str): XMLファイルのフルパス
        """
        f = open(xmlFile, 'r')
        root = et.fromstringlist(f.readlines())
        parent_map = dict((c, p) for p in root.getiterator() for c in p)
        for child in root.iter('item'):
            IDParam = {'parent': parent_map[child].attrib['name'], 'name': child.attrib['name']}
            print(parent_map[child].tag, parent_map[child].attrib)
            parentName = ''
            parentNode = child.find('{}..')
            if not parentNode is None:
                parentName = parentNode.attrib('name')
            for param in child:
                print('Item:{0} ({1} : {2}), Parent: {3}'.format(child.attrib['name'],param.tag, param.attrib, parentName))
                IDParam[param.tag] = param.text
            item = IDData(IDParam)
            self.addData(item)


class IdmMainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ID Manager')
        self.setMinimumSize(QtCore.QSize(500,500))
        vlayout = QtWidgets.QVBoxLayout(self)
        
        self.tableView = QtWidgets.QTableView()
        self.tableModel = IdmTableItemModel()
        self.tableView.setModel(self.tableModel)
        vlayout.addWidget(self.tableView)

        button = QtWidgets.QPushButton('REFLESH')
        button.clicked.connect(self.updateXml)
        vlayout.addWidget(button)
    def updateXml(self):
        self.tableModel.importXml(XML_FILE)


if __name__ == "__main__":
    app = QtWidgets.QApplication()
    win = IdmMainWindow()
    win.show()
    exit(app.exec_())