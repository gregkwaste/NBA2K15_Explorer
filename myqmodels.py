from PySide.QtCore import *
from PySide.QtGui import *


from pygl_widgets import GLWidgetQ

import operator
import sys
from nba2k15commonvars import *


class ModelPanel(QDialog):

    def __init__(self):
        super(ModelPanel, self).__init__()

        self.mode = 0
        self.status = True
        self.resize(300, 100)
        self.setWindowTitle('Model Panel')
        main_layout = QVBoxLayout()

        hor_layout = QHBoxLayout()

        lab = QLabel()
        lab.setText('Select Model Mode')
        hor_layout.addWidget(lab)
        main_layout.addLayout(hor_layout)

        but_group = QButtonGroup()
        hor_layout = QVBoxLayout()

        but = QRadioButton()
        but.setText('Stadium Models')
        self.stadium_but = but

        but_group.addButton(but)
        hor_layout.addWidget(but)

        but = QRadioButton()
        but.setText('Rest Models')
        self.rest_but = but

        but_group.addButton(but)
        hor_layout.addWidget(but)

        main_layout.addLayout(hor_layout)

        hor_layout = QHBoxLayout()
        but = QPushButton()
        but.setText('Import')
        but.clicked.connect(self.changeMode)
        hor_layout.addWidget(but)

        but = QPushButton()
        but.setText('Cancel')
        but.clicked.connect(self.quit)
        hor_layout.addWidget(but)

        main_layout.addLayout(hor_layout)
        self.setLayout(main_layout)

    def changeMode(self):
        if self.stadium_but.isChecked():
            self.mode = 0
        else:
            self.mode = 1
        self.close()

    def quit(self):
        self.status = False
        self.close()


class ImportPanel(QDialog):
    img_type = ['DXT1', 'DXT3', 'DXT5', 'RGBA', 'DXT5_NM']
    nvidia_opts = ['-dxt1a', '-dxt3', '-dxt5', '-u8888', '-n5x5']
    mipMaps = [str(i + 1) for i in range(13)]

    def __init__(self):
        super(ImportPanel, self).__init__()
        self.CurrentImageType = self.nvidia_opts[0]
        self.CurrentMipmap = self.mipMaps[11]
        self.swizzleFlag = True
        self.ImportStatus = False
        self.initUI()

    def initUI(self):

        self.resize(250, 150)
        self.setWindowTitle('Texture Import Panel')
        main_layout = QVBoxLayout()

        sub_layout = QHBoxLayout()
        lab = QLabel()
        lab.setText('Texture Type')
        but = QComboBox()
        but.addItems(self.img_type)
        but.currentIndexChanged.connect(self.setImageType)
        sub_layout.addWidget(lab)
        sub_layout.addWidget(but)

        main_layout.addLayout(sub_layout)

        sub_layout = QHBoxLayout()
        lab = QLabel()
        lab.setText('Mipmaps')
        but = QComboBox()
        but.addItems(self.mipMaps)
        but.currentIndexChanged.connect(self.setMipmap)
        sub_layout.addWidget(lab)
        sub_layout.addWidget(but)

        main_layout.addLayout(sub_layout)

        sub_layout = QHBoxLayout()
        but = QCheckBox()
        but.setText('Swizzle')
        but.setChecked(True)
        but.stateChanged.connect(self.setSwizzleFlag)

        sub_layout.addWidget(but)
        main_layout.addLayout(sub_layout)

        sub_layout = QHBoxLayout()
        but = QPushButton()
        but.setText('Import')
        but.clicked.connect(self.imported_image)

        sub_layout.addWidget(but)
        main_layout.addLayout(sub_layout)

        self.setLayout(main_layout)

    def imported_image(self):
        self.ImportStatus = True
        self.hide()

    def setImageType(self, index):
        self.CurrentImageType = self.nvidia_opts[index]

    def setMipmap(self, index):
        self.CurrentMipmap = self.mipMaps[index]

    def setSwizzleFlag(self):
        self.swizzleFlag = not self.swizzleFlag


class AboutDialog(QWidget):

    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)
        self.setWindowTitle("About")
        self.setFixedSize(500, 200)
        layout = QVBoxLayout()
        # main label
        lab = QLabel()
        lab.setAlignment(Qt.AlignCenter)
        lab.setText(
            "<P><b><FONT COLOR='#000000' FONT SIZE = 5>NBA 2K15 Explorer v0.28</b></P></br>")
        layout.addWidget(lab)
        lab = QLabel()
        lab.setAlignment(Qt.AlignCenter)
        lab.setText(
            "<P><b><FONT COLOR='#000000' FONT SIZE = 2>Coded by: gregkwaste</b></P></br>")
        layout.addWidget(lab)

        # textbox
        tex = QTextBrowser()
        f = open("about.html")
        tex.setHtml(f.read())
        f.close()
        tex.setOpenExternalLinks(True)
        tex.setReadOnly(True)
        layout.addWidget(tex)

        self.setLayout(layout)


class IffEditorWindow(QMainWindow):

    def __init__(self, parent=None):
        super(IffEditorWindow, self).__init__(parent)
        self.setWindowTitle("Iff Editor")

        # Window private properties
        self.archiveContents = MyTableModel([('Test', '0', 'NONE', '0'),
                                             ('Test1', '1', 'NONE', '1')],
                                            ['Name', 'Offset', 'Type', 'Size'])

        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.setSizePolicy(sizePolicy)

        centerwidget = QWidget(self)  # Define CenterWidget
        centerwidget.setSizePolicy(sizePolicy)

        mainlayout = QSplitter()  # Define Splitter
        mainlayout.setOrientation(Qt.Horizontal)

        # mainlayout=QHBoxLayout()
        self.glwidget = GLWidgetQ(self)
        self.glwidget.renderText(0.5, 0.5, "3dgamedevblog")
        mainlayout.addWidget(self.glwidget)  # Add GLWidget to the splitter

        vertlist = QSplitter()
        vertlist.setOrientation(Qt.Vertical)

        gbox = QGroupBox()
        gbox.setTitle('Archive Contents')
        vlayout = QVBoxLayout()

        tableview = QTableView(parent=gbox)
        tableview.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        tableview.horizontalHeader().setMovable(True)
        tableview.setSortingEnabled(True)
        tableview.sortByColumn(1, Qt.AscendingOrder)
        tableview.setSelectionBehavior(QAbstractItemView.SelectRows)
        tableview.setModel(self.archiveContents)

        vlayout.addWidget(tableview)
        gbox.setLayout(vlayout)

        vertlist.addWidget(gbox)

        # Text Editor
        self.text_editor = QPlainTextEdit()

        # File Explorer
        self.file_explorer_model = MyTableModel(
            [('testing',), ('testingtwo',)], ['Name'])
        self.file_explorer_view = QTableView()
        self.file_explorer_view.horizontalHeader().setResizeMode(
            QHeaderView.Stretch)
        self.file_explorer_view.setModel(self.file_explorer_model)

        # Tools Tab Widget
        gbox = QGroupBox()
        gbox.setTitle('Tools')
        tabwidget = QTabWidget()
        tabwidget.addTab(self.file_explorer_view, 'File Explorer')
        tabwidget.addTab(self.text_editor, 'Text Editor')

        vlayout = QVBoxLayout()
        vlayout.addWidget(tabwidget)
        gbox.setLayout(vlayout)

        vertlist.addWidget(gbox)

        mainlayout.addWidget(vertlist)
        self.setCentralWidget(mainlayout)
        self.resize(1276, 700)

        # Configure Menu Bar
        self.menubar = QMenuBar(self)
        self.fileMenu = QMenu('File', parent=self.menubar)

        self.fileOpenAction = QAction(self)
        self.fileOpenAction.setText('Open File')
        self.fileOpenAction.triggered.connect(self.openFile)

        self.closeWindowAction = QAction(self)
        self.closeWindowAction.setText('Close')
        self.closeWindowAction.triggered.connect(self.closeWindow)

        self.fileMenu.addAction(self.fileOpenAction)
        self.fileMenu.addAction(self.closeWindowAction)

        self.menubar.addAction(self.fileMenu.menuAction())

        self.setMenuBar(self.menubar)

    def openFile(self):
        print('Opening File')

    def closeWindow(self):
        print('Closing Window')
        self.close()


class IffPanel(QWidget):

    def __init__(self, parent=None):
        super(IffPanel, self).__init__(parent)
        self.setWindowTitle("Iff Panel")
        self.setFixedSize(800, 600)


class PreferencesWindow(QDialog):

    def __init__(self, parent=None):
        super(PreferencesWindow, self).__init__(parent)
        self.setWindowTitle("Preferences")
        try:
            key = r'SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 282350'
            reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
            key = OpenKey(reg, key)
            val, typ = QueryValueEx(key, 'InstallLocation')
            self.mainDirectory = os.path.abspath(val)
        except:
            self.mainDirectory = 'C:\\'
        self.preferences_checkFile()
        # self.pref_window.resize(500,300)

        horizontal_layout = QGridLayout(self)
        hpos = 0
        vpos = 0
        for i in range(len(archiveName_list)):
            op_name = archiveName_list[i]
            button = QCheckBox(self)
            button.setText(op_name + archiveName_discr[i])
            button.setChecked(bool_dict[settings_dict[op_name]])
            horizontal_layout.addWidget(button, hpos, vpos)
            vpos += 1
            if vpos > 8:
                hpos += 1
                vpos = 0

        horizontal_layout_2 = QHBoxLayout()
        button = QPushButton()
        button.setText("Select All")
        button.clicked.connect(self.preferences_selectAll)
        horizontal_layout_2.addWidget(button)

        button = QPushButton()
        button.setText("Select None")
        button.clicked.connect(self.preferences_selectNone)
        horizontal_layout_2.addWidget(button)

        button = QPushButton()
        button.setText("Save Settings")
        button.clicked.connect(self.preferences_saveSettings)
        horizontal_layout_2.addWidget(button)

        horizontal_layout_3 = QHBoxLayout()
        lab = QLabel()
        lab.setText("Select NBA 2K15 Directory: ")
        horizontal_layout_3.addWidget(lab)

        settingsLineEdit = QLineEdit()
        settingsLineEdit.setText(self.mainDirectory)
        settingsLineEdit.setReadOnly(True)
        horizontal_layout_3.addWidget(settingsLineEdit)

        settingsPathButton = QPushButton()
        settingsPathButton.setText("Select")
        settingsPathButton.clicked.connect(self.preferences_loadDirectory)
        horizontal_layout_3.addWidget(settingsPathButton)

        settingsLabel = QLabel()
        settingsLabel.setText("Select Archives to Load")

        settingsGroupBox = QGroupBox()
        settingsGroupBox.setLayout(horizontal_layout)
        settingsGroupBox.setTitle("Archives")

        layout = QVBoxLayout(self)
        layout.addLayout(horizontal_layout_3)

        layout.addWidget(settingsLabel)
        layout.addWidget(settingsGroupBox)
        layout.addLayout(horizontal_layout_2)

        self.setLayout(layout)
        self.pref_window_buttonGroup = settingsGroupBox
        self.pref_window_Directory = settingsLineEdit

        # Preferences Window Functions
    def preferences_checkFile(self):
        # Try parsing Settings File
        try:
            sf = open('settings.ini', 'r')
            sf.readline()
            sf.readline()
            self.mainDirectory = sf.readline().split(' : ')[-1][:-1]
            print(self.mainDirectory)
            set = sf.readlines()
            for setting in set:
                settings_dict[setting.split(' : ')[0]] = setting.split(
                    ' : ')[1][:-1]
        except:
            msgbox = QMessageBox()
            msgbox.setWindowTitle("Warning")
            msgbox.setText(
                "Settings file not found. Please set your preferences")
            msgbox.exec_()

    def preferences_selectAll(self):
        for child in self.pref_window_buttonGroup.children():
            if isinstance(child, QCheckBox):
                child.setChecked(True)

    def preferences_selectNone(self):
        for child in self.pref_window_buttonGroup.children():
            if isinstance(child, QCheckBox):
                child.setChecked(False)

    def preferences_saveSettings(self):
        f = open('settings.ini', 'w')
        f.writelines(('NBA 2K Explorer Settings File \n', 'Version 0.1 \n'))
        f.write('NBA 2K15 Path : ' + self.mainDirectory + '\n')
        for child in self.pref_window_buttonGroup.children():
            if isinstance(child, QCheckBox):
                f.write(
                    child.text().split(' ')[0] + ' : ' + str(child.isChecked()) + '\n')
        f.close()
        print('Settings Saved')

    def preferences_loadDirectory(self):
        selected_dir = QFileDialog.getExistingDirectory(
            caption="Choose Export Directory")
        self.pref_window_Directory.setText(selected_dir)
        self.mainDirectory = selected_dir


class TreeItem(object):

    def __init__(self, data, parent=None):
        self.parentItem = parent
        self.itemData = data
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.itemData)

    def data(self, column):
        try:
            return self.itemData[column]
        except IndexError:
            return None

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)

        return 0


class TreeModel(QAbstractItemModel):
    progressTrigger = Signal(int)

    def __init__(self, columns, parent=None):
        super(TreeModel, self).__init__(parent)

        self.rootItem = TreeItem(columns)
        # self.setupModelData(data, self.rootItem)

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return None

        item = index.internalPointer()

        return item.data(index.column())

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.rootItem.data(section)

        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    # load list to viewer
    def setupModelData(self, data, parent, settings):
        print('Parsing Settings')
        selected_archives = []
        for child in settings.children():
            if isinstance(child, QCheckBox):
                if child.isChecked():
                    selected_archives.append(
                        archiveName_dict[child.text().split(' ')[0]])

        print(selected_archives)
        print('Setting up data')
        step = 0
        for i in selected_archives:
            step += len(data[i][3])
        step = float(step / 100)
        prog = 0
        count = 0
        for i in selected_archives:
            entry = data[i]
            arch_parent = TreeItem((entry[0], entry[1], entry[2]), parent)
            parent.appendChild(arch_parent)
            for kid in entry[3]:
                arch_parent.appendChild(
                    TreeItem((kid[0], int(kid[1]), int(kid[2]), kid[3]), arch_parent))
                if count > step:
                    prog += 1
                    self.progressTrigger.emit(prog)
                    QCoreApplication.sendPostedEvents()
                    count = 0
                else:
                    count += 1
        self.progressTrigger.emit(100)


class MyTableView(QTableView):

    def __init__(self, parent=None):
        QTableView.__init__(self, parent=None)

    def keyPressEvent(self, event):
        '''Use the default fallback'''
        QTableView.keyPressEvent(self, event)

    def editorDestroyed(self, editor):
        print(editor)
        self.dataChanged()
    # def commitData(self,editor):
    #    print('Commiting Data')
    #    print(dir(editor))
    #    print(editor.children[0])


class MyTableModel(QAbstractTableModel):

    def __init__(self, mylist, header, *args):
        QAbstractTableModel.__init__(self, parent=None, *args)
        self.mylist = mylist
        self.header = header

    def rowCount(self, parent=None):
        return len(self.mylist)

    def columnCount(self, parent=None):
        return len(self.mylist[0])

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role == Qt.EditRole:
            return self.mylist[index.row()][index.column()]
        elif role != Qt.DisplayRole:
            return None
        return self.mylist[index.row()][index.column()]

    def setData(self, index, value, role=Qt.EditRole):
        self.mylist[index.row()][index.column()] = str(value)
        return True

    def flags(self, index):
        if index.column() == 4:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None

    def sort(self, col, order):
        """sort table by given column number col"""
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.mylist = sorted(self.mylist,
                             key=operator.itemgetter(col))
        if order == Qt.DescendingOrder:
            self.mylist.reverse()
        self.emit(SIGNAL("layoutChanged()"))

    def findlayer(self, name):
        """
        Find a layer in the model by it's name
        """
        for colId in range(self.columnCount()):
            startindex = self.index(0, colId)
            items = self.match(startindex, Qt.DisplayRole, name,
                               1, Qt.MatchExactly | Qt.MatchWrap | Qt.MatchContains)
            try:
                return items[0]
            except:
                continue
        return QModelIndex()


class SortModel(QSortFilterProxyModel):

    def __init__(self, parent=None):
        super(SortModel, self).__init__(parent)
        self.model = self.sourceModel()

    def lessThan(self, left, right):
        # print(left,right)
        leftData = self.sourceModel().data(left, self.sortRole())
        rightData = self.sourceModel().data(right, self.sortRole())

        try:
            return int(leftData) < int(rightData)
        except ValueError:
            return leftData < rightData

    def filterAcceptsRow(self, row_num, source_parent):
        ''' Overriding the parent function '''
        model = self.sourceModel()
        source_index = model.index(row_num, 0, source_parent)
        offset_index = model.index(row_num, 1, source_parent)

        if self.filterRegExp().pattern() in model.data(source_index, Qt.DisplayRole) or \
           self.filterRegExp().pattern() in str(model.data(offset_index, Qt.DisplayRole)):
            return True
        return False


# app = QApplication(sys.argv)
# form = IffEditorWindow()
# form.show()
# app.exec_()
