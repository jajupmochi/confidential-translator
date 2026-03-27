## Mur4Cast Daten Oesterreich

die *verlinkenden Variablen* zwischen den Tabellen sind in kursiv dargestellt!

### ereignisse.xlsx

Beschreibung der Ereignisse.\
Genaue Variablen Beschreibung siehe: **ereignisse_legende.csv**

- *ereignis_id*:	Ereignis ID 
- Ereignisdatum: Tag des Ereignis
- volumen:	Volumen in m³ (abgelagert)
- EZG_NS_Dauer:	Niederschlagsdauer in Minuten
- EZG_NS_Intensitaet:	Niederschlagshoehe in mm


### ezgEreignisse.csv

Verlinkung der Ereignisse mit den Einzugsgebieten.

- *ezg_id*: Einzugsgebiets ID (selbst gesetzt)
- *ereignis_id*: Ereignis ID

In einem Einzugsgebiet koennen mehrere Ereignisse vorkommen.


### ezgTerrainAnalysis.csv

Beschreibung des Gelaendes und Landbedeckung der einzelnen Einzugsgebieten. 
Landbedeckungskategorien: Fels, Grasland, Wald, Sparsely_vegetated_areas, Sonstige(keine separate Geroell-Kategorie vorhanden).

- *ezg_id*: Einzugsgebiets ID
- EZG_Anteil_Fels: Anteil an Fels innerhalb des EZG (0-1)
- EZG_Anteil_Grasland: Anteil an Grasland innerhalb des EZG (0-1)
- EZG_Anteil_Wald: Anteil an Wald innerhalb des EZG (0-1)
- EZG_Anteil_Sparsely_vegetated_areas: Anteil an Sparsely_vegetated_areas (0-1) (Landbedeckungskategorie, die im AT-Datensatz vorkommt, nicht im CH-Datensatz)
- EZG_Anteil_uebrig: Anteil an uebrigen Landbedeckung innerhalb des EZG (0-1)
- ...: weitere EZG- und Gerinneparameter aus DTM-Ableitung (analog CH-Datensatz)

### ezgSpartacusCoordinates.csv

Koordinaten fuer die Meteorologischen Daten ([Spartacus Datensatz](https://data.hub.geosphere.at/dataset/spartacus-v2-1d-1km)).\
mit dem Skript **downloadSpartacusData.py** koennen die Spartacus (Meteo) Daten heruntergeladen werden:
- in Zeile 24: outDir definieren (Pfad zu Ordner, in den die Daten gespeichert werden)
2025- das Skript laedt fuer alle Jahre (1961-2025) und alle Variablen netcdf - files herunter:
    - die Filenamen sind: "SPARTACUS2-DAILY_{variable}_{jahr}.nc"
    - die Variablen sind: 
		-"TX" Maximumtemperatur  (°C)
		-"TN" Minimumtemperatur (°C)
		-"RR" Nierschlagssumme (km/m²)
		-"SA" Sonnenscheindauer (sec)
    - Die netcdf Daten enthalten Tageswerte fuer ganz Oesterreich in 1 km Aufloesung
    - Die Dimensionen der netcdf Daten sind x (x-Koordinate innerhalb Oesterreich), y (y-Kooorinate), time (Tag innerhalb eines Jahres). x und y sind jeweils die Zentren der Raster-Grid-Zellen. Die Data variable enthält die Werte für die entsprechende Variable.
    - EPSG: 3416

- in **ezgSpartacusCoordinates.csv** sind :
    - *ezg_id*: Einzugsgebiets ID
    - x: x - Koordinate des Zentrums der Spartacus- Grid - Zelle, in der das Einzugsgebiet liegt (eine Dimension der netcdf Datei)
    - y: y - Koordinate des Zentrums der Spartacus- Grid - Zelle, in der das Einzugsgebiet liegt (eine Dimension der netcdf Datei)
    - ratio: Anteil, wie viel Flache der Spartacus- Grid - Zelle vom Einzugsgebiet abgedeckt ist (der minimum threhsold für den Flaechenanteil ist 0.00001)
