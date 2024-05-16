# -*- coding:utf-8 -*-

import fx
import os

from PySide2 import QtWidgets
from tools.objectIterator import getObjects
from tools.objectIterator import ObjectFinder


def getTrackerNodename():
  clipboard = QtWidgets.QApplication.clipboard()
  cbtext = clipboard.text().encode('utf-8')
  
  for line in cbtext.splitlines(): #Get name of the layer
    line = line.decode("utf-8")
    if "name" in line:
      nameofNode = str(line)
      nameofNode = nameofNode.replace("name ","").replace(" ","")
      
      return nameofNode


def gatherTrackerInfo():
  clipboard = QtWidgets.QApplication.clipboard()
  cbtext = clipboard.text().encode('utf-8')
  
  curvelist = []
  trackerData = {}
  
  for line in cbtext.splitlines(): #Get name of the layer
    line = line.decode("utf-8")
    if "{ {curve K" in line:
       curvelist.append(line)
       
       
  a = 0

  for curve in curvelist:
      a += 1
      trackerData["tracker %s"%(a)] = {}
      innercurvelist = curve.split("{curve")
      del innercurvelist[0]

      innercurvelist[1] = innercurvelist[1].replace("}","")
      xCurvelist = innercurvelist[1].split(" ") #Getting X coordinates
      del xCurvelist[0]
      del xCurvelist[-1]
      trackerData["tracker %s"%(a)]["startframe"] = xCurvelist[0].replace("x","")
      del xCurvelist[0] #Deleting the hero frame
      trackerData["tracker %s"%(a)]["x"] = xCurvelist

      innercurvelist[2] = innercurvelist[2].replace("}","")
      yCurvelist = innercurvelist[2].split(" ")
      del yCurvelist[0]
      del yCurvelist[-1]
      del yCurvelist[0] #Deleting the hero frame
      trackerData["tracker %s"%(a)]["y"] = yCurvelist


  return trackerData


def applyNukeTrackers():
    trackerData = gatherTrackerInfo()
    trackerNodename = getTrackerNodename()
    
    node = fx.activeNode()
    nodetype = node.type

    if nodetype == "RotoNode" or nodetype == "TrackerNode":
        session = node.session
        
        for tracker in trackerData:
            silTracker =  fx.Tracker("%s_%s"%(trackerNodename,tracker))
            node.property("objects").addObjects([silTracker])
            startframe = int(trackerData[tracker]["startframe"])
            xList = trackerData[tracker]["x"]
            yList = trackerData[tracker]["y"]
            position = silTracker.property("position")
            position.constant = False
        
            endframe = startframe + len(xList)
            timeRange = list(range(startframe,endframe))

            for index, value in enumerate(xList):
                pEditor = fx.PropertyEditor(position) #Have to be inside for loop to refresh position info
                time1 = timeRange[index] - int(session.startFrame)
                x = ((float(value) - (session.size[0]/2))/session.size[1])* session.pixelAspect
                y = ((session.size[1]- float(yList[index])) - (session.size[1]/2))/session.size[1]
                pEditor.setValue(fx.Point3D(x,y,0),time1)
                pEditor.execute()


            if startframe != session.startFrame:
                position = silTracker.property("position") 
                pEditor = fx.PropertyEditor(position)
                pEditor.deleteKey(0)
                pEditor.execute()

        print("Nuke Tracker Imported successfully")
    else:
        print("Please select Roto or Tracker Node.")
        


class ImportNukeTracker(fx.Action):
    """Imports Nuke Trackers from clipboard"""

    def __init__(self):
        fx.Action.__init__(self, 'EM Nuke | Import Nuke Tracker from Clipboard')
        

    def execute(self):

        fx.beginUndo("Import Nuke Tracker")
        
        try:
            applyNukeTrackers()
        except:
            print("Unable to import Nuke Trackers")
            
        fx.endUndo()

fx.addAction(ImportNukeTracker())