import numpy as np

class GaussGeodeECC:
    def __init__(self, size=10):
        # Für den PoC nutzen wir eine handliche 10x10x10 Matrix im RAM
        self.size = size
        self.matrix = np.zeros((size, size, size), dtype=int)

    def write_data_bit(self, x, y, z, val):
        """Schreibt ein Bit in die Geode."""
        if 0 <= x < self.size-1 and 0 <= y < self.size-1 and 0 <= z < self.size-1:
            self.matrix[x, y, z] = val

    def calculate_3d_parity(self):
        """
        Der 3D-Schraubstock: Berechnet die Paritäts-Bits entlang aller 3 Raumachsen.
        Die jeweils letzten Sektoren (Index size-1) jeder Achse dienen als Speicher
        für die Kontroll-Bits (Gerade Parität).
        """
        # 1. X-Parität (Zeilen prüfen)
        for y in range(self.size):
            for z in range(self.size):
                summe = np.sum(self.matrix[0:self.size-1, y, z])
                self.matrix[self.size-1, y, z] = summe % 2

        # 2. Y-Parität (Spalten prüfen)
        for x in range(self.size):
            for z in range(self.size):
                summe = np.sum(self.matrix[x, 0:self.size-1, z])
                self.matrix[x, self.size-1, z] = summe % 2

        # 3. Z-Parität (Schichten prüfen)
        for x in range(self.size):
            for y in range(self.size):
                summe = np.sum(self.matrix[x, y, 0:self.size-1])
                self.matrix[x, y, self.size-1] = summe % 2

    def scan_and_repair(self):
        """
        Das Lesegerät scannt die Gauss Geode. Weicht die berechnete Parität
        vom gespeicherten Zustand ab, schnappt das geometrische Fadenkreuz zu.
        """
        print("\n[GAUSS-Scanner] Starte 3D-Feld-Integritätsprüfung...")
        
        error_x = -1
        error_y = -1
        error_z = -1

        # Prüfe X-Achse
        for y in range(self.size-1):
            for z in range(self.size-1):
                summe = np.sum(self.matrix[0:self.size-1, y, z])
                if (summe % 2) != self.matrix[self.size-1, y, z]:
                    error_y = y
                    error_z = z
                    break

        # Prüfe Y-Achse
        for x in range(self.size-1):
            for z in range(self.size-1):
                summe = np.sum(self.matrix[x, 0:self.size-1, z])
                if (summe % 2) != self.matrix[x, self.size-1, z]:
                    error_x = x
                    break

        # Auswertung des geometrischen Fadenkreuzes
        if error_x != -1 and error_y != -1 and error_z != -1:
            print(f"⚠️ FEHLER LOKALISIERT! Bruch in der magnetischen Flussdichte erkannt.")
            print(f" -> Geometrisches Fadenkreuz rastet ein bei Koordinate: ({error_x}, {error_y}, {error_z})")
            
            # Die Reparatur: Flippe das Bit einfach um!
            altes_bit = self.matrix[error_x, error_y, error_z]
            neues_bit = 1 if altes_bit == 0 else 0
            self.matrix[error_x, error_y, error_z] = neues_bit
            
            print(f"🔧 REPARATUR ERFOLGREICH: Bit an Stelle ({error_x},{error_y},{error_z}) von {altes_bit} auf {neues_bit} korrigiert.")
            return True
        else:
            print("✅ MATRIX INTEGRITÄT NOMINAL: Keine Bit-Verzerrungen gefunden.")
            return False

# --- LIVE TEST IN DER WERKSTATT ---
if __name__ == "__main__":
    print("--- GAUSS CORE ECC TESTLAUF ---")
    geode = GaussGeodeECC(size=10)
    
    # 1. Wir schreiben ein paar Testdaten in unsere Gauss Geode™
    geode.write_data_bit(3, 4, 5, 1) # Ein wichtiges Datenbit
    geode.write_data_bit(1, 2, 3, 1) # Noch ein Datenbit
    
    # 2. Parität berechnen und einbrennen
    geode.calculate_3d_parity()
    print("[System] 3D-Kreuzparität erfolgreich in der Geode verankert.")
    
    # 3. DER UNFALL: Wir simulieren einen bösen Lesefehler an Koordinate (3, 4, 5)
    # Ein Staubkorn manipuliert das Bit im RAM des Lesegeräts fälschlicherweise auf 0
    print("\n💥 STÖRUNG: Ein Partikel verzerrt das Signal an Position (3, 4, 5)!")
    geode.matrix[3, 4, 5] = 0 
    
    # 4. Der Scanner wirft das Rettungssystem an
    geode.scan_and_repair()
    
    # 5. Gegenkontrolle: Ist das Bit wieder da?
    print(f"\n[Verifikation] Zustand des Bits an Koordinate (3, 4, 5) ist jetzt wieder: {geode.matrix[3, 4, 5]} (Soll-Wert: 1)")
