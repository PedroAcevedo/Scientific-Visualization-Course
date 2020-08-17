#! /usr/bin/env python
import sys
import vtk

warp = vtk.vtkWarpScalar()

def SliderCallback(obj, event):
    slider = obj.GetRepresentation()
    value = slider.GetValue()
    warp.SetScaleFactor(value/100)

def main():
	# Read.
	min = 0 #ImageViewer.GetSliceMin()
	max = 10000 #ImageViewer.GetSliceMax()
	if (len(sys.argv)<3):
		print ("Takes two Files")
		return None

	bathymetryDataset = vtk.vtkXMLImageDataReader()
	bathymetryDataset.SetFileName(sys.argv[1])
	bathymetryDataset.Update()
	imageDataset = vtk.vtkJPEGReader()
	imageDataset.SetFileName(sys.argv[2])

	geometry = vtk.vtkImageDataGeometryFilter()
	geometry.SetInputConnection(bathymetryDataset.GetOutputPort())
	warp.SetInputConnection(geometry.GetOutputPort())
	warp.SetScaleFactor(min)

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
	renderer_.SetBackground(0.772, 0.988, 0.847)

	render_window.SetSize(800, 600)

	# Define vtkSliderWidget
	Slider_representation = vtk.vtkSliderRepresentation2D()
	Slider_representation.SetMinimumValue(min)
	Slider_representation.SetMaximumValue(max)
	Slider_representation.SetValue(min)
	Slider_representation.SetTitleText("scale")
	Slider_representation.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
	Slider_representation.GetPoint1Coordinate().SetValue(0.1, 0.1)
	Slider_representation.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
	Slider_representation.GetPoint2Coordinate().SetValue(0.4, 0.1)
	Slider_representation.SetSliderLength(0.02)
	Slider_representation.SetSliderWidth(0.03)
	Slider_representation.SetEndCapLength(0.01)
	Slider_representation.SetEndCapWidth(0.03)
	Slider_representation.SetTubeWidth(0.005)
	Slider_representation.SetLabelFormat("%3.0lf / 10000")
	Slider_representation.SetTitleHeight(0.02)
	Slider_representation.SetLabelHeight(0.02)
	SliderWidget = vtk.vtkSliderWidget()
	SliderWidget.SetInteractor(interactor)
	SliderWidget.SetRepresentation(Slider_representation)
	SliderWidget.KeyPressActivationOff()
	SliderWidget.SetAnimationModeToAnimate()
	SliderWidget.SetEnabled(True)
	SliderWidget.AddObserver("InteractionEvent", SliderCallback)

	interactor.Initialize()
	render_window.Render()
	interactor.Start()

if __name__ == '__main__':
  main()