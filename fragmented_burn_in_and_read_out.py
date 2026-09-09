# -*- coding: utf-8 -*-
import numpy as np
import math

class GaussGeodeCompiler:
    def __init__(self, size=300, seed=1337):
        self.size = size
        self.matrix = np.zeros((size, size, size), dtype=np.uint8)
        self.seed = seed

    def text_to_bits(self, text):
        bits = []
        for char in text:
            bin_char = format(ord(char), '08b')
            bits.extend([int(b) for b in bin_char])
        return bits

    def get_d20_ray_path(self, start_pos, direction_list, length):
        x0, y0, z0 = start_pos
        dx, dy, dz = direction_list[0], direction_list[1], direction_list[2]
        
        max_axis = max(abs(dx), abs(dy), abs(dz))
        if max_axis == 0: return []
        
        vx = dx / max_axis
        vy = dy / max_axis
        vz = dz / max_axis
        
        path = []
        for t in range(length):
            px = int(x0 + vx * t)
            py = int(y0 + vy * t)
            pz = int(z0 + vz * t)
            if 0 <= px < self.size and 0 <= py < self.size and 0 <= pz < self.size:
                path.append((px, py, pz))
            else: break
        return path

    def generate_d20_axis(self, alpha, beta, gamma):
        phi = (1.0 + math.sqrt(5.0)) / 2.0
        x, y, z = 1.0, 1.0 / phi, phi
        
        x1 = x
        y1 = y * math.cos(alpha) - z * math.sin(alpha)
        z1 = y * math.sin(alpha) + z * math.cos(alpha)
        
        x2 = x1 * math.cos(beta) + z1 * math.sin(beta)
        y2 = y1
        z2 = -x1 * math.sin(beta) + z1 * math.cos(beta)
        
        x3 = x2 * math.cos(gamma) - y2 * math.sin(gamma)
        y3 = x2 * math.sin(gamma) + y2 * math.cos(gamma)
        z3 = z2
        
        return [x3, y3, z3]

    def burn_in_fragment(self, target_bits, alpha, beta, gamma, start_pos):
        """Brennt ein einzelnes Fragment ein und gibt den belegten Pfad zurueck."""
        achse_liste = self.generate_d20_axis(alpha, beta, gamma)
        pfad = self.get_d20_ray_path(start_pos, achse_liste, len(target_bits))
        
        if len(pfad) < len(target_bits):
            return None # Kollision mit der Wand!
            
        for i, (x, y, z) in enumerate(pfad):
            self.matrix[x, y, z] = target_bits[i]
        return pfad

    def flood_remaining_matrix(self, path_protection_set):
        print(f"\n[Phase 2] Flute restliches Feld zur Saettigung der {self.size}^3 Matrix...")
        np.random.seed(self.seed)
        
        zufalls_rauschen = np.random.randint(0, 2, size=(self.size, self.size, self.size), dtype=np.uint8)
        
        mask = np.ones((self.size, self.size, self.size), dtype=bool)
        for (x, y, z) in path_protection_set:
            mask[x, y, z] = False
            
        self.matrix[mask] = zufalls_rauschen[mask]
        
        physische_bits = self.size ** 3
        gesetzte_einsen = np.sum(self.matrix == 1)
        print(f" -> Matrix-Saettigung abgeschlossen. Gesamtkapazitaet: {physische_bits:,} Bits.")

    def bits_to_text(self, bits):
        text = ""
        for i in range(0, len(bits), 8):
            byte_bits = bits[i:i+8]
            if len(byte_bits) < 8: break
            bin_str = "".join(map(str, byte_bits))
            text += chr(int(bin_str, 2))
        return text

# --- RUNNING ENGINE ---
if __name__ == "__main__":
    print("--- GAUSS GEODE™ FRAGMENTATION COMPILER ---")
    compiler = GaussGeodeCompiler(size=300, seed=1337)
    
    # Der verbotene EAV-Songtext!
    songtext = "BaBaBaBaBaBankueberfall"
    print(f"[System] Ziel-Text: '{songtext}' | Laenge: {len(songtext)} Zeichen.")
    
    # 1. PHASE 1: FRAGMENTIERUNG & EINBRENNEN
    # Wir teilen den Text in Stücke von max 8 Zeichen (64 Bits)
    haepchen_groesse = 8
    fragmente = [songtext[i:i+haepchen_groesse] for i in range(0, len(songtext), haepchen_groesse)]
    
    gesamter_geschuetzter_pfad = []
    shard_chain = []
    
    # Die KI verteilt die Fragmente an verschiedene Startpunkte im Raum
    # Um den PoC sauber zu halten, nutzen wir eine feste Schrittweite fuer die Startpunkte
    for idx, frag in enumerate(fragmente):
        bits = compiler.text_to_bits(frag)
        
        # Jedes Fragment bekommt eine eigene, leicht rotierte Achse und einen neuen Startpunkt!
        winkel = (1.987 + idx*0.1, 0.854 + idx*0.1, 4.528 + idx*0.1)
        start_koord = (50 + idx*40, 50 + idx*40, 50 + idx*40)
        
        pfad = compiler.burn_in_fragment(bits, *winkel, start_koord)
        
        if pfad is not None:
            gesamter_geschuetzter_pfad.extend(pfad)
            # Wir speichern die Shard-Metadaten fuer den Reader
            shard_chain.append({
                "WINKEL": winkel,
                "START": start_koord,
                "BITS_ANZAHL": len(bits),
                "PFAD": pfad # Wichtig fuer die fehlerfreie Verifikation
            })
            print(f" -> Fragment {idx} ('{frag}') erfolgreich eingebrannt (Start: {start_koord}).")
        else:
            print(f" ⚠️ Kollision bei Fragment {idx}!")

    # 2. PHASE 2: Den gesamten ungenutzten Raum der 27 Millionen Bits fluten!
    compiler.flood_remaining_matrix(gesamter_geschuetzter_pfad)
    
    # 3. VERIFIKATION (Das Lesegerät liest die Shard-Kette aus)
    print("\n[GAUSS-Scanner] Lade Gauss Shard™ Chain und setze Fragmente zusammen...")
    
    rekonstruierte_bits = []
    for idx, shard in enumerate(shard_chain):
        # Der Reader liest exakt die geschuetzten Spuren ab
        gelesene_bits = [int(compiler.matrix[x, y, z]) for x, y, z in shard["PFAD"]]
        rekonstruierte_bits.extend(gelesene_bits)
        
    finaler_text = compiler.bits_to_text(rekonstruierte_bits)
    print(f"🎉 KOMPLETTE REKONSTRUKTION AUS DEM RAUSCHEN: '{finaler_text}'")
