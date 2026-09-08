
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

  
## 🔍 Abgrenzung zum Stand der Technik (State of the Art)

Zur Wahrung der Erfindungshöhe und zur rechtlichen Absicherung gegen Fehlinterpretationen wird VOMCS hiermit explizit von bestehenden Arbeiten zur neuronalen Volumenkompression und klassischen Dateisystemen abgegrenzt.

### 1. Wissenschaftliche Differenzierung

#### Abgrenzung zu arXiv:2401.08840 (Devkota & Pattanaik)
* **Der Ansatz des Papers:** Nutze Coordinate-Based Networks und Multi-Resolution Hash Encoding, um die Intensitätswerte *eines spezifischen* 3D-Datensatzes (z. B. MRT/CT) direkt in den Gewichten eines MLPs abzubilden. Kompression entsteht durch Verkleinerung des neuronalen Netzwerks im Vergleich zum Rohdatensatz.
* **Die VOMCS-Innovation:** VOMCS nutzt das resultierende 3D-Schachbrettmuster (den bereits komprimierten Raum) als **universelles geometrisches Wörterbuch**. VOMCS trainiert das Netzwerk nicht für jede Folgedatei neu. Stattdessen sucht eine KI nach Übereinstimmungen und speichert Folgedateien rein als *Pointer-Sequenzen*.

#### Abgrenzung zu herkömmlichen volumetrischen Dateisystemen (z. B. NeuralVDB)
* **Der traditionelle Ansatz:** Datenpunkte werden in starren, hierarchischen Baumstrukturen oder entlang vordefinierter, unelastischer Scan-Pfade (z. B. linear oder per Zickzack) adressiert.
* **Die VOMCS-Innovation:** Der Abtastpfad selbst ist im VOMCS-Pointer als **dynamische Variable (`MUSTER_ID`) auf Inode-Ebene** hinterlegt. Derselbe physische 3D-Speicherpunkt wird je nach Bedarf via Spirale, Hilbert-Kurve oder Schalen-Scan uminterpretiert. Das gab es in dieser Form in keinem Dateisystem.

---

### 💡 Veranschaulichung durch Alltagsszenarien

Um das mathematische Kernprinzip von VOMCS greifbar zu machen, lässt es sich durch folgende Analogien beschreiben:

#### Das "Buch-Szenario" (VOMCS vs. klassische ZIP-Kompression)
* **Klassisches ZIP:** Ein Kompressionsprogramm scannt einen Text, findet das Wort "Apfelbaum" zehnmal, ersetzt es durch eine kurze Abkürzung und speichert dieses Wörterbuch *mit in die Datei*.
* **Das VOMCS-Prinzip:** Wir nehmen ein bereits gedrucktes, riesiges Buch (deine erste Datei im Würfel). Wenn du einen neuen Text speichern willst, schreibst du nicht die Buchstaben auf, sondern generierst eine Wegbeschreibung: *"Nimm Wort 5 von Seite 20, lies dann rückwärts bis Wort 2, springe auf Seite 50 und lies dort im Kreis."* Die Information wird **allein durch die Geometrie der Lesebewegung** auf einem starren Medium erzeugt.

#### Das "Chamäleon-Matrix-Szenario" (Mehrfachnutzung derselben Bits)
* **Klassische Festplatte:** Sektor 1 ist immer Sektor 1. Wenn dort eine `0` steht, liest der Computer eine `0`. Jedes Bit hat genau eine Funktion.
* **Das VOMCS-Prinzip:** Durch die verschiedenen Raumachsen und variablen Muster liest das System dieselbe physische Speicherzelle in Muster 1 (Spirale) als Bit Nr. 3, in Muster 2 (Zickzack) als Bit Nr. 78 und in Muster 3 als Teil des zentralen Markers. Ein physisches Bit existiert im logischen Datenstrom **mehrfach an völlig unterschiedlichen Stellen**.

#### Das "Tresor-Szenario" (Kryptographischer Mehrwert)
* **Klassische Verschlüsselung:** Ein digitaler Schlüssel füttert einen mathematischen Algorithmus, um eine lange Reihe von Zufallszahlen zu generieren.
* **Das VOMCS-Prinzip:** Der 3D-Würfel dient als physischer, unknackbarer Datentresor. Da die `MUSTER_ID` in den Inodes bestimmt, wie die Spirale abbiegt oder wo die Hilbert-Kurve ansetzt, entstehen aus den exakt gleichen 27 Start-Bits Milliarden unterschiedlicher Schlüsselketten. Ohne die exakte Muster-Reihenfolge ist es mathematisch unmöglich, die versteckte zweite Datei zu rekonstruieren.

