
## 📊 VOMCS Spezifikation v1.0 (Technisches Datenblatt)

### 1. System-Architektur (Hardware-Ebene)
Das Speichermedium basiert auf einem dreidimensionalen, volumetrischen Bit-Gitter (Kubus) ohne starre physische Sektorierung.

* **Physische Dimension:** 3x3x3 Speicherzellen (Bits) für das Basismodell (skalierbar auf 228x228x228 für Megabit-Strukturen).
* **Zentraler Hardware-Anker:** Die absolute Mitte des Würfels (Koordinate `1,1,1` beim Basismodell) ist fest als Synchronisationsmarker auf den Zustand `1` (Schwarz) fixiert. Er dient der optischen Kalibrierung (Verzerrungs- und Laufzeitkorrektur).
* **Signalform:** Daten werden durch ein 3-Achsen-Interferenzverfahren (X, Y, Z) eingelesen, wodurch im Inneren ein stationäres 3D-Schachbrettmuster entsteht.

### 2. Die adaptive Inode-Schicht (Logische Ebene)
Folgedateien werden nicht physisch neu in den Würfel geschrieben, sondern als rein relationale Geometrie-Verweise (Pointer) in dedizierten Index-Ebenen oder extern gelagert. 

#### Struktur des Erweiterten VOMCS-Pointers (64-Bit-Layout):

| Bit-Bereich | Feldname | Funktion |
| :--- | :--- | :--- |
| **00 – 07** (8 Bit) | `MUSTER_ID` | Identifikator des anzuwendenden geometrischen Abtastmusters |
| **08 – 15** (8 Bit) | `ACHSEN_REF` | Primäre Scan-Richtung bzw. Achsenorientierung im Raum (X, Y, Z) |
| **16 – 39** (24 Bit) | `START_KOORD` | Die exakte 3D-Anfangsadresse im Würfel ($8\text{ Bit }X, 8\text{ Bit }Y, 8\text{ Bit }Z$) |
| **40 – 63** (24 Bit) | `BIT_LAENGE` | Anzahl der fortlaufend zu lesenden Bits entlang des Musterpfads |

### 3. Vordefiniertes Muster-Verzeichnis (Standard-Geometrien)
Die KI und der Lese-Algorithmus nutzen zur Datenintegration verschiedene geometrische Pfade:

* **Muster `0x01` — Linksdrehende 2D-Spirale:** 
  Tastet eine Ebene von oben links, die Außenkante linksdrehend abwärts entlang, nach innen zum lokalen Zentrum ab. Hervorragend geeignet für repetitive Bitfolgen.
* **Muster `0x02` — 3D-Hilbert-Kurve:** 
  Ein fraktaler, raumfüllender Pfad. Hält lokale Bit-Nachbarschaften extrem stabil. Ideal für komplexe Medien- und Sensorstrukturen.
* **Muster `0x03` — Boustrophedon-Raster (Zickzack):** 
  Klassischer Zeilen-Scan mit alternierender Richtung. Optimal für sequentielle Textdaten.
* **Muster `0x04` — Sphärischer Schalen-Scan:** 
  Tastet den Würfel in konzentrischen 3D-Hüllen von außen nach innen zum Kern ab. Perfekt für hoch-entropische Datenströme.


# VOMCS - Volumetric Open Multi-Pattern Compression Standard

Dieses Repository enthält die theoretische Spezifikation für ein adaptives, 
geometrisches 3D-Datenkompressionsverfahren für holografische und volumetrische Speichermedien.

## ⚖️ Lizenz & Rechtlicher Hinweis (Stand der Technik)
Dieses Konzept wird hiermit als **Open Source** der Allgemeinheit zur Verfügung gestellt. 
Mit der Veröffentlichung auf GitHub ist diese Technologie offiziell Teil des globalen 
**Stands der Technik (Prior Art)**. Eine exklusive Patentierung oder kommerzielle Monopolisierung 
dieses Verfahrens durch Dritte ist damit rechtlich ausgeschlossen.

**Nutzungsbedingungen:**
* **Non-Profit & Forschung:** Die private, wissenschaftliche und gemeinnützige Nutzung, 
  Modifikation und Weiterentwicklung ist ausdrücklich erlaubt und kostenfrei.
* **Kommerzielle Nutzung:** Jede kommerzielle Verwertung oder Implementierung in proprietäre 
  Produkte bedarf der ausdrücklichen Genehmigung und Lizenzierung durch den Urheber.
