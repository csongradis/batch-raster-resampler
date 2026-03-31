# -*- coding: utf-8 -*-

import os
from qgis.core import (
    Qgis,
    QgsProcessingFeedback,
    QgsProcessingContext,
    QgsProcessingAlgorithm,
    QgsProcessingParameterNumber,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFolderDestination,
    QgsProcessingParameterFile,
    QgsApplication, 
    QgsMessageLog
)

from qgis import processing

class BatchRasterResampleAlgorithm(QgsProcessingAlgorithm):
    INPUT_FOLDER = 'INPUT_FOLDER'
    OUTPUT_FOLDER = 'OUTPUT_FOLDER'
    TARGET_RESOLUTION_X_UI = 'TARGET_RESOLUTION_X_UI' # UI paraméter neve
    TARGET_RESOLUTION_Y_UI = 'TARGET_RESOLUTION_Y_UI' # UI paraméter neve
    RESAMPLING_METHOD = 'RESAMPLING_METHOD'

    RESAMPLING_METHODS_DESC = [
        '0: Legközelebbi szomszéd (Nearest Neighbour)',
        '1: Bilineáris (Bilinear)',
        '2: Kubikus (Cubic)',
        '3: Kubikus spline (Cubic Spline)',
        '4: Lanczos',
        '5: Átlag (Average)',
        '6: Módusz (Mode)',
        '7: Maximum',
        '8: Minimum',
        '9: Medián (Median)',
        '10: Alsó kvartilis (Q1)',
        '11: Felső kvartilis (Q3)'
    ]

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT_FOLDER,
                'Bemeneti mappa (.tif fájlokkal)', 
                behavior=QgsProcessingParameterFile.Folder
            )
        )
        # A felhasználói felületen továbbra is X és Y pixelméretet kérünk
        self.addParameter(
            QgsProcessingParameterNumber(
                self.TARGET_RESOLUTION_X_UI, # UI paraméter
                'Cél X pixelméret (a raszter vetületének egységében)', 
                type=QgsProcessingParameterNumber.Double,
                defaultValue=5.0, 
                minValue=0.000001
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.TARGET_RESOLUTION_Y_UI, # UI paraméter
                'Cél Y pixelméret (a raszter vetületének egységében)', 
                type=QgsProcessingParameterNumber.Double,
                defaultValue=5.0, 
                minValue=0.000001
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                self.RESAMPLING_METHOD,
                'Átmintavételezési módszer', 
                options=self.RESAMPLING_METHODS_DESC,
                defaultValue=1, 
                optional=False
            )
        )
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.OUTPUT_FOLDER,
                'Kimeneti mappa' 
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Felhasználó által megadott értékek
        user_target_res_x = self.parameterAsDouble(parameters, self.TARGET_RESOLUTION_X_UI, context)
        user_target_res_y = self.parameterAsDouble(parameters, self.TARGET_RESOLUTION_Y_UI, context)
        
        input_folder = self.parameterAsString(parameters, self.INPUT_FOLDER, context)
        output_folder = self.parameterAsString(parameters, self.OUTPUT_FOLDER, context)
        resampling_method_index = self.parameterAsEnum(parameters, self.RESAMPLING_METHOD, context)

        algo_id_to_check = "gdal:warpreproject"
        gdal_warp_algo = QgsApplication.processingRegistry().algorithmById(algo_id_to_check)

        if gdal_warp_algo is None:
            error_msg = f"A '{algo_id_to_check}' algoritmus nem található a Processing Registry-ben."
            feedback.reportError(error_msg, fatalError=True)
            # ... (a korábbi hibakezelő kód változatlan, itt nem másolom be újra a rövidség kedvéért) ...
            gdal_algorithms = QgsApplication.processingRegistry().algorithms()
            available_gdal_ids = []
            feedback.pushInfo("Elérhető algoritmusok keresése (GDAL)...")
            for alg in gdal_algorithms:
                current_id = alg.id()
                if current_id.startswith("gdal:"):
                    available_gdal_ids.append(current_id)
            if available_gdal_ids:
                feedback.pushInfo("Elérhető GDAL algoritmusok azonosítói:")
                for gdal_id in sorted(available_gdal_ids):
                    feedback.pushInfo(f"- {gdal_id}")
            else:
                feedback.pushInfo("Nem található egyetlen GDAL algoritmus sem a registry-ben.")
            return {self.OUTPUT_FOLDER: None}
        else:
            feedback.pushInfo(f"A '{algo_id_to_check}' algoritmus sikeresen megtalálva.")


        if not os.path.exists(input_folder) or not os.path.isdir(input_folder):
            feedback.reportError(f"Bemeneti mappa nem található vagy nem mappa: {input_folder}", fatalError=True)
            return {self.OUTPUT_FOLDER: None}

        if not os.path.exists(output_folder):
            try:
                os.makedirs(output_folder)
                feedback.pushInfo(f"Kimeneti mappa létrehozva: {output_folder}")
            except Exception as e:
                feedback.reportError(f"Nem sikerült létrehozni a kimeneti mappát: {output_folder}. Hiba: {e}", fatalError=True)
                return {self.OUTPUT_FOLDER: None}

        tif_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.tif', '.tiff'))]
        total_files = len(tif_files)
        feedback.pushInfo(f"Talált .tif/.tiff fájlok száma: {total_files}")

        if total_files == 0:
            feedback.reportError("Nem található .tif vagy .tiff kiterjesztésű fájl a bemeneti mappában.", fatalError=True)
            return {self.OUTPUT_FOLDER: output_folder}

        processed_files_count = 0
        
        # Figyelmeztetés, ha a felhasználó nem négyzetes pixelt adott meg, de mi az X-et használjuk
        if user_target_res_x != user_target_res_y:
            feedback.pushWarning(f"Figyelem: A cél X ({user_target_res_x}) és Y ({user_target_res_y}) pixelméret eltérő. " \
                                 f"Az algoritmus a {user_target_res_x} értéket használja a TARGET_RESOLUTION paraméterhez (négyzetes pixeleket feltételezve).")
                                 # Warning: Target X and Y pixel sizes differ. The algorithm will use {user_target_res_x} for TARGET_RESOLUTION (assuming square pixels).

        # A gdal:warpreproject algoritmusnak átadandó célfelbontás
        # (az X értéket használjuk, feltételezve, hogy a felhasználó négyzetes pixeleket szeretne)
        target_resolution_for_algo = user_target_res_x

        feedback.pushInfo(f"Felhasználói cél X pixelméret: {user_target_res_x}, Y pixelméret: {user_target_res_y}")
        feedback.pushInfo(f"Algoritmusnak átadott TARGET_RESOLUTION: {target_resolution_for_algo}")


        for index, filename in enumerate(tif_files):
            if feedback.isCanceled():
                feedback.pushInfo("Feldolgozás megszakítva.")
                break

            input_raster_path = os.path.join(input_folder, filename)
            base, ext = os.path.splitext(filename)
            output_raster_name = f"{base}_resampled{ext}"
            output_raster_path = os.path.join(output_folder, output_raster_name)

            feedback.pushInfo(f"({index + 1}/{total_files}) Feldolgozás alatt: {filename} -> {output_raster_name}")
            feedback.setProgress(((index + 1) / total_files) * 100)

            alg_params = {
                'INPUT': input_raster_path,
                'SOURCE_CRS': None,
                'TARGET_CRS': None,
                'RESAMPLING': resampling_method_index,
                'NODATA': None,
                # VÁLTOZTATÁS: A TARGET_RESOLUTION paramétert használjuk, TR_X és TR_Y törölve
                # CHANGE: Use TARGET_RESOLUTION parameter, TR_X and TR_Y removed
                'TARGET_RESOLUTION': target_resolution_for_algo, 
                # 'TR_X': None, # Törölve - Removed
                # 'TR_Y': None, # Törölve - Removed
                'DATA_TYPE': 0,
                'OPTIONS': 'TFW=YES', 
                'TARGET_EXTENT': None,
                'OUTPUT': output_raster_path
            }
            
            try:
                result = processing.run(
                    algo_id_to_check, 
                    alg_params,
                    context=context,
                    feedback=feedback,
                    is_child_algorithm=True
                )

                if result and result.get('OUTPUT') and os.path.exists(result['OUTPUT']):
                    feedback.pushInfo(f"Sikeresen átméretezve: {output_raster_path}")
                    processed_files_count += 1
                else:
                    feedback.reportError(f"Hiba a(z) {filename} feldolgozása során a '{algo_id_to_check}' algoritmussal. A kimenet nem jött létre, vagy a result üres.", fatalError=False)
                    feedback.pushDebugInfo(f"GDAL Warp result for {filename}: {result}")

            except Exception as e:
                import traceback
                feedback.reportError(f"Kritikus hiba történt a(z) {filename} feldolgozása során a '{algo_id_to_check}' hívásakor: {str(e)}\n{traceback.format_exc()}", fatalError=False)


        if feedback.isCanceled():
            feedback.pushInfo(f"Feldolgozás megszakítva. {processed_files_count}/{total_files} fájl lett feldolgozva a megszakításig.")
        else:
            feedback.pushInfo(f"Feldolgozás befejezve. {processed_files_count}/{total_files} fájl sikeresen átméretezve.")
        
        return {self.OUTPUT_FOLDER: output_folder}

    def name(self):
        return 'batchrasterresampler'

    def displayName(self):
        return 'Kötegelt raszter átméretező (felbontás módosító)'

    def group(self):
        return 'Raszter Műveletek'

    def groupId(self):
        return 'rasteroperations'

    def shortHelpString(self):
        return """
Ez az algoritmus egy megadott mappában lévő összes .tif vagy .tiff raszterfájl felbontását (pixelméretét) módosítja
a felhasználó által meghatározott cél X és Y pixelméretre. A kimeneti fájlok egy külön mappába kerülnek
"_resampled" utótaggal a nevükben. A művelet megőrzi az eredeti vetületi rendszert és létrehoz .tfw fájlokat.
Az algoritmus a megadott X pixelméretet használja a célfelbontásként (négyzetes pixeleket feltételezve).

This algorithm changes the resolution (pixel size) of all .tif or .tiff raster files in a specified input folder
to a user-defined target X and Y pixel size. Output files are saved to a separate output folder
with a "_resampled" suffix in their names. The operation preserves the original coordinate reference system and creates .tfw files.
The algorithm uses the specified X pixel size as the target resolution (assuming square pixels).
"""

    def createInstance(self):
        return BatchRasterResampleAlgorithm()
