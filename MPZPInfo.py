# -*- coding: utf-8 -*-
"""
/***************************************************************************
 mpzp
                                 A QGIS plugin
 MPZPInfo
                              -------------------
        begin                : 2015-09-13
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Tomasz Hak
        email                : tomplamka@gmail.com
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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from datetime import *
from PyQt4.QtXml import QDomDocument
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from MPZPInfo_dialog import mpzpDialog
import os.path


class mpzp:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'mpzp_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = mpzpDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&MPZPInfo')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'mpzp')
        self.toolbar.setObjectName(u'mpzp')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('mpzp', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/mpzp/icon/search.png'
        self.add_action(
            icon_path,
            text=self.tr(u'MPZPInfo'),
            callback=self.run,
            parent=self.iface.mainWindow())
            
        #self.toolButton.toggled.connect(self.__enableTool)
        #self.iface.mapCanvas().mapToolSet.connect(self.__onToolSet)


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&MPZPInfo'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
        
        
    def __enableTool(self, active):
        self.tool.setEnabled(active)

    def __onToolSet(self, tool):
        if tool != self.tool:
            self.toolButton.setChecked(False)
        
    def szukaj(self):
        # selekcja atrybutów na podstawie zaznaczonych wartości
        self.iface.mapCanvas().setSelectionColor( QColor("yellow") )
        warstwa = self.iface.mapCanvas().currentLayer()
        
        #wartości z coboBoxów do zmiennej
        varObreb = unicode(self.dlg.obrebComboBox.currentText())
        varNumer = unicode(self.dlg.dzialkaComboBox.currentText())
        varArkusz = unicode(self.dlg.arkuszComboBox.currentText())
        
        #request = QgsFeatureRequest().setFilterExpression( "\"OBREB\"='" + varObreb + "' OR \"NUMER\"='"+ varNumer + "'  OR \"ARKUSZ\"='"+ varArkusz + "'" )
        expr = QgsExpression( "\"OBREB\"='" + varObreb + "' AND \"NUMER\"='"+ varNumer + "'  AND \"ARKUSZ\"='"+ varArkusz + "'" )
        it = warstwa.getFeatures( QgsFeatureRequest( expr ) )
        ids = [i.id() for i in it]
        warstwa.setSelectedFeatures( ids )
        self.idAtlas = int(ids[0])
        
        #zoom do wybranej działki
        box = warstwa.boundingBoxOfSelected()
        self.iface.mapCanvas().setExtent(box)
        self.iface.mapCanvas().refresh()
        
    def szukajDate(self):
        # selekcja atrybutów na podstawie zaznaczonych wartości
        self.iface.mapCanvas().setSelectionColor( QColor("yellow") )
        warstwa = self.iface.mapCanvas().currentLayer()
        
        #wartości z coboBoxów do zmiennej
        varObreb_2 = self.dlg.obrebComboBox_2.currentText()
        varOdDate = self.dlg.odDateEdit.date().toString("dd.mm.yyyy")
        varDoDate = self.dlg.doDateEdit.date().toString("dd.mm.yyyy")
        
        #request = QgsFeatureRequest().setFilterExpression( "\"OBREB\"='" + varObreb + "' OR \"NUMER\"='"+ varNumer + "'  OR \"ARKUSZ\"='"+ varArkusz + "'" )
        expr = QgsExpression( "\"OBREB\"='" + varObreb_2 + "' AND \"OD\">='"+ varOdDate + "'  AND \"DO\"<='"+ varDoDate + "'" )
        it = warstwa.getFeatures( QgsFeatureRequest( expr ) )
        ids = [i.id() for i in it]
        warstwa.setSelectedFeatures( ids )
        
        #zoom do wybranej działki
        box = warstwa.boundingBoxOfSelected()
        self.iface.mapCanvas().setExtent(box)
        self.iface.mapCanvas().refresh()
        
    def printPDF(self):
        alayer = self.iface.activeLayer()
        # Dodaje wszystkie warstwy do widoku mapy
        myMapRenderer = self.iface.mapCanvas().mapRenderer()

        # ładuje szablon druku
        myComposition = QgsComposition(myMapRenderer)
        template = 'wyrys.qpt'
        
        #mapa w oparciu o zmienne z comboboxów
        
        #idAtlas = map(int, self.ids)
        #idAtlas = alayer.selectedFeaturesIds()

        myFile = r'C:\Users\haku\Desktop\Opole\Knurow\druk\wyrys.qpt'
        myTemplateFile = file(myFile, 'rt')
        myTemplateContent = myTemplateFile.read()
        myTemplateFile.close()


        myDocument = QDomDocument()
        myDocument.setContent(myTemplateContent)
        myComposition.loadFromTemplate(myDocument)

        # pobierz kompozycję mapy i zdefinuj skalę
        myAtlasMap = myComposition.getComposerMapById(0)
        
        # Konfiguracja Atlas
        myAtlas = myComposition.atlasComposition()#ustawia warstwÄ w atlasie
        
        myAtlas.setEnabled(True)
        myAtlas.setCoverageLayer(alayer)
        myAtlas.setHideCoverage(False)
        myAtlas.setSingleFile(True)
        myAtlas.setHideCoverage(False)
        
        myAtlasMap.setAtlasDriven(True)#mapa kontrolowana przez atlas
        myAtlasMap.setAtlasScalingMode(QgsComposerMap.Auto)# jaka skala kontrolowana przez atlas (margin)
        myComposition.setAtlasMode(QgsComposition.ExportAtlas)#Ustawia Atlas na Eksport do PDF

        myComposition.refreshItems()        



            # generuj atlas
        myAtlas.beginRender()
        
        myAtlas.prepareForFeature( self.idAtlas )
        saveDir = r'C:\Users\haku\Desktop\Opole\Knurow\druk\atlas\pdf'
        output_pdf = saveDir + str(self.idAtlas)+ "_MPZP_plan.pdf"
        myComposition.exportAsPDF(output_pdf)
        myAtlas.endRender()
        
    def printPD2(self):
        # parametry
        template_path = r'C:\Users\haku\Desktop\Opole\Knurow\druk\template1.qpt'
        mainPath = r'C:/Users/haku/.qgis2/python/plugins/rejestrDok/wydruki/'
        filename = QFileDialog.getSaveFileName(self.dlg, "Select output file ","", '*.pdf')
        imageType = "pdf"
        canvas = QgsMapCanvas()
        # Load our project
        #QgsProject.instance().read(QFileInfo(project_path))
        #bridge = QgsLayerTreeMapCanvasBridge(
        #    QgsProject.instance().layerTreeRoot(), canvas)
        #bridge.setCanvasLayers()

        template_file = file(template_path)
        template_content = template_file.read()
        template_file.close()
        document = QDomDocument()
        document.setContent(template_content)
        composition = QgsComposition(canvas.mapSettings())
        # You can use this to replace any string like this [key]
        # in the template with a new value. e.g. to replace
        # [date] pass a map like this {'date': '1 Jan 2012'}
        substitution_map = {
            'DATE_TIME_START': 'foo',
            'DATE_TIME_END': 'bar'}
        composition.loadFromTemplate(document, substitution_map)
        # You must set the id in the template
        map_item = composition.getComposerItemById('map')
        #map_item.setMapCanvas(canvas)
        #map_item.zoomToExtent(canvas.extent())
        # Trzeba ustawić id w szablonie
        #legend_item = composition.getComposerItemById('legend')
        #legend_item.updateLegend()
        composition.refreshItems()
        composition.exportAsPDF(filename)

        #image.save(filename, imageType)
        self.iface.messageBar().pushMessage(u'Sukces', u'Obraz został zapisany', level=QgsMessageBar.SUCCESS, duration=5)


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        
        self.dlg.btnGenerujPDF.clicked.connect(self.printPDF)
        self.dlg.btnSzukajTab2.clicked.connect(self.szukajDate)
        self.dlg.btnSzukaj.clicked.connect(self.szukaj)
        
        self.dlg.obrebComboBox.clear()
        self.dlg.dzialkaComboBox.clear()
        self.dlg.arkuszComboBox.clear()
        
        warstwa = self.iface.activeLayer()
        
        #filtr Obręby
        obreb = warstwa.dataProvider().fieldNameIndex( 'OBREB' ) 
        atrObreb = warstwa.dataProvider().uniqueValues( obreb )
        cbObreb = self.dlg.obrebComboBox.addItems( atrObreb )

        
                #filtr Działki
        dzialka = warstwa.dataProvider().fieldNameIndex( 'NUMER' ) 
        atrDzialka = warstwa.dataProvider().uniqueValues( dzialka )
        cbDzialka = self.dlg.dzialkaComboBox.addItems( atrDzialka )

        
                #filtr Arkusze
        arkusz = warstwa.dataProvider().fieldNameIndex( 'ARKUSZ' ) 
        atrArkusz = warstwa.dataProvider().uniqueValues( arkusz )
        cbArkusz = self.dlg.arkuszComboBox.addItems( atrArkusz )

        
                #filtr Obręby
        obreb_2 = warstwa.dataProvider().fieldNameIndex( 'OBREB' ) 
        atrObreb_2 = warstwa.dataProvider().uniqueValues( obreb_2 )
        cbObreb_2 = self.dlg.obrebComboBox_2.addItems( atrObreb_2 )
        
        
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
