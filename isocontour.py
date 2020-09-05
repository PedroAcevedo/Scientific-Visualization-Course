#!/usr/bin/env python

import sys
import vtk
from vtk import vtkScalarBarActor, vtkTextProperty

# Callback function for vtkSliderWidgets
def vtkSliderCallback1(obj, event):
    sliderRepres1 = obj.GetRepresentation()
    pos = sliderRepres1.GetValue()
    mapper.SetRadius(pos)

# Load bathymetry dataset
bathymetryReader = vtk.vtkXMLImageDataReader()
bathymetryReader.SetFileName(sys.argv[1])

satelliteReader = vtk.vtkJPEGReader()
satelliteReader.SetFileName(sys.argv[2]) # "world.topo.bathy.200408.medium.jpg"
satelliteReader.Update()  # use an object before the pipeline updates it for you

texture = vtk.vtkTexture()
texture.SetInputConnection(satelliteReader.GetOutputPort())

textureMapper = vtk.vtkDataSetMapper()
textureMapper.SetInputData(bathymetryReader.GetOutput())
textureMapper.SetScalarRange(0, 255)
textureMapper.ScalarVisibilityOff()

textureActor = vtk.vtkActor()
textureActor.SetMapper(textureMapper)
textureActor.SetTexture(texture)

geometry = vtk.vtkImageDataGeometryFilter()
geometry.SetInputConnection(bathymetryReader.GetOutputPort())


colorVar1 = -10000
colorVar2 = 8000

# Setup color mapping
lut = vtk.vtkColorTransferFunction()
lut.SetColorSpaceToRGB()
lut.AddRGBPoint(-10000, 0, 0.651, 1)
lut.AddRGBPoint(-1000, 0.91, 0.96, 1)
lut.AddRGBPoint(0, 1, 0, 0)
lut.AddRGBPoint(1000, 0.99, 1, 0.89)
lut.AddRGBPoint(8000, 1, 1, 0)


# Load bathymetry data into Geometry Filter
contour = vtk.vtkContourFilter()
contour.GenerateValues(19, -10000, 8000)
contour.SetInputConnection(geometry.GetOutputPort())

mapper = vtk.vtkTubeFilter()
mapper.SetInputConnection(contour.GetOutputPort())
mapper.SetRadius(5000)

heightMapper = vtk.vtkDataSetMapper()
heightMapper.SetInputConnection(mapper.GetOutputPort())
heightMapper.SetLookupTable(lut)


# Setup color mapping bar
colorBar = vtkScalarBarActor()
colorBar.SetLookupTable(heightMapper.GetLookupTable())
colorBar.SetTitle("Color map")
colorBar.SetNumberOfLabels(6)
colorBar.SetLabelFormat("%6.0f")
colorBar.SetPosition(0.89, 0.1)
colorBar.SetWidth(0.08)
colorBar.SetHeight(0.7)

actor = vtk.vtkActor()
actor.SetMapper(heightMapper)

# Create renderer stuff
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# Add the actors to the renderer, set the background and size
ren.AddActor(textureActor)
ren.AddActor(actor)
ren.AddActor(colorBar)
ren.ResetCamera()
ren.SetBackground(0.1, 0.2, 0.4)
ren.ResetCameraClippingRange()
renWin.SetSize(800, 600)

# Add vtkSliderWidget
SliderRepres1 = vtk.vtkSliderRepresentation2D()
min = 0 #ImageViewer.GetSliceMin()
max = 100000 #ImageViewer.GetSliceMax()
SliderRepres1.SetMinimumValue(min)
SliderRepres1.SetMaximumValue(max)
SliderRepres1.SetValue(-1000)
SliderRepres1.SetTitleText("Raidus value")
SliderRepres1.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
SliderRepres1.GetPoint1Coordinate().SetValue(0.5, 0.2)
SliderRepres1.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
SliderRepres1.GetPoint2Coordinate().SetValue(0.8, 0.2)
SliderRepres1.SetSliderLength(0.02)
SliderRepres1.SetSliderWidth(0.03)
SliderRepres1.SetEndCapLength(0.01)
SliderRepres1.SetEndCapWidth(0.03)
SliderRepres1.SetTubeWidth(0.005)
SliderRepres1.SetLabelFormat("%3.0lf")
SliderRepres1.SetTitleHeight(0.02)
SliderRepres1.SetLabelHeight(0.02)
SliderWidget1 = vtk.vtkSliderWidget()
SliderWidget1.SetInteractor(iren)
SliderWidget1.SetRepresentation(SliderRepres1)
SliderWidget1.KeyPressActivationOff()
SliderWidget1.SetAnimationModeToAnimate()
SliderWidget1.SetEnabled(True)
SliderWidget1.AddObserver("InteractionEvent", vtkSliderCallback1)

iren.Initialize()
renWin.SetWindowName("Project 2: GeoVisualization - Pedro Acevedo & Randy Consuegra")
renWin.Render()
iren.Start()