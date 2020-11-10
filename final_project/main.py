#! /usr/bin/env python
import sys
import argparse

import vtk

class Slider():

	def __init__(self,x, y, min, max, title, function, value=10):

		self.SliderInstance = vtk.vtkSliderRepresentation2D()
		self.changeValue = function

		#Define the slider on screen
		self.SliderInstance.SetMinimumValue(min)
		self.SliderInstance.SetMaximumValue(max)
		self.SliderInstance.SetValue(value)
		self.SliderInstance.SetTitleText(title)
		self.SliderInstance.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
		self.SliderInstance.GetPoint1Coordinate().SetValue(x,y)
		self.SliderInstance.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
		self.SliderInstance.GetPoint2Coordinate().SetValue(x+0.3, y)
		self.SliderInstance.SetSliderLength(0.02)
		self.SliderInstance.SetSliderWidth(0.03)
		self.SliderInstance.SetEndCapLength(0.01)
		self.SliderInstance.SetEndCapWidth(0.03)
		self.SliderInstance.SetTubeWidth(0.005)
		self.SliderInstance.SetLabelFormat("%3.0lf /" + str(max))
		self.SliderInstance.SetTitleHeight(0.02)
		self.SliderInstance.SetLabelHeight(0.02)

	def SliderCallback(self, obj, event):
		slider = obj.GetRepresentation()
		value = slider.GetValue()
		self.changeValue(value)

	def SetInteractor(self, interactor):
		SliderWidget = vtk.vtkSliderWidget()
		SliderWidget.SetInteractor(interactor)
		SliderWidget.SetRepresentation(self.SliderInstance)
		SliderWidget.KeyPressActivationOff()
		SliderWidget.SetAnimationModeToAnimate()
		SliderWidget.SetEnabled(True)
		SliderWidget.AddObserver("InteractionEvent", self.SliderCallback)
		return SliderWidget

class Visualization(object):
	"""docstring for Visualization"""

	def __init__(self, args):
		self.satellite = args.satellite
		self.data = args.file
		self.wrap = vtk.vtkWarpScalar()
		self.TubeMapper = vtk.vtkTubeFilter()

		minWrap = 0
		maxWrap = 100
		minTube = -10000
		maxTube = 8000

		bathymetryDataset = vtk.vtkXMLPolyDataReader()
		bathymetryDataset.SetFileName(self.data)

		bathymetryDataset.Update()
		imageDataset = vtk.vtkJPEGReader()
		imageDataset.SetFileName(self.satellite)

		#Filter geometry of the bathymetry dataset
		self.wrap.SetInputConnection(bathymetryDataset.GetOutputPort())
		self.wrap.SetScaleFactor(0.5)

		# Create texture from satellite images
		texture = vtk.vtkTexture()
		texture.SetInputConnection(imageDataset.GetOutputPort())

		# Wrapmapper is defined
		WrapMapper = vtk.vtkDataSetMapper()
		WrapMapper.SetInputConnection(self.wrap.GetOutputPort())
		WrapMapper.SetScalarRange(minWrap, maxWrap)
		WrapMapper.ScalarVisibilityOff()

		# actor that combines mapper and texture for Wrap
		actor = vtk.vtkActor()
		actor.SetMapper(WrapMapper)
		actor.SetTexture(texture)

		# Setup color mapping
		lut = vtk.vtkColorTransferFunction()
		lut.SetColorSpaceToRGB()
		lut.AddRGBPoint(-10000, 0, 0.651, 1)
		lut.AddRGBPoint(-1000, 0.91, 0.96, 1)
		lut.AddRGBPoint(0, 1, 0, 0)
		lut.AddRGBPoint(1000, 0.99, 1, 0.89)
		lut.AddRGBPoint(8000, 1, 1, 0)

		#Defines the contour filter over wrap data
		contour = vtk.vtkContourFilter()
		contour.GenerateValues(19, minTube, maxTube)
		contour.SetInputConnection(self.wrap.GetOutputPort())

		# mapper is define
		self.TubeMapper.SetInputConnection(contour.GetOutputPort())
		self.TubeMapper.SetRadius(5000)

		# Mapper for the height value is define
		heightMapper = vtk.vtkDataSetMapper()
		heightMapper.SetInputConnection(self.TubeMapper.GetOutputPort())
		heightMapper.SetLookupTable(lut)

		# Actor with colored Isocontours
		coloredActor = vtk.vtkActor()
		coloredActor.SetMapper(heightMapper)

		# Render
		renderer_ = vtk.vtkRenderer()
		render_window = vtk.vtkRenderWindow()
		render_window.AddRenderer(renderer_)
		interactor = vtk.vtkRenderWindowInteractor()
		interactor.SetRenderWindow(render_window)

		# Add slider for parameters modfication
		SliderWidget = Slider(0.1,0.1,minWrap,maxWrap,'Wrap factor',self.wrap.SetScaleFactor).SetInteractor(interactor)
		SliderWidget2 = Slider(0.1,0.2,0,(minTube*-10),'Isocontours factor', self.TubeMapper.SetRadius, value=5000).SetInteractor(interactor)
		
		# Add the actors to the renderer, define the background and size
		renderer_.AddActor(coloredActor)
		renderer_.AddActor(actor)
		renderer_.ResetCamera()
		renderer_.SetBackground(0.1, 0.2, 0.4)

		render_window.SetSize(800, 600)

		interactor.Initialize()
		render_window.Render()
		render_window.SetWindowName("Final project: Scientific Visualization - Pedro Acevedo & Randy Consuegra")
		interactor.Start()



if __name__ == "__main__":
	# --define argument parser and parse arguments--
	parser = argparse.ArgumentParser(
		description="Climate change visualization. Final Project")
	parser.add_argument('file')
	parser.add_argument('satellite')
	args = parser.parse_args()

	Visualization(args)