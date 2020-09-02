#! /usr/bin/env python
import sys
import vtk

warp = vtk.vtkWarpScalar()

def SliderCallbackWrap(obj, event):
    slider = obj.GetRepresentation()
    value = slider.GetValue()
    warp.SetScaleFactor(value)

def SliderCallbackIso(obj, event):
	slider = obj.GetRepresentation()
	value = slider.GetValue()
    #warp.SetScaleFactor(value)

def SliderRep(x,y,min, max, title):
	SliderRepresentation = vtk.vtkSliderRepresentation2D()
	SliderRepresentation.SetMinimumValue(min)
	SliderRepresentation.SetMaximumValue(max)
	SliderRepresentation.SetValue(min)
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
	SliderRepresentation.SetLabelFormat("%3.0lf / 100")
	SliderRepresentation.SetTitleHeight(0.02)
	SliderRepresentation.SetLabelHeight(0.02)
	return SliderRepresentation

def main():

	min = 0 #ImageViewer.GetSliceMin()
	max = 100 #ImageViewer.GetSliceMax()
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

	# mapper is defined
	mapper = vtk.vtkDataSetMapper()
	mapper.SetInputConnection(warp.GetOutputPort())
	mapper.SetScalarRange(min, max)
	mapper.ScalarVisibilityOff()

	# actor that combines mapper and texture
	actor = vtk.vtkActor()
	actor.SetMapper(mapper)
	actor.SetTexture(texture)

	# Render
	renderer_ = vtk.vtkRenderer()
	render_window = vtk.vtkRenderWindow()
	render_window.AddRenderer(renderer_)
	interactor = vtk.vtkRenderWindowInteractor()
	interactor.SetRenderWindow(render_window)

	# Add the actors to the renderer, define the background and size
	renderer_.AddActor(actor)
	renderer_.ResetCamera()
	renderer_.SetBackground(1,99/255,77/255)

	render_window.SetSize(800, 600)

	# Define vtkSliderWidget
	SliderWidget = vtk.vtkSliderWidget()
	SliderWidget.SetInteractor(interactor)
	SliderWidget.SetRepresentation(SliderRep(0.1,0.1,min,max,'Scale factor'))
	SliderWidget.KeyPressActivationOff()
	SliderWidget.SetAnimationModeToAnimate()
	SliderWidget.SetEnabled(True)
	SliderWidget.AddObserver("InteractionEvent", SliderCallbackWrap)

	SliderWidget2 = vtk.vtkSliderWidget()
	SliderWidget2.SetInteractor(interactor)
	SliderWidget2.SetRepresentation(SliderRep(0.1,0.2,min,max,'Isocontours scale'))
	SliderWidget2.KeyPressActivationOff()
	SliderWidget2.SetAnimationModeToAnimate()
	SliderWidget2.SetEnabled(True)
	SliderWidget2.AddObserver("InteractionEvent", SliderCallbackIso)

	interactor.Initialize()
	render_window.Render()
	render_window.SetWindowName("Project 1: GeoVisualization - Pedro Acevedo & Randy Consuegra")
	interactor.Start()

if __name__ == '__main__':
  main()