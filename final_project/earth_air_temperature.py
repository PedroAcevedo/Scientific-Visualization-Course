#! /usr/bin/env python
import sys
import argparse
import netCDF4 as nc
import time

import vtk

#Defining a Slider class for easy use of the API of vtkSliderRepresentation2D
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

	#Adaptative Callback for different types of variables
	def SliderCallback(self, obj, event):
		slider = obj.GetRepresentation()
		value = slider.GetValue()
		self.changeValue(value)

	#Interactor assign
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
		self.data = args.file # netCDF dataset
		self.mode = args.mode # mode of the visualization, 0: with button for reproduction or 1: with slider for control time
		self.time_of_lecture = 1.92847; # According to Paraview exploration is the first timestamp presented into the dataset
		self.max_lecture = 1.92847 + args.lectures*10**-6; #

		# Reading the netCDF dataset
		self.ncDataSet = vtk.vtkNetCDFCFReader()
		self.ncDataSet.SetFileName(self.data)
		self.ncDataSet.UpdateMetaData()
		self.ncDataSet.SetVariableArrayStatus('air', 1) #Activation of the variable to be analyzed
		self.ncDataSet.Update()

		# Assign the array air as an attribute 
		assignAttribute = vtk.vtkAssignAttribute()
		assignAttribute.SetInputConnection(self.ncDataSet.GetOutputPort())
		assignAttribute.Assign("air", "SCALARS","CELL_DATA")

		# Extract geometry of the dataset
		surfaceFilter = vtk.vtkDataSetSurfaceFilter()
		surfaceFilter.SetInputConnection(assignAttribute.GetOutputPort())

		# Setup color mapping of Kelvins scale
		color_scale = vtk.vtkColorTransferFunction()
		color_scale.SetColorSpaceToRGB()
		color_scale.AddRGBPoint(150, 4/255, 15/255, 170/255) # blue 			
		color_scale.AddRGBPoint(200, 190/255, 189/255, 189/255) # gray 			
		color_scale.AddRGBPoint(300, 179/255, 16/255, 30/255) # red

		#Color Bar
		color_bar = vtk.vtkScalarBarActor()
		color_bar.SetLookupTable(color_scale)
		color_bar.SetTitle("Temperature (ºK)")
		color_bar.SetLabelFormat("%4.0f")
		color_bar.SetPosition(0.9, 0.1)
		color_bar.SetWidth(0.1)
		color_bar.SetHeight(0.7)

		# Mapper for the air value is define
		airMapper = vtk.vtkDataSetMapper()
		airMapper.SetInputConnection(surfaceFilter.GetOutputPort())
		airMapper.SetLookupTable(color_scale)

		# Actor with colored temperature data
		self.coloredActor = vtk.vtkActor()
		self.coloredActor.SetMapper(airMapper)
		self.coloredActor.GetProperty().SetOpacity(args.opacity) 

		#Define earth sphere for texture of the satellite
		source = vtk.vtkTexturedSphereSource()
		source.SetRadius(1000) # For fit actor spheres
		source.SetThetaResolution(100)
		source.SetPhiResolution(12)
		imageDataset = vtk.vtkJPEGReader()
		imageDataset.SetFileName(self.satellite)

		texture = vtk.vtkTexture() 
		texture.SetInputConnection(imageDataset.GetOutputPort()) 

		transformTexture = vtk.vtkTransformTextureCoords() 
		transformTexture.SetInputConnection(source.GetOutputPort()) 

		mapper = vtk.vtkPolyDataMapper() 
		mapper.SetInputConnection(transformTexture.GetOutputPort()) 
		mapper.ScalarVisibilityOff()

		actor = vtk.vtkActor() 
		actor.SetMapper( mapper ) 
		actor.SetTexture( texture )

		# Render
		renderer_ = vtk.vtkRenderer()
		self.render_window = vtk.vtkRenderWindow()
		self.render_window.AddRenderer(renderer_)
		interactor = vtk.vtkRenderWindowInteractor()
		interactor.SetRenderWindow(self.render_window)

		# Add the actors to the renderer, define the background and size
		renderer_.AddActor(self.coloredActor)
		renderer_.AddActor(actor)
		renderer_.AddActor(color_bar)
		renderer_.ResetCamera()
		renderer_.SetUseDepthPeeling(1)
		renderer_.SetMaximumNumberOfPeels(10)
		renderer_.SetOcclusionRatio(0.4)
		renderer_.SetBackground(0.1, 0.2, 0.4)

		#defining modes
		if(self.mode == 0):
			#Add button
			buttonWidget = vtk.vtkButtonWidget()
			button = vtk.vtkTexturedButtonRepresentation2D()
			button.SetNumberOfStates(1)
			tex1r = vtk.vtkImageData()
			prop  = vtk.vtkTextProperty()
			prop.SetFontSize(50)
			prop.SetColor(1.0, 0.95, 0.95); 
			prop.SetBold(5)
			str2im = vtk.vtkFreeTypeStringToImage()
			str2im.RenderString(prop,'Potentials',1,tex1r)
			button.SetButtonTexture(0, tex1r)
			buttonWidget.SetInteractor(interactor)
			buttonWidget.SetRepresentation(button)
			button.SetPlaceFactor(1)
			button.PlaceWidget([0., 200, 50, 500, 50, 50])
			buttonWidget.On()
			buttonWidget.AddObserver(vtk.vtkCommand.StateChangedEvent,self.changeTime)
		else:
			#add slider
			SliderWidget = Slider(0.1,0.1, 0, args.lectures,'Time lecture',self.changeTime).SetInteractor(interactor)

		self.render_window.Render()
		self.render_window.SetSize(800, 600)
		interactor.Initialize()
		self.render_window.SetWindowName("Final project: Scientific Visualization - Pedro Acevedo & Randy Consuegra")
		interactor.Start()


	# Change timesteps of the dataset by mode
	def changeTime(self, value, e=None):
		if(self.mode == 0):
			while(self.time_of_lecture < self.max_lecture):
				self.ncDataSet.UpdateTimeStep(self.time_of_lecture*10**6)
				self.time_of_lecture += 1*10**-6
				self.ncDataSet.Update()
				self.ncDataSet.Modified()
				self.coloredActor.GetMapper().Update()
				self.render_window.Render()
		else:
			self.ncDataSet.UpdateTimeStep(self.time_of_lecture*10**6 + value*10**-3)
			self.ncDataSet.Update()
			self.ncDataSet.Modified()
			self.coloredActor.GetMapper().Update()
			self.render_window.Render()
		

if __name__ == "__main__":
	# --define argument parser and parse arguments--
	parser = argparse.ArgumentParser(
		description="Climate change visualization. Final Project")
	parser.add_argument('file')
	parser.add_argument('satellite')
	parser.add_argument('--mode', type=int, help='Control time through slider',
	metavar='int', default=1)
	parser.add_argument('--opacity', type=int, help='Opacity of the dataset',
	metavar='float', default=0.8)
	parser.add_argument('--lectures', type=int, help='Number of lectures by time',
	metavar='int', default=1000)
	args = parser.parse_args()

	Visualization(args)