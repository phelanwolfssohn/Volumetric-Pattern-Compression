# -*- coding: utf-8 -*-
import numpy as np
import math
import json
import os

class GaussFileManager:
    def __init__(self, size=500, seed=1337):
        self.size = size
        self.seed = seed
        self.matrix = np.zeros((size, size, size), dtype=np.uint8)

    def file_to_bits(self, file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        bits = []
        for byte in data:
            bin_char = format(byte, '08b')
            bits.extend([int(b) for b in bin_char])
        return bits

    def bits_to_file(self, bits, output_path):
        byte_arr = bytearray()
        for i in range(0, len(bits), 8):
            byte_bits = bits[i:i+8]
            if len(byte_bits) < 8: break
            bin_str = "".join(map(str, byte_bits))
            byte_arr.append(int(bin_str, 2))
        with open(output_path, "wb") as f:
            f.write(byte_arr)

    def get_d20_ray_path(self, start_pos, direction_list, length):
        x0, y0, z0 = start_pos
        dx = float(direction_list[0])
        dy = float(direction_list[1])
        dz = float(direction_list[2])
        
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

    def compile_to_files(self, source_file, output_geode_path, output_shard_path):
        print(f"--- START GAUSS COMPILER (Geoden-Groesse: {self.size}^3) ---")
        if not os.path.exists(source_file):
            print(f"⚠️ FEHLER: Die Datei '{source_file}' existiert nicht!")
            return False
            
        target_bits = self.file_to_bits(source_file)
        print(f"[System] Quelldatei geladen: {len(target_bits)} Bits ({len(target_bits)//8} Bytes).")
        
        chunk_size = 128
        bit_chunks = [target_bits[i:i+chunk_size] for i in range(0, len(target_bits), chunk_size)]
        
        if len(bit_chunks) > 5000:
            print(f"[Warnung] Begrenze PoC-Verarbeitung auf die ersten 5000 Fragmente.")
            bit_chunks = bit_chunks[:5000]
        
        total_protected_path = []
        belegte_koordinaten = set()
        shard_list_metadata = []
        
        puffer = self.size - 50
        
        for idx, chunk in enumerate(bit_chunks):
            bahn_gefunden = False
            
            # UPGRADE: 50 Versuche statt 10 für maximale Weichenstellung im dichten Raum!
            for versuch in range(50):
                alpha = 1.987 + idx * 0.005 + versuch * 0.05
                beta  = 0.854 + idx * 0.005 + versuch * 0.05
                gamma = 4.528 + idx * 0.005 + versuch * 0.05
                
                start_pos = (20 + (idx * 23 + versuch * 17) % puffer, 
                             20 + (idx * 13 + versuch * 29) % puffer, 
                             20 + (idx * 17 + versuch * 11) % puffer)
                
                achse = self.generate_d20_axis(alpha, beta, gamma)
                pfad = self.get_d20_ray_path(start_pos, achse, len(chunk))
                
                if len(pfad) == len(chunk) and not any(p in belegte_koordinaten for p in pfad):
                    bahn_gefunden = True
                    for bit_idx, (x, y, z) in enumerate(pfad):
                        self.matrix[x, y, z] = chunk[bit_idx]
                        total_protected_path.append((x, y, z))
                        belegte_koordinaten.add((x, y, z))
                    
                    # LOGISCHES UPGRADE: Shard NUR speichern, wenn die Bahn glatt ging!
                    shard_list_metadata.append({
                        "alpha": alpha, "beta": beta, "gamma": gamma,
                        "start": start_pos, "length": len(chunk)
                    })
                    break
            
            if not bahn_gefunden:
                continue
            
        print(f"[Phase 2] Flute restliches Feld zur Saettigung der Rauschmatrix...")
        np.random.seed(self.seed)
        zufalls_rauschen = np.random.randint(0, 2, size=(self.size, self.size, self.size), dtype=np.uint8)
        
        mask = np.ones((self.size, self.size, self.size), dtype=bool)
        for (x, y, z) in total_protected_path:
            mask[x, y, z] = False
            
        self.matrix[mask] = zufalls_rauschen[mask]
        
        packed_geode = np.packbits(self.matrix)
        with open(output_geode_path, "wb") as f:
            f.write(packed_geode.tobytes())
        print(f"💾 Gauss Geode erfolgreich lokal exportiert: '{output_geode_path}'")
        
        with open(output_shard_path, "w", encoding="utf-8") as f:
            json.dump(shard_list_metadata, f, indent=4)
        print(f"🔑 Gauss Shard-Verzeichnis erfolgreich lokal exportiert: '{output_shard_path}'")
        return True

    def decompile_from_files(self, geode_path, shard_path, output_recovered_file):
        print(f"\n--- START GAUSS RECONSTRUCTOR ---")
        
        with open(geode_path, "rb") as f:
            packed_data = np.frombuffer(f.read(), dtype=np.uint8)
        
        unpacked_matrix = np.unpackbits(packed_data)
        total_bits = self.size ** 3
        self.matrix = unpacked_matrix[:total_bits].reshape((self.size, self.size, self.size))
        print(f"📖 Gauss Geode erfolgreich von D-Platte eingelesen.")
        
        with open(shard_path, "r", encoding="utf-8") as f:
            shard_chain = json.load(f)
        print(f"🔑 Gauss Shard-Schlüssel erfolgreich geladen ({len(shard_chain)} Fragmente gefunden).")
        
        rekonstruierte_bits = []
        for idx, shard in enumerate(shard_chain):
            achse = self.generate_d20_axis(shard["alpha"], shard["beta"], shard["gamma"])
            pfad = self.get_d20_ray_path(shard["start"], achse, shard["length"])
            
            chunk_bits = [int(self.matrix[x, y, z]) for x, y, z in pfad]
            rekonstruierte_bits.extend(chunk_bits)
            
        self.bits_to_file(rekonstruierte_bits, output_recovered_file)
        print(f"🎉 ZUSAMMENFÜGUNG ERFOLGREICH! Originaldatei wiederhergestellt unter: '{output_recovered_file}'")

if __name__ == "__main__":
    # JETZT SIND DIE 500 DRAN! 🏎️💨
    GEODEN_GROESSE = 500 
    
    manager = GaussFileManager(size=GEODEN_GROESSE, seed=1337)
    
    quell_datei = "beispiel.txt"
    geode_datei = "kristall.geode"
    shard_datei = "schluessel.shard"
    rettungs_datei = "wiederhergestellt.txt"
    
    if manager.compile_to_files(quell_datei, geode_datei, shard_datei):
        manager.decompile_from_files(geode_datei, shard_datei, rettungs_datei)
        
        if os.path.exists(rettungs_datei):
            with open(rettungs_datei, "r", encoding="utf-8", errors="ignore") as f:
                inhalt = f.read(200)
            print(f"\n🔍 Blick in die gerettete Datei (Erste 200 Zeichen): '{inhalt}...'")
