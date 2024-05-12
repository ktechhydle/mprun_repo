from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
from PyQt5.Qt import *

class QDetachTabInfo:
    def __init__(self, title, widget, placeholderWidget):
        self._title = title
        self._widget = widget
        self._placeholderWidget = placeholderWidget

class QDetachTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tabInfo = []
        self.tabBar().setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabBar().customContextMenuRequested.connect(self.handleShowContextMenu)
        self.tabCloseRequested.connect(self.handleTabClosedRequested)

    def closeEvent(self, e):
        for tab_info in self._tabInfo:
            tab_info._widget.deleteLater()
        super().closeEvent(e)

    def handleShowContextMenu(self, point):
        if point.isNull():
            return
        tabIndex = self.tabBar().tabAt(point)
        menu = QMenu("Window Action", self)
        closeAction = menu.addAction('Close')
        detachAction = menu.addAction("Detach")
        reattachAction = menu.addAction("Reattach")
        w = self.widget(tabIndex)
        if w.objectName() == "QDetachTabWidgetPlaceholder":
            detachAction.setEnabled(False)
            reattachAction.setEnabled(True)
        else:
            detachAction.setEnabled(True)
            reattachAction.setEnabled(False)

        action = menu.exec_(self.mapToGlobal(point))
        if action == detachAction:
            w = self.widget(tabIndex)
            if w.objectName() == "QDetachTabWidgetPlaceholder":
                return
            placeholder = QWidget()
            placeholder.setObjectName("QDetachTabWidgetPlaceholder")
            tabinfo = QDetachTabInfo(self.tabText(tabIndex), w, placeholder)
            self._tabInfo.append(tabinfo)
            self.removeTab(tabIndex)
            self.insertTab(tabIndex, placeholder, tabinfo._title)
            w.setParent(None)
            flags = w.windowFlags() & ~Qt.WindowCloseButtonHint & ~Qt.WindowMinimizeButtonHint
            w.setWindowFlags(flags)
            w.setWindowTitle(tabinfo._title)
            w.setWindowIcon(self.windowIcon())
            w.show()
            self.setCurrentIndex(tabIndex)

        if action == reattachAction:
            w = self.widget(tabIndex)
            if w.objectName() != "QDetachTabWidgetPlaceholder":
                return
            it = self.findPlaceholderWidget(w)
            if it is None:
                return
            self.removeTab(tabIndex)
            w.deleteLater()
            self.insertTab(tabIndex, it._widget, it._title)
            self.setCurrentIndex(tabIndex)
            self._tabInfo.remove(it)

        if action == closeAction:
            if self.count() > 1:
                self.removeTab(tabIndex)

            else:
                pass

    def handleTabClosedRequested(self, tabIndex):
        w = self.widget(tabIndex)
        if w.objectName() == "QDetachTabWidgetPlaceholder":
            it = self.findPlaceholderWidget(w)
            if it is None:
                return
            self.removeTab(tabIndex)
            w.deleteLater()
            self.insertTab(tabIndex, it._widget, it._title)
            self.setCurrentIndex(tabIndex)
            self._tabInfo.remove(it)

    def findWidget(self, widget):
        for tab_info in self._tabInfo:
            if tab_info._widget == widget:
                return tab_info
        return None

    def findPlaceholderWidget(self, widget):
        for tab_info in self._tabInfo:
            if tab_info._placeholderWidget == widget:
                return tab_info
        return None
