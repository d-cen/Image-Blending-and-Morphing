#######################################################
#    Author:      Ti-Wei Chen
#    email:       chen2228@purdue.edu
#    ID:          ee364e03
#    Date:        12/2/2019
#######################################################
import os
import sys
import re
import imageio
import numpy as np
from scipy.spatial import Delaunay
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from Lab12.Morphing import *
from Lab12.MorphingGUI import *

class MorphingApp(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MorphingApp, self).__init__(parent)
        self.setupUi(self)
        self.chkShowTriangles.setEnabled(False)
        self.sliderAlpha.setEnabled(False)
        self.txtAlphaValue.setEnabled(False)
        self.txtAlphaValue.setText(str(0.0))
        self.btnLoadStartingImage.clicked.connect(self.loadStartingImage)
        self.btnLoadEndingImage.clicked.connect(self.loadEndingImage)
        self.btnBlendImage.setEnabled(False)
        self.sliderAlpha.valueChanged.connect(self.changeSlider)
        self.btnBlendImage.clicked.connect(self.morphImage)
        self.chkShowTriangles.clicked.connect(self.showTriangles)
        self.viewStartingImage.mousePressEvent = self.addStartingPoint
        self.viewEndingImage.mousePressEvent = self.addEndingPoint
        self.viewStartingImage.keyPressEvent = self.deleteStartingPoint
        self.viewEndingImage.keyPressEvent = self.deleteEndingPoint
        self.mousePressEvent = self.confirmPoint

        # Variable
        self.alpha = 0
        self.startExist = False
        self.endExist = False
        self.tmpStartList = list()
        self.tmpEndList = list()
        self.tmpStartDot = QGraphicsEllipseItem()
        self.tmpEndDot = QGraphicsEllipseItem()



    def loadStartingImage(self):
        filePath, _ = QFileDialog.getOpenFileName(self, caption='Open JPG or PNG file ...', filter='JPG files (*.jpg), PNG files (*.png)')
        if not filePath:
            return
        self.startImage(filePath)

    def startImage(self, filePath):
        self.startingPath = filePath
        img = QPixmap(filePath)
        imgScene = QGraphicsScene()
        self.viewStartingImage.setScene(imgScene)
        imgScene.addPixmap(img)
        self.viewStartingImage.fitInView(imgScene.sceneRect(), 1)
        pts = self.getCoords(filePath)
        if os.path.exists(filePath + '.txt'):
            for pt in pts:
                ellipse = QGraphicsEllipseItem(0, 0, 15, 15)
                ellipse.setPos(QPointF(QPoint(pt[0]-5, pt[1]-5)))
                ellipse.setBrush(QBrush(Qt.red))
                imgScene.addItem(ellipse)
        self.slbEnable()

    def loadEndingImage(self):
        filePath, _ = QFileDialog.getOpenFileName(self, caption='Open JPG or PNG file ...', filter='JPG files (*.jpg), PNG files (*.png)')
        if not filePath:
            return
        self.endImage(filePath)

    def endImage(self, filePath):
        self.endingPath = filePath
        img = QPixmap(filePath)
        imgScene = QGraphicsScene()
        self.viewEndingImage.setScene(imgScene)
        imgScene.addPixmap(img)
        self.viewEndingImage.fitInView(imgScene.sceneRect(), 1)
        pts = self.getCoords(filePath)
        if os.path.exists(filePath + '.txt'):
            for pt in pts:
                ellipse = QGraphicsEllipseItem(0, 0, 15, 15)
                ellipse.setPos(QPointF(QPoint(pt[0] - 5, pt[1] - 5)))
                ellipse.setBrush(QBrush(Qt.red))
                imgScene.addItem(ellipse)
        self.slbEnable()

    def getCoords(self, filePath):
        txtPath = filePath + '.txt'
        pts = []
        if os.path.exists(txtPath):
            with open(txtPath, 'r') as f:
                for line in f:
                    pt = line.split()
                    coord = [float(pt[0]), float(pt[1])]
                    pts.append(coord)
        return np.array(pts)

    def showTriangles(self):
        if self.chkShowTriangles.isChecked() == True and self.pathExist() == True:
            result = loadTriangles(self.startingPath + '.txt', self.endingPath + '.txt')
            startingTriangles = result[0]
            endingTriangles = result[1]
            for triangle in startingTriangles:
                vertices = triangle.vertices
                self.viewStartingImage.scene().addLine(vertices[0][0], vertices[0][1], vertices[1][0], vertices[1][1], QPen(Qt.red))
                self.viewStartingImage.scene().addLine(vertices[1][0], vertices[1][1], vertices[2][0], vertices[2][1], QPen(Qt.red))
                self.viewStartingImage.scene().addLine(vertices[2][0], vertices[2][1], vertices[0][0], vertices[0][1], QPen(Qt.red))
            for triangle in endingTriangles:
                vertices = triangle.vertices
                self.viewEndingImage.scene().addLine(vertices[0][0], vertices[0][1], vertices[1][0], vertices[1][1], QPen(Qt.red))
                self.viewEndingImage.scene().addLine(vertices[1][0], vertices[1][1], vertices[2][0], vertices[2][1], QPen(Qt.red))
                self.viewEndingImage.scene().addLine(vertices[2][0], vertices[2][1], vertices[0][0], vertices[0][1], QPen(Qt.red))
        if self.chkShowTriangles.isChecked() == False:
            self.viewStartingImage.scene().clear()
            self.startImage(self.startingPath)
            self.endImage(self.endingPath)

    def addStartingPoint(self, event):
        if self.startExist == True and self.endExist == True:
            self.confirmPoint(event)
        if self.btnBlendImage.isEnabled() and self.readyStart == True:
            actualPos = self.viewStartingImage.mapToScene(event.pos())
            self.tmpStartDot = QGraphicsEllipseItem(0, 0, 15, 15)
            self.tmpStartDot.setPos(actualPos)
            self.tmpStartDot.setBrush(QBrush(Qt.green))
            self.viewStartingImage.scene().addItem(self.tmpStartDot)
            self.tmpStartList.append([actualPos.x(), actualPos.y()])
            self.readyStart = False
            self.startExist = True

    def addEndingPoint(self, event):
        if self.btnBlendImage.isEnabled() and self.readyEnd == True:
            actualPos = self.viewEndingImage.mapToScene(event.pos())
            self.tmpEndDot = QGraphicsEllipseItem(0, 0, 15, 15)
            self.tmpEndDot.setPos(actualPos)
            self.tmpEndDot.setBrush(QBrush(Qt.green))
            self.viewEndingImage.scene().addItem(self.tmpEndDot)
            self.tmpEndList.append([actualPos.x(), actualPos.y()])
            self.readyEnd = False
            self.endExist = True

    def deleteStartingPoint(self, event):
        if self.btnBlendImage.isEnabled() and self.readyStart == False:
            self.viewStartingImage.scene().removeItem(self.tmpStartDot)
            self.tmpStartList.pop()
            self.readyStart = True
            self.startExist = False

    def deleteEndingPoint(self, event):
        if self.btnBlendImage.isEnabled() and self.readyEnd == False:
            self.viewEndingImage.scene().removeItem(self.tmpEndDot)
            self.tmpEndList.pop()
            self.readyEnd = True
            self.endExist = False

    def confirmPoint(self, event):
        if self.startExist == True and self.endExist == True:
            self.viewStartingImage.scene().removeItem(self.tmpStartDot)
            self.viewEndingImage.scene().removeItem(self.tmpEndDot)
            self.tmpStartDot.setBrush(QBrush(Qt.blue))
            self.tmpEndDot.setBrush(QBrush(Qt.blue))
            self.viewStartingImage.scene().addItem(self.tmpStartDot)
            self.viewEndingImage.scene().addItem(self.tmpEndDot)
            self.readyStart = True
            self.readyEnd = True
            self.startExist = False
            self.endExist = False
            tmpStartPoint = np.array([self.tmpStartList[-1][0], self.tmpStartList[-1][1]], dtype=np.float64)
            tmpEndPoint = np.array([self.tmpEndList[-1][0], self.tmpEndList[-1][1]], dtype=np.float64)
            if os.path.exists(self.startingPath + '.txt') and os.path.exists(self.endingPath + '.txt'):
                with open(self.startingPath + '.txt', 'a') as f:
                    f.write('\n' + str(round(tmpStartPoint[0], 1)) + ' ' + str(round(tmpStartPoint[1], 1)))
                with open(self.endingPath + '.txt', 'a') as f:
                    f.write('\n' + str(round(tmpEndPoint[0], 1)) + ' ' + str(round(tmpEndPoint[1], 1)))
            else:
                with open(self.startingPath + '.txt', 'w') as f:
                    f.write(str(round(tmpStartPoint[0], 1)) + ' ' + str(round(tmpStartPoint[1], 1)))
                with open(self.endingPath + '.txt', 'w') as f:
                    f.write(str(round(tmpEndPoint[0], 1)) + ' ' + str(round(tmpEndPoint[1], 1)))


    def changeSlider(self):
        value = self.sliderAlpha.value()
        if value > 95:
            value = 100
        value = int(value / 5) * 5
        self.sliderAlpha.setValue(value)
        self.alpha = round(value * 0.01, 2)
        self.txtAlphaValue.setText(str(self.alpha))

    def slbEnable(self):
        if self.viewStartingImage.scene != None and self.viewEndingImage.scene() != None:
            self.chkShowTriangles.setEnabled(True)
            self.sliderAlpha.setEnabled(True)
            self.txtAlphaValue.setEnabled(True)
            self.btnBlendImage.setEnabled(True)
            self.readyStart = True
            self.readyEnd = True

    def pathExist(self):
        if os.path.exists(self.startingPath + '.txt') and os.path.exists(self.endingPath + '.txt'):
            return True
        else:
            return False

    def morphImage(self):
        if self.btnBlendImage.isEnabled():
            result = loadTriangles(self.startingPath + '.txt', self.endingPath + '.txt')
            image1 = np.array(imageio.imread(self.startingPath))
            image2 = np.array(imageio.imread(self.endingPath))
            m = Morpher(image1, result[0], image2, result[1])
            image3 = Morpher.getImageAtAlpha(m, self.alpha)
            image3 = QtGui.QImage(image3, image3.shape[1], image3.shape[0], image3.shape[1], QtGui.QImage.Format_Indexed8)
            pix = QtGui.QPixmap.fromImage(image3)
            tempScene = QGraphicsScene()
            tempScene.addPixmap(pix)
            self.blendImage.setScene(tempScene)
            self.blendImage.fitInView(tempScene.sceneRect())

if __name__ == "__main__":
    currentApp = QApplication(sys.argv)
    currentForm = MorphingApp()
    currentForm.show()
    currentApp.exec_()
