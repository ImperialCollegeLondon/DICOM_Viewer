from functools import partial

from PyQt6 import QtCore
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import QWidget

from GUI.docks.DockSeries import DockSeries
from GUI.graphics import DICOMGraphicsView
from GUI.graphics.GIFExporter import GIFExporter


class GIFHandler(QWidget):
    animationToggled = pyqtSignal()

    def __init__(self, dockSeries: DockSeries, graphicsView: DICOMGraphicsView, handler):
        super().__init__(parent = graphicsView)

        self.__speed = 50

        self.dockSeries = dockSeries
        self.currentSeriesIndex = dockSeries.currentSelectedSeriesIndex
        self.graphicsView = graphicsView
        self.handler = handler
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateImage)
        self.currentSeries = None
        self.seriesSize = None
        self.dockSeriesContentChanged()
        self.currentImageIndex = 0
        self.stopped = False
        self.graphicsView.setIsAnimationOn(True)
        self.animationToggled.connect(partial(self.handler.toggleGifSlider, self.stopped))
        self.animationToggled.connect(self.handler.changeAnimateActionText)

    def dockSeriesContentChanged(self):

        if self.currentSeries == self.handler.srcList[self.currentSeriesIndex][1]:
            self.stopAnimation()
            self.startAnimation()
            return

        self.stopAnimationTimer()
        self.currentSeriesIndex = self.dockSeries.currentSelectedSeriesIndex
        self.currentSeries = self.handler.srcList[self.currentSeriesIndex][1]
        self.seriesSize = self.currentSeries.size
        self.startAnimationTimer()

    def startAnimationTimer(self):
        self.timer.start(self.__speed)

    def startAnimation(self):
        self.stopped = False
        self.graphicsView.setIsAnimationOn(True)
        self.currentImageIndex = self.dockSeries.currentPosition
        self.startAnimationTimer()
        self.animationToggled.emit()

    def stopAnimation(self):
        self.graphicsView.setIsAnimationOn(False)
        self.stopAnimationTimer()
        self.stopped = True
        self.animationToggled.emit()

    def stopAnimationTimer(self):
        self.timer.stop()

    def updateImage(self):
        if self.currentImageIndex == self.seriesSize:
            self.currentImageIndex = 0

        self.dockSeries.setSelectedItem(self.currentImageIndex)

        self.graphicsView.setImageToView(DicomContainer = self.currentSeries.getDicomFile(self.currentImageIndex),
                                         viewMode = self.handler.currentViewMode,
                                         isFirstImage = False)

        self.currentImageIndex = self.currentImageIndex + 1

    def keyPressEvent(self, qKeyEvent):
        if qKeyEvent.key() == QtCore.Qt.Key.Key_Return:
            if self.stopped is False:
                self.stopAnimation()
            else:
                self.startAnimation()

    @classmethod
    def prepareGIFExport(cls, data):
        GIFExporter.setGIFData(data)

    @property
    def speed(self):
        return self.__speed

    @speed.setter
    def speed(self, speed):
        if speed > 0:
            self.__speed = abs(speed - 201)
            self.stopAnimationTimer()
            self.startAnimationTimer()
