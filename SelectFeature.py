# -*- coding: utf-8 -*-
"""
/***************************************************************************
 NearestFeature
                                 A QGIS plugin
 Selects the nearest feature.
                              -------------------
        begin                : 2014-10-15
        git sha              : $Format:%H$
        copyright            : (C) 2014 by Peter Wells for Lutra Consulting
        email                : info@lutraconsulting.co.uk
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.gui import *
from qgis.core import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class NearestFeatureMapTool(QgsMapTool):
    
    def __init__(self, canvas):
        
        super(QgsMapTool, self).__init__(canvas)
        self.canvas = canvas
        self.cursor = QCursor(Qt.CrossCursor)
        
    def activate(self):
        self.canvas.setCursor(self.cursor)

    def canvasReleaseEvent(self, mouseEvent):
    
        layerData = []
    
        for layer in self.canvas.layers():
        
            if layer.type() != QgsMapLayer.VectorLayer:
            # Ignorowanie warstwy kt�ra nie jest wektorem
                continue
        
            if layer.featureCount() == 0:
            # Brak obiekt�w - pomi�
                continue
        
            layer.removeSelection()
            
            # Pobiera wsp�rz�dne kursora myszki
            layerPoint = self.toLayerCoordinates( layer, mouseEvent.pos() )

            shortestDistance = float("inf")
            closestFeatureId = -1

            # Loop through all features in the layer
            for f in layer.getFeatures():
                dist = f.geometry().distance( QgsGeometry.fromPoint( layerPoint) )
                if dist < shortestDistance:
                    shortestDistance = dist
                    closestFeatureId = f.id()

            info = (layer, closestFeatureId, shortestDistance)
            layerData.append(info)
        
        if not len(layerData) > 0:
        # Looks like no vector layers were found - do nothing
            return

        # Sort the layer information by shortest distance
        layerData.sort( key=lambda element: element[2] )

        # Select the closest feature
        layerWithClosestFeature, closestFeatureId, shortestDistance = layerData[0]
        layerWithClosestFeature.select( closestFeatureId )