# -*- coding: utf-8 -*-

from qgis.core import QgsProcessingProvider, QgsMessageLog, Qgis, QgsApplication # Hozzáadva: QgsApplication
from qgis.PyQt.QtGui import QIcon
import os

from .batch_raster_resample_algorithm import BatchRasterResampleAlgorithm

class BatchRasterResamplerProvider(QgsProcessingProvider):

    def __init__(self):
        QgsMessageLog.logMessage("BatchRasterResamplerProvider: __init__ called", "PluginDev", Qgis.Info)
        super().__init__() # Fontos, hogy ez legyen az első!
        
        # Próbáljuk meg itt expliciten hozzáadni a providert a registry-hez
        # Ez általában nem ajánlott itt, de a jelenlegi helyzetben egy kísérlet
        try:
            if not QgsApplication.processingRegistry().providerById(self.id()):
                if QgsApplication.processingRegistry().addProvider(self):
                    QgsMessageLog.logMessage(f"BatchRasterResamplerProvider: Provider '{self.name()}' EXPLICITLY ADDED to registry in Provider __init__.", "PluginDev", Qgis.Info)
                else:
                    QgsMessageLog.logMessage(f"BatchRasterResamplerProvider: FAILED to add provider '{self.name()}' to registry in Provider __init__.", "PluginDev", Qgis.Critical)
            else:
                QgsMessageLog.logMessage(f"BatchRasterResamplerProvider: Provider '{self.name()}' was ALREADY REGISTERED (checked in Provider __init__).", "PluginDev", Qgis.Warning)
        except Exception as e:
            QgsMessageLog.logMessage(f"BatchRasterResamplerProvider: Error during explicit addProvider in __init__: {e}", "PluginDev", Qgis.Critical)


    def load(self) -> bool: # A QgsProcessingProvider.load() metódus felülírása naplózáshoz
        QgsMessageLog.logMessage(f"BatchRasterResamplerProvider: load() method called for provider '{self.name()}'. Attempting to load algorithms.", "PluginDev", Qgis.Info)
        # Hívjuk meg az ősosztály load() metódusát, ami majd meghívja a loadAlgorithms()-t
        # A load() metódus bool értéket ad vissza, jelezve a sikerességet.
        loaded_successfully = super().load()
        if loaded_successfully:
            QgsMessageLog.logMessage(f"BatchRasterResamplerProvider: super().load() reported SUCCESS for '{self.name()}'.", "PluginDev", Qgis.Info)
        else:
            QgsMessageLog.logMessage(f"BatchRasterResamplerProvider: super().load() reported FAILURE for '{self.name()}'. Algorithms might not be loaded.", "PluginDev", Qgis.Warning)
        return loaded_successfully

    def loadAlgorithms(self): # Ezt a metódust a QgsProcessingProvider.load() hívja meg
        QgsMessageLog.logMessage("BatchRasterResamplerProvider: loadAlgorithms called", "PluginDev", Qgis.Info)
        try:
            alg = BatchRasterResampleAlgorithm()
            self.addAlgorithm(alg)
            QgsMessageLog.logMessage(f"BatchRasterResamplerProvider: Algorithm '{alg.displayName()}' added.", "PluginDev", Qgis.Info)
        except Exception as e:
            QgsMessageLog.logMessage(f"BatchRasterResamplerProvider: Error in loadAlgorithms: {e}", "PluginDev", Qgis.Critical)
            import traceback
            QgsMessageLog.logMessage(traceback.format_exc(), "PluginDev", Qgis.Critical)

    def id(self):
        return 'batch_raster_resampler_provider'

    def name(self):
        return 'Batch Raster Resampler Tools'

    def longName(self):
        return self.name()

    def icon(self):
        plugin_dir = os.path.dirname(__file__)
        icon_path = os.path.join(plugin_dir, 'icon.png')
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return QIcon()

    def initGui(self):
        QgsMessageLog.logMessage("BatchRasterResamplerProvider: initGui called", "PluginDev", Qgis.Info)
        pass 

    def unload(self):
        QgsMessageLog.logMessage("BatchRasterResamplerProvider: unload called", "PluginDev", Qgis.Info)
        # Amikor a provider maga kerül eltávolításra a registry-ből, ez a metódus is lefuthat.
        # Itt nem kell expliciten eltávolítani a registry-ből, ha a QGIS kezeli a plugin életciklusát.
        # Ha az __init__-ben adjuk hozzá, akkor itt lehetne eltávolítani, de óvatosan.
        try:
            if QgsApplication.processingRegistry().providerById(self.id()):
                if QgsApplication.processingRegistry().removeProvider(self.id()):
                    QgsMessageLog.logMessage(f"BatchRasterResamplerProvider: Provider '{self.name()}' EXPLICITLY REMOVED from registry in Provider unload.", "PluginDev", Qgis.Info)
                else:
                    QgsMessageLog.logMessage(f"BatchRasterResamplerProvider: FAILED to remove provider '{self.name()}' from registry in Provider unload.", "PluginDev", Qgis.Warning)
        except Exception as e:
            QgsMessageLog.logMessage(f"BatchRasterResamplerProvider: Error during explicit removeProvider in unload: {e}", "PluginDev", Qgis.Critical)
        super().unload() # Fontos lehet az ősosztály unload() metódusának hívása
