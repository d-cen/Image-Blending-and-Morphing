#######################################################
#    Author:      Ti-Wei Chen
#    email:       chen2228@purdue.edu
#    ID:          ee364e03
#    Date:        11/24/2019
#######################################################
import os
import imageio
import numpy as np
from PIL import Image, ImageDraw
from scipy.spatial import Delaunay
from scipy import ndimage

def loadTriangles(leftPointFilePath, rightPointFilePath):
    leftPoints = []
    leftTriangles = []
    rightPoints = []
    rightTriangles = []
    with open(leftPointFilePath, 'r') as f:
        for line in f:
            pts = line.split()
            coords = [float(pts[0]), float(pts[1])]
            leftPoints.append(coords)
    with open(rightPointFilePath, 'r') as f:
        for line in f:
            pts = line.split()
            coords = [float(pts[0]), float(pts[1])]
            rightPoints.append(coords)
    leftPoints = np.array(leftPoints)
    rightPoints = np.array(rightPoints)
    tri = Delaunay(leftPoints)
    for vertice in tri.simplices:
        leftTriangles.append(Triangle(leftPoints[vertice]))
        rightTriangles.append(Triangle(rightPoints[vertice]))
    return (leftTriangles, rightTriangles)

class Triangle:
    def __init__(self, vertices):
        if vertices.shape != (3, 2):
            raise ValueError("The vertices are not in correct dimensions.")
        elif vertices.dtype.name != 'float64':
            raise ValueError("The vertices are not of type float64.")
        self.vertices = vertices

    def getPoints(self):
        pts = []
        xpts = np.array([self.vertices[0][0], self.vertices[1][0], self.vertices[2][0]])
        ypts = np.array([self.vertices[0][1], self.vertices[1][1], self.vertices[2][1]])
        xrange = np.arange(int(np.min(xpts)), int(np.max(xpts)) + 1)
        yrange = np.arange(int(np.min(ypts)), int(np.max(ypts)) + 1)
        for x in xrange:
            for y in yrange:
                if self.checkPoint(np.float64(x), np.float64(y)) == True:
                    pts.append((x, y))
        return np.array(pts)

    def checkPoint(self, x, y):
        v1 = self.vertices[0]
        v2 = self.vertices[1]
        v3 = self.vertices[2]
        c1 = (x - v2[0]) * (v1[1] - v2[1]) - (v1[0] - v2[0]) * (y - v2[1])
        c2 = (x - v3[0]) * (v2[1] - v3[1]) - (v2[0] - v3[0]) * (y - v3[1])
        c3 = (x - v1[0]) * (v3[1] - v1[1]) - (v3[0] - v1[0]) * (y - v1[1])
        if not((c1 < 0) or (c2 < 0) or (c3 < 0)) and ((c1 > 0) or (c2 > 0) or ( c3 > 0)):
            return True
        else:
            return False

class Morpher:
    def __init__(self, leftImage, leftTriangles, rightImage, rightTriangles):
        if leftImage.dtype.name != 'uint8' or rightImage.dtype.name != 'uint8':
            raise TypeError("The given image is not type uint8.")
        for tri in leftTriangles:
            if not isinstance(tri, Triangle):
                raise TypeError("The input is not an instance of Triangle.")
        for tri in rightTriangles:
            if not isinstance(tri, Triangle):
                raise TypeError("The input is not an instance of Triangle.")
        self.leftImage = leftImage
        self.leftTriangles = leftTriangles
        self.rightImage = rightImage
        self.rightTriangles = rightTriangles

    def getImageAtAlpha(self, alpha):
        leftIMG = np.array(Image.new('L', (self.leftImage.shape[1], self.leftImage.shape[0]), "white"))
        rightIMG = np.array(Image.new('L', (self.leftImage.shape[1], self.leftImage.shape[0]), "white"))
        finalIMG = np.array(Image.new('L', (self.leftImage.shape[1], self.leftImage.shape[0]), "white"))
        for i, triangle in enumerate(self.leftTriangles):
            b = ((1 - alpha) * self.leftTriangles[i].vertices) + (alpha * self.rightTriangles[i].vertices)
            Bn = np.array([[b[0][0]], [b[0][1]], [b[1][0]], [b[1][1]], [b[2][0]], [b[2][1]]], dtype=np.float64)
            leftINV = self.findInverse(self.leftTriangles[i], Bn)
            rightINV = self.findInverse(self.rightTriangles[i], Bn)
            self.transform(leftINV, b, self.leftImage, leftIMG)
            self.transform(rightINV, b, self.rightImage, rightIMG)
        finalIMG[np.arange(self.leftImage.shape[0])] = (1 - alpha) * leftIMG[np.arange(self.leftImage.shape[0])] + alpha * rightIMG[np.arange(self.rightImage.shape[0])]
        return finalIMG

    def transform(self, matrix, b, sourceIMG, finalIMG):
        newIMG = Image.new('L', (self.leftImage.shape[1], self.leftImage.shape[0]), 0)
        ImageDraw.Draw(newIMG).polygon([(b[0][0], b[0][1]), (b[1][0], b[1][1]), (b[2][0], b[2][1])], outline=255, fill=255)
        mask = np.array(newIMG)
        nonZero = np.nonzero(mask)
        xcoords = list(nonZero[0])
        ycoords = list(nonZero[1])
        pts = matrix.dot(np.vstack((ycoords, xcoords, np.ones((len(xcoords))))))
        finalIMG[xcoords, ycoords] = ndimage.map_coordinates(sourceIMG, [pts[1], pts[0]], order=1, mode='nearest')

    def findInverse(self, triangle, Bn):
        An = np.concatenate(((self.getMatrix(triangle.vertices[0][0], triangle.vertices[0][1])), (self.getMatrix(triangle.vertices[1][0], triangle.vertices[1][1])), (self.getMatrix(triangle.vertices[2][0], triangle.vertices[2][1]))))
        h = np.linalg.solve(An, Bn)
        H = np.array([[h[0], h[1], h[2]], [h[3], h[4], h[5]], [0, 0, 1]], dtype=np.float64)
        inverse = np.linalg.inv(H)
        return inverse

    def getMatrix(self, xn, yn):
        return np.array([[xn, yn, 1, 0, 0, 0], [0, 0, 0, xn, yn, 1]], dtype=np.float64)

if __name__ == "__main__":
    pass
