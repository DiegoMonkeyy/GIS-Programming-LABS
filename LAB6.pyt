# -*- coding: utf-8 -*-

import arcpy
import os
import time

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Lab6_Toolbox"
        self.alias = "Lab6_Toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [Lab6_Tool]


class Lab6_Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Lab6_Tool"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param_proj_path = arcpy.Parameter(
            displayName="ArcGIS Pro Project (.aprx)",
            name="aprx",
            datatype="DEFile",
            parameterType="Required",
            direction="Input"
        )
        param_proj_path.filter.list = ["aprx"]

        param_layer_name = arcpy.Parameter(
            displayName="Layer name (optional)",
            name="layer_name",
            datatype="GPString",
            parameterType="Optional",
            direction="Input"
        )

        param_output = arcpy.Parameter(
            displayName="Output project path (optional)",
            name="output_aprx",
            datatype="DEFile",
            parameterType="Optional",
            direction="Output"
        )

        params = [param_proj_path, param_layer_name, param_output]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        # setup the progressor
        # 3s should be enough for you to take screenshots for submission
        readTime = 3
        start = 0
        max_progress = 100
        step = 25
        arcpy.SetProgressor("step", "Initializing...", start, max_progress, step)

        # Add message to the results pane
        arcpy.AddMessage("Init tool...")

        # Accept user input from toolbox interface
        aprxFilePath = parameters[0].valueAsText
        layerName = parameters[1].valueAsText if parameters[1].valueAsText else None
        outputPath = parameters[2].valueAsText if parameters[2].valueAsText else None

        # fetch the project
        arcpy.SetProgressorPosition(start + step)
        arcpy.SetProgressorLabel("Loading project...")
        arcpy.AddMessage("Loading project...")
        time.sleep(readTime)
        project = arcpy.mp.ArcGISProject(aprxFilePath)

        # Fetch the list of layers
        layers = project.listMaps('Map')[0].listLayers()

        # Find layers step
        arcpy.SetProgressorPosition(start + step * 2)
        arcpy.SetProgressorLabel("Finding target layers...")
        arcpy.AddMessage("Finding target layers...")
        time.sleep(readTime)

        # Re-render Structures
        arcpy.SetProgressorPosition(start + step * 3)
        arcpy.SetProgressorLabel("Re-rendering Structures...")
        arcpy.AddMessage("Re-rendering Structures...")
        time.sleep(readTime)
        for layer in layers:
            if not layer.isFeatureLayer:
                continue
            if layerName and layer.name.lower() != layerName.lower():
                continue
            symbology = layer.symbology
            if hasattr(symbology, 'renderer') and layer.name == 'Structures':
                symbology.updateRenderer('UniqueValueRenderer')
                symbology.renderer.fields = ['Type']
                layer.symbology = symbology

        # Re-render Trees
        arcpy.SetProgressorPosition(start + step * 4 if start + step * 4 <= max_progress else max_progress)
        arcpy.SetProgressorLabel("Re-rendering Trees...")
        arcpy.AddMessage("Re-rendering Trees...")
        time.sleep(readTime)
        for layer in layers:
            if not layer.isFeatureLayer:
                continue
            if layerName and layer.name.lower() != layerName.lower():
                continue
            symbology = layer.symbology
            if hasattr(symbology, 'renderer') and layer.name == 'Trees':
                symbology.updateRenderer('GraduatedColorsRenderer')
                symbology.renderer.classificationField = 'Shape_Area'
                symbology.renderer.breakCount = 5
                # per template: use exact ramp name
                symbology.renderer.colorRamp = project.listColorRamps('Oranges (5 Classes)')[0]
                layer.symbology = symbology

        # Save the updated project into a new copy.
        if not outputPath:
            base, _ = os.path.splitext(aprxFilePath)
            outputPath = base + '_new.aprx'

        arcpy.SetProgressorPosition(max_progress)
        arcpy.SetProgressorLabel("Saving the project...")
        arcpy.AddMessage("Saving the project...")
        time.sleep(readTime)
        project.saveACopy(outputPath)

        return
