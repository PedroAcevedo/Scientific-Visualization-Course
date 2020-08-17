# -*- coding: utf-8 -*-
"""

@author: Pedro_Acevedo and Randy Consuegra

"""

import sys
import vtk
import argparse
from GUI import *
from PyQt5 import QtCore, QtGui, QtWidgets
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtk.util.misc import vtkGetDataRoot
VTK_DATA_ROOT = vtkGetDataRoot()

class MainWindow(QtWidgets.QMainWindow, Ui_Dialog):

    def __init__(self, files, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        # Read in an image and compute a luminance value. The image is
        # extracted as a set of polygons (vtkImageDataGeometryFilter). We then
        # will warp the plane using the scalar (luminance) values.
        elevationFile = vtk.vtkXMLImageDataReader()
        elevationFile.SetFileName("data/elevation/elevation_small.vti")
        imageFile = vtk.vtkJPEGReader()
        imageFile.SetFileName("data/satelite/world.topo.bathy.200408.medium.jpg")
        luminance = vtk.vtkImageLuminance()
        luminance.SetInputConnection(imageFile.GetOutputPort())
        geometry = vtk.vtkImageDataGeometryFilter()
        geometry.SetInputConnection(luminance.GetOutputPort())
        warp = vtk.vtkWarpScalar()
        warp.SetInputConnection(geometry.GetOutputPort())
        warp.SetScaleFactor(0.3)
        
        # Use vtkMergeFilter to combine the original image with the warped
        # geometry.
        merge = vtk.vtkMergeFilter()
        merge.SetGeometryConnection(warp.GetOutputPort())
        merge.SetScalarsConnection(imageFile.GetOutputPort())
        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputConnection(merge.GetOutputPort())
        mapper.SetScalarRange(0, 255)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)

        #self.vtkWidget.SetSize(800,600)

        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        self.ren.AddActor(actor)
        self.ren.ResetCamera()
        self.ren.GetActiveCamera().Azimuth(20)
        self.ren.GetActiveCamera().Elevation(30)
        self.ren.SetBackground(0.1, 0.2, 0.4)
        self.ren.ResetCameraClippingRange()


        self.show()
        self.iren.Initialize()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('elevation')
    parser.add_argument('image')
    args = parser.parse_args()
    print(args.elevation)
    app = QtWidgets.QApplication([])
    window = MainWindow(['2','3','4'])
    window.show()
    app.exec_()
