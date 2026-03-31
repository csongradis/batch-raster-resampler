# batch-raster-resampler
A QGIS plugin for batch resizing and resampling raster datasets.
A geoinformatikai gyakorlatban gyakran előforduló feladat a nagyméretű raszteres állományok, például ortofotók vagy domborzatmodellek felbontásának módosítása.
A jelenlegi QGIS funkcionalitás (pl. GDAL "Warp (reproject)" eszköz) lehetővé teszi egy-egy raszter átméretezését, de több fájl esetén ez a folyamat időigényes lehet. Ez a feladat egy olyan QGIS plugin fejlesztését tűzte ki célul, amely automatizálja ezt a munkafolyamatot, lehetővé téve egy teljes mappában lévő összes raszterfájl kötegelt átméretezését a felhasználó által megadott cél pixelméretre.
2. A Kifejlesztett Plugin: Batch Raster Resampler
A "Batch Raster Resampler" (Kötegelt raszter átméretező) egy Python nyelven írt QGIS plugin, amely integrálódik a QGIS Feldolgozó Eszköztárába (Processing Toolbox). A plugin célja, hogy egyszerű és felhasználóbarát felületet biztosítson .tif (és .tiff) kiterjesztésű raszterfájlok kötegelt átméretezéséhez.
Főbb funkciók:
•	Kötegelt feldolgozás: Egy teljes mappa tartalmát képes feldolgozni, automatikusan végigiterálva az összes támogatott raszterfájlon.
•	Felhasználó által definiált célfelbontás: A felhasználó megadhatja a kívánt cél X és Y pixelméretet a raszterek eredeti vetületi rendszerének egységében (pl. méterben).
•	Átmintavételezési módszer kiválasztása: Többféle átmintavételezési algoritmus közül lehet választani (pl. Legközelebbi szomszéd, Bilineáris, Kubikus), így a felhasználó az adat típusának és a kívánt eredménynek megfelelően optimalizálhatja a folyamatot.
•	Vetületi rendszer megőrzése: A plugin nem változtatja meg a raszterek eredeti vetületi rendszerét, csupán a pixelméretüket módosítja.
•	.tfw (World fájl) generálása: Az átméretezett .tif fájlok mellé automatikusan létrehozza a megfelelő .tfw georeferencia fájlokat.
•	Egyszerű felhasználói felület: A QGIS Feldolgozó Eszköztárának megszokott felületén keresztül érhető el, könnyen kezelhető paraméterekkel.
•	Naplózás: A feldolgozás során visszajelzést ad a folyamatról és az esetleges hibákról.
3. Működési Elv és Használt Technológiák
A plugin a QGIS Python API-ját (PyQGIS) és a GDAL (Geospatial Data Abstraction Library) könyvtár QGIS-be integrált eszközeit használja a raszteres műveletek végrehajtásához. Konkrétan a gdal:warpreproject (vagy hasonló nevű) feldolgozó algoritmust hívja meg a háttérben a megfelelő paraméterekkel.
A munkafolyamat a következőképpen zajlik:
1.	A felhasználó a plugin felületén megadja a bemeneti mappát, a cél pixelméreteket, az átmintavételezési módszert és a kimeneti mappát.
2.	A plugin végigiterál a bemeneti mappában található .tif és .tiff fájlokon.
3.	Minden egyes fájlra meghívja a GDAL átméretező funkcióját a megadott paraméterekkel, beleértve a .tfw fájl létrehozására vonatkozó opciót is.
4.	Az eredményfájlokat a megadott kimeneti mappába menti, az eredeti fájlnévhez egy _resampled utótagot fűzve.
Használt technológiák:
•	QGIS: Verzió 3.16 vagy újabb (tesztelve QGIS 3.32.0 "Lima" verzióval).
•	Python: A QGIS-sel telepített Python verzió (tesztelve Python 3.9.5 verzióval).
•	PyQGIS: A QGIS Python API-ja.
•	GDAL: A raszteres műveletek végrehajtásához (QGIS-be integrált verzió, tesztelve GDAL 3.7.0 verzióval).
