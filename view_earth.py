#! /usr/bin/env python
import sys
import vtk

#Global wrap scalar
warp = vtk.vtkWarpScalar()
#Global tube filter
TubeMapper = vtk.vtkTubeFilter()

#  Callback function for wrap's slider
def SliderCallbackWrap(obj, event):
    slider = obj.GetRepresentation()
    value = slider.GetValue()
    warp.SetScaleFactor(value)

#  Callback function for Isocontours' slider
def SliderCallbackIso(obj, event):
	slider = obj.GetRepresentation()
	value = slider.GetValue()
	TubeMapper.SetRadius(value)
    #warp.SetScaleFactor(value)

#Define a slider on the screen
def SliderRep(x,y,min, max, title):
	SliderRepresentation = vtk.vtkSliderRepresentation2D()
	SliderRepresentation.SetMinimumValue(min)
	SliderRepresentation.SetMaximumValue(max)
	SliderRepresentation.SetValue(5000)
	SliderRepresentation.SetTitleText(title)
	SliderRepresentation.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
	SliderRepresentation.GetPoint1Coordinate().SetValue(x,y)
	SliderRepresentation.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
	SliderRepresentation.GetPoint2Coordinate().SetValue(x+0.3, y)
	SliderRepresentation.SetSliderLength(0.02)
	SliderRepresentation.SetSliderWidth(0.03)
	SliderRepresentation.SetEndCapLength(0.01)
	SliderRepresentation.SetEndCapWidth(0.03)
	SliderRepresentation.SetTubeWidth(0.005)
	SliderRepresentation.SetLabelFormat("%3.0lf /" + str(max))
	SliderRepresentation.SetTitleHeight(0.02)
	SliderRepresentation.SetLabelHeight(0.02)
	return SliderRepresentation

def main():

	minWrap = 0
	maxWrap = 100
	minTube = -10000
	maxTube = 8000

	if (len(sys.argv)<3):
		print ("Takes two Files")
		return None
	#Read files
	elevationFile = sys.argv[1]
	satelliteFile = sys.argv[2]

	bathymetryDataset = vtk.vtkXMLPolyDataReader()
	bathymetryDataset.SetFileName(elevationFile)

	bathymetryDataset.Update()
	imageDataset = vtk.vtkJPEGReader()
	imageDataset.SetFileName(satelliteFile)

	#Filter geometry of the bathymetry dataset
	warp.SetInputConnection(bathymetryDataset.GetOutputPort())
	warp.SetScaleFactor(0.5)

	# Create texture from satellite images
	texture = vtk.vtkTexture()
	texture.SetInputConnection(imageDataset.GetOutputPort())

	# Wrapmapper is defined
	WrapMapper = vtk.vtkDataSetMapper()
	WrapMapper.SetInputConnection(warp.GetOutputPort())
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
	contour.SetInputConnection(warp.GetOutputPort())

	# mapper is define
	TubeMapper.SetInputConnection(contour.GetOutputPort())
	TubeMapper.SetRadius(5000)

	# Mapper for the height value is define
	heightMapper = vtk.vtkDataSetMapper()
	heightMapper.SetInputConnection(TubeMapper.GetOutputPort())
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

	# Actor with colored Isocontours
	coloredActor = vtk.vtkActor()
	coloredActor.SetMapper(heightMapper)


	# Render
	renderer_ = vtk.vtkRenderer()
	render_window = vtk.vtkRenderWindow()
	render_window.AddRenderer(renderer_)
	interactor = vtk.vtkRenderWindowInteractor()
	interactor.SetRenderWindow(render_window)

	# Add the actors to the renderer, define the background and size
	renderer_.AddActor(coloredActor)
	renderer_.AddActor(actor)
	renderer_.AddActor(colorBar)
	renderer_.ResetCamera()
	renderer_.SetBackground(0.1, 0.2, 0.4)

	render_window.SetSize(800, 600)

	# Define vtkSliderWidget for wrap factor
	SliderWidget = vtk.vtkSliderWidget()
	SliderWidget.SetInteractor(interactor)
	SliderWidget.SetRepresentation(SliderRep(0.1,0.1,minWrap,maxWrap,'Wrap factor'))
	SliderWidget.KeyPressActivationOff()
	SliderWidget.SetAnimationModeToAnimate()
	SliderWidget.SetEnabled(True)
	SliderWidget.AddObserver("InteractionEvent", SliderCallbackWrap)

	# Define vtkSliderWidget for Isocontours factor
	SliderWidget2 = vtk.vtkSliderWidget()
	SliderWidget2.SetInteractor(interactor)
	SliderWidget2.SetRepresentation(SliderRep(0.1,0.2,0,(minTube*-10),'Isocontours factor'))
	SliderWidget2.KeyPressActivationOff()
	SliderWidget2.SetAnimationModeToAnimate()
	SliderWidget2.SetEnabled(True)
	SliderWidget2.AddObserver("InteractionEvent", SliderCallbackIso)

	interactor.Initialize()
	render_window.Render()
	render_window.SetWindowName("Project 2: GeoVisualization - Pedro Acevedo & Randy Consuegra")
	interactor.Start()

if __name__ == '__main__':
  main()