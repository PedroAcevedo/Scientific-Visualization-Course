#!/usr/bin/env python

import sys
import vtk

# Callback function for vtkSliderWidgets
def vtkSliderCallback(obj, event):
    sliderRepres1 = obj.GetRepresentation()
    value = sliderRepres1.GetValue()
    tubeMapper.SetRadius(value)

# Load bathymetry dataset
bathymetryReader = vtk.vtkXMLImageDataReader()
bathymetryReader.SetFileName(sys.argv[1])

satelliteReader = vtk.vtkJPEGReader()
satelliteReader.SetFileName(sys.argv[2])
satelliteReader.Update()

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

tubeMapper = vtk.vtkTubeFilter()
tubeMapper.SetInputConnection(contour.GetOutputPort())
tubeMapper.SetRadius(5000)

heightMapper = vtk.vtkDataSetMapper()
heightMapper.SetInputConnection(tubeMapper.GetOutputPort())
heightMapper.SetLookupTable(lut)


# Setup color mapping bar
colorBar = vtk.vtkScalarBarActor()
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
WindowRender = vtk.vtkRenderWindowInteractor()
WindowRender.SetRenderWindow(renWin)

# Add the actors to the renderer, set the background and size
ren.AddActor(textureActor)
ren.AddActor(actor)
ren.AddActor(colorBar)
ren.ResetCamera()
ren.SetBackground(0.1, 0.2, 0.4)
ren.ResetCameraClippingRange()
renWin.SetSize(800, 600)

# Add vtkSliderWidget
SliderRepr = vtk.vtkSliderRepresentation2D()
SliderWidget = vtk.vtkSliderWidget()
min = 0 #
max = 100000
SliderRepr.SetMinimumValue(min)
SliderRepr.SetMaximumValue(max)
SliderRepr.SetValue(5000)
SliderRepr.SetTitleText("Raidus value")
SliderRepr.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
SliderRepr.GetPoint1Coordinate().SetValue(0.5, 0.2)
SliderRepr.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
SliderRepr.GetPoint2Coordinate().SetValue(0.8, 0.2)
SliderRepr.SetSliderLength(0.02)
SliderRepr.SetSliderWidth(0.03)
SliderRepr.SetEndCapLength(0.01)
SliderRepr.SetEndCapWidth(0.03)
SliderRepr.SetTubeWidth(0.005)
SliderRepr.SetLabelFormat("%3.0lf")
SliderRepr.SetTitleHeight(0.02)
SliderRepr.SetLabelHeight(0.02)
SliderWidget.SetInteractor(WindowRender)
SliderWidget.SetRepresentation(SliderRepr)
SliderWidget.KeyPressActivationOff()
SliderWidget.SetAnimationModeToAnimate()
SliderWidget.SetEnabled(True)
SliderWidget.AddObserver("InteractionEvent", vtkSliderCallback)

WindowRender.Initialize()
renWin.SetWindowName("Project 2: GeoVisualization - Pedro Acevedo & Randy Consuegra")
renWin.Render()
WindowRender.Start()