#! /usr/bin/env python
import sys
import argparse
import netCDF4 as nc

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
		self.wrap = vtk.vtkPolyDataMapper()

		minWrap = 1
		maxWrap = 5000
		
		self.ncDataSet = vtk.vtkNetCDFCFReader()
		self.ncDataSet.SetFileName(self.data)
		self.ncDataSet.UpdateMetaData()
		self.ncDataSet.SetVariableArrayStatus('air', 1)
		self.ncDataSet.Update()

		assignAttribute = vtk.vtkAssignAttribute()
		assignAttribute.SetInputConnection(self.ncDataSet.GetOutputPort())
		assignAttribute.Assign("air", "SCALARS","CELL_DATA")

		surfaceFilter = vtk.vtkDataSetSurfaceFilter()
		surfaceFilter.SetInputConnection(assignAttribute.GetOutputPort())

		# Setup color mapping
		color_scale = vtk.vtkColorTransferFunction()
		color_scale.SetColorSpaceToRGB()
		color_scale.AddRGBPoint(180, 255/255, 228/255, 111/255) 			
		color_scale.AddRGBPoint(250, 249/255, 168/255, 35/255) 			
		color_scale.AddRGBPoint(350, 234/255, 42/255, 3/255)


		#Color Bar
		color_bar = vtk.vtkScalarBarActor()
		#color_bar.SetOrientationToHorizontal()
		color_bar.SetLookupTable(color_scale)
		color_bar.SetTitle("Temperature scale")
		color_bar.SetLabelFormat("%4.0f")
		color_bar.SetPosition(0.9, 0.1)
		color_bar.SetWidth(0.1)
		color_bar.SetHeight(0.7)

		# #Defines the contour filter over wrap data
		# contour = vtk.vtkContourFilter()
		# contour.GenerateValues(19, minTube, maxTube)
		# contour.SetInputConnection(self.wrap.GetOutputPort())

		# # mapper is define
		# self.TubeMapper.SetInputConnection(contour.GetOutputPort())
		# self.TubeMapper.SetRadius(5000)

		# Mapper for the height value is define
		heightMapper = vtk.vtkDataSetMapper()
		heightMapper.SetInputConnection(surfaceFilter.GetOutputPort())
		heightMapper.SetLookupTable(color_scale)
		#heightMapper.ScalarVisibilityOff()
		#heightMapper.SetScalarRange(100,2500)
		#heightMapper.SetScalarModeToUsePointFieldData()
		
		# Actor with colored Isocontours
		coloredActor = vtk.vtkActor()
		coloredActor.SetMapper(heightMapper)
		coloredActor.GetProperty().SetOpacity(0.6) 
		#coloredActor.SetTexture(texture)

		source = vtk.vtkTexturedSphereSource()
		source.SetRadius(1000)
		source.SetThetaResolution(100)
		source.SetPhiResolution(12)
		imageDataset = vtk.vtkJPEGReader()
		imageDataset.SetFileName(self.satellite)

		texture = vtk.vtkTexture() 
		texture.SetInputConnection(imageDataset.GetOutputPort()) 

		transformTexture = vtk.vtkTransformTextureCoords() 
		transformTexture.SetInputConnection(source.GetOutputPort()) 
		#transformTexture.SetPosition(translate) 

		mapper = vtk.vtkPolyDataMapper() 
		mapper.SetInputConnection(transformTexture.GetOutputPort()) 
		mapper.ScalarVisibilityOff()

		actor = vtk.vtkActor() 
		actor.SetMapper( mapper ) 
		actor.SetTexture( texture ) 

		# earthSource = vtk.vtkEarthSource()
		# earthSource.SetRadius(1000)
		# earthSource.OutlineOn()
		# earthSource.Update()

		# #Create a mapper and actor
		# mapper = vtk.vtkPolyDataMapper()
		# mapper.SetInputConnection(earthSource.GetOutputPort())

		# actor = vtk.vtkActor()
		# actor.SetMapper(mapper)


		# Render
		renderer_ = vtk.vtkRenderer()
		render_window = vtk.vtkRenderWindow()
		render_window.AddRenderer(renderer_)
		interactor = vtk.vtkRenderWindowInteractor()
		interactor.SetRenderWindow(render_window)

		# Add slider for parameters modfication
		SliderWidget = Slider(0.1,0.1,minWrap,maxWrap,'Wrap factor',self.changeTime).SetInteractor(interactor)
		#SliderWidget2 = Slider(0.1,0.2,0,(minTube*-10),'Isocontours factor', self.TubeMapper.SetRadius, value=5000).SetInteractor(interactor)
		
		# Add the actors to the renderer, define the background and size
		renderer_.AddActor(coloredActor)
		renderer_.AddActor(actor)
		renderer_.AddActor(color_bar)

		#renderer_.AddActor(actor)
		renderer_.ResetCamera()
		renderer_.SetUseDepthPeeling(1)
		renderer_.SetMaximumNumberOfPeels(10)
		renderer_.SetOcclusionRatio(0.4)
		renderer_.SetBackground(0.1, 0.2, 0.4)

		render_window.SetSize(800, 600)

		interactor.Initialize()
		render_window.Render()
		render_window.SetWindowName("Final project: Scientific Visualization - Pedro Acevedo & Randy Consuegra")
		interactor.Start()


	def changeTime(self,time):
		self.ncDataSet.UpdateTimeStep(time*10**-6)
		self.ncDataSet.Update()

if __name__ == "__main__":
	# --define argument parser and parse arguments--
	parser = argparse.ArgumentParser(
		description="Climate change visualization. Final Project")
	parser.add_argument('file')
	parser.add_argument('satellite')
	args = parser.parse_args()

	Visualization(args)