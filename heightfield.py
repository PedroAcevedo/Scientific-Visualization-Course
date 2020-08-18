#! /usr/bin/env python
import sys
import vtk

warp = vtk.vtkWarpScalar()

def SliderCallback(obj, event):
    slider = obj.GetRepresentation()
    value = slider.GetValue()
    warp.SetScaleFactor(value)

def main():

	min = 0 #ImageViewer.GetSliceMin()
	max = 100 #ImageViewer.GetSliceMax()
	if (len(sys.argv)<3):
		print ("Takes two Files")
		return None
	#Read files
	bathymetryDataset = vtk.vtkXMLImageDataReader()
	bathymetryDataset.SetFileName(sys.argv[1])
	bathymetryDataset.Update()
	imageDataset = vtk.vtkJPEGReader()
	imageDataset.SetFileName(sys.argv[2])

	#Filter geometry of the bathymetry dataset
	warp.SetInputConnection(bathymetryDataset.GetOutputPort())
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
	ren = vtk.vtkRenderer()
	renWin = vtk.vtkRenderWindow()
	renWin.AddRenderer(ren)
	iren = vtk.vtkRenderWindowInteractor()
	iren.SetRenderWindow(renWin)

	# Add the actors to the renderer, define the background and size
	ren.AddActor(actor)
	ren.ResetCamera()
	ren.SetBackground(1,99/255,77/255)

	renWin.SetSize(800, 600)

	# Define vtkSliderWidget
	SliderRepres = vtk.vtkSliderRepresentation2D()
	SliderRepres.SetMinimumValue(min)
	SliderRepres.SetMaximumValue(max)
	SliderRepres.SetValue(min)
	SliderRepres.SetTitleText("Scale factor")
	SliderRepres.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
	SliderRepres.GetPoint1Coordinate().SetValue(0.1, 0.1)
	SliderRepres.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
	SliderRepres.GetPoint2Coordinate().SetValue(0.4, 0.1)
	SliderRepres.SetSliderLength(0.02)
	SliderRepres.SetSliderWidth(0.03)
	SliderRepres.SetEndCapLength(0.01)
	SliderRepres.SetEndCapWidth(0.03)
	SliderRepres.SetTubeWidth(0.005)
	SliderRepres.SetLabelFormat("%3.0lf / 100")
	SliderRepres.SetTitleHeight(0.02)
	SliderRepres.SetLabelHeight(0.02)
	SliderWidget = vtk.vtkSliderWidget()
	SliderWidget.SetInteractor(iren)
	SliderWidget.SetRepresentation(SliderRepres)
	SliderWidget.KeyPressActivationOff()
	SliderWidget.SetAnimationModeToAnimate()
	SliderWidget.SetEnabled(True)
	SliderWidget.AddObserver("InteractionEvent", SliderCallback)

	iren.Initialize()
	renWin.Render()
	renWin.SetWindowName("Project 1: GeoVisualization - Pedro Acevedo & Randy Consuegra")
	iren.Start()

if __name__ == '__main__':
  main()