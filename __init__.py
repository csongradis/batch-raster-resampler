# -*- coding: utf-8 -*-
from qgis.core import QgsMessageLog, Qgis

# Ezt a függvényt hívja meg a QGIS a plugin betöltésekor.
def classFactory(iface):
    QgsMessageLog.logMessage("BatchRasterResampler (__init__.py): classFactory called", "PluginDev", Qgis.Info)
    try:
        from .processing_provider import BatchRasterResamplerProvider
        QgsMessageLog.logMessage("BatchRasterResampler (__init__.py): BatchRasterResamplerProvider imported from .processing_provider", "PluginDev", Qgis.Info)
        
        provider_instance = BatchRasterResamplerProvider() # Példányosítás
        QgsMessageLog.logMessage("BatchRasterResampler (__init__.py): BatchRasterResamplerProvider instance created", "PluginDev", Qgis.Info)
        
        return provider_instance # Visszaadjuk a provider példányt
    except Exception as e:
        QgsMessageLog.logMessage(f"BatchRasterResampler (__init__.py): Error in classFactory: {str(e)}", "PluginDev", Qgis.Critical)
        import traceback
        QgsMessageLog.logMessage(traceback.format_exc(), "PluginDev", Qgis.Critical)
        return None

def name():
    return "Batch Raster Resampler"

def description():
    return "Provides algorithms for batch raster resampling to a target resolution."

def version():
    return "1.0.5" # Verziószám növelése

def qgisMinimumVersion():
    return "3.16"

def authorName():
    return "Te Neved & Gemini"

# A modul szintű plugin_load és plugin_unload függvényekre itt nincs szükség,
# mivel a QGIS a classFactory által visszaadott objektum initGui és unload metódusait hívja.
# Ha mégis szükség lenne rájuk valamilyen általánosabb plugin inicializáláshoz, akkor itt lennének.
# def plugin_load(iface):
#     pass
# def plugin_unload():
#     pass

# Opcionális: ikon a Plugin Managerben
# def icon():
#     return "icon.png"
