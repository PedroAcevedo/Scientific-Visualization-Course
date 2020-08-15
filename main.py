# -*- coding: utf-8 -*-
"""

@author: Pedro_Acevedo and Randy Consuegra

"""

import sys
import vtk
from GUI import *
from PyQt5 import QtCore, QtGui, QtWidgets
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor    
 
class MainWindow(QtWidgets.QMainWindow, Ui_Dialog):
 
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)

        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
 
        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
 
        # Create source
        source = vtk.vtkSphereSource()
        source.SetCenter(0, 0, 0)
        source.SetRadius(5.0)
 
        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(source.GetOutputPort())
 
        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
 
        self.ren.AddActor(actor)
 
        self.ren.ResetCamera()
         
        self.show()
        self.iren.Initialize()
    
if __name__ == "__main__":
 
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
