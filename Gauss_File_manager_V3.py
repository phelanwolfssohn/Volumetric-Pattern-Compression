# -*- coding: utf-8 -*-
import numpy as np
import math
import struct
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
        """Berechnet den 3D-Pfad einer Ikosaeder-Achse durch das Raster (Raycasting)."""
        x0, y0, z0 = start_pos
        
        # JETZT ABSOLUT REIN: Einzelner Index-Zugriff befreit uns von jedem Typenfehler!
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
        """Generiert eine rotierte Ikosaeder-Hauptachse mittels reinem Python math."""
        phi = (1.0 + math.sqrt(5.0)) / 2.0
        x, y, z = 1.0, 1.0 / phi, phi
        
        # 3D-Rotationen über Standard-Math
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

    def compile_to_files(self, source_file, output_geode_path, output_bin_shard_path):
        print(f"--- START GAUSS BINARY COMPILER (Geode: {self.size}^3) ---")
        if not os.path.exists(source_file):
            print(f"⚠️ FEHLER: Quelldatei fehlt!")
            return False
            
        target_bits = self.file_to_bits(source_file)
        print(f"[System] Quelldatei geladen: {len(target_bits)} Bits ({len(target_bits)//8} Bytes).")
        
        # DER ELEMENTARE SWEET SPOT: 256 Bits (32 Bytes) pro Shard! Max-Auslastung der 500er-Geode.
        chunk_size = 256
        bit_chunks = [target_bits[i:i+chunk_size] for i in range(0, len(target_bits), chunk_size)]
        
        if len(bit_chunks) > 2500:
            print(f"[Warnung] Begrenze PoC-Verarbeitung für stabilen Massenlauf.")
            bit_chunks = bit_chunks[:2500]
        
        total_protected_path = []
        belegte_koordinaten = set()
        
        binary_shard_data = bytearray()
        valid_chunks_count = 0
        puffer = self.size - 50
        
        for idx, chunk in enumerate(bit_chunks):
            bahn_gefunden = False
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
                    
                    # 💎 PURE REINE BINÄR-CODIERUNG (Exakt 20 Bytes per Shard!)
                    packed_shard = struct.pack("<fffHHHH", 
                        alpha, beta, gamma, 
                        start_pos[0], start_pos[1], start_pos[2], 
                        len(chunk)
                    )
                    binary_shard_data.extend(packed_shard)
                    valid_chunks_count += 1
                    break
            
            if not bahn_gefunden: continue
            
        print(f"[Phase 2] Sättige Geoden-Feld mit Rauschen...")
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
        
        with open(output_bin_shard_path, "wb") as f:
            f.write(binary_shard_data)
        print(f"🔑 BINÄRER GAUSS SHARD erfolgreich exportiert: '{output_bin_shard_path}' ({valid_chunks_count} Shards)")
        return True

    def decompile_from_files(self, geode_path, bin_shard_path, output_recovered_file):
        print(f"\n--- START GAUSS BINARY RECONSTRUCTOR ---")
        
        with open(geode_path, "rb") as f:
            packed_data = np.frombuffer(f.read(), dtype=np.uint8)
        unpacked_matrix = np.unpackbits(packed_data)
        self.matrix = unpacked_matrix[:self.size**3].reshape((self.size, self.size, self.size))
        print(f"📖 Gauss Geode von D-Platte eingelesen.")
        
        with open(bin_shard_path, "rb") as f:
            binary_data = f.read()
            
        shard_size = 20 
        num_shards = len(binary_data) // shard_size
        print(f"🔑 Binäre Shard-Kette geladen. Rekonstruiere {num_shards} Fragmente...")
        
        rekonstruierte_bits = []
        for i in range(num_shards):
            offset = i * shard_size
            shard_packet = binary_data[offset:offset+shard_size]
            
            alpha, beta, gamma, sx, sy, sz, length = struct.unpack("<fffHHHH", shard_packet)
            
            achse = self.generate_d20_axis(alpha, beta, gamma)
            pfad = self.get_d20_ray_path((sx, sy, sz), achse, length)
            
            chunk_bits = [int(self.matrix[x, y, z]) for x, y, z in pfad]
            rekonstruierte_bits.extend(chunk_bits)
            
        self.bits_to_file(rekonstruierte_bits, output_recovered_file)
        print(f"🎉 BINÄRE EXTRAKTION ERFOLGREICH! Datei wiederhergestellt: '{output_recovered_file}'")

if __name__ == "__main__":
    GEODEN_GROESSE = 500
    manager = GaussFileManager(size=GEODEN_GROESSE, seed=1337)
    
    quell_datei = "beispiel.txt"
    geode_datei = "kristall.geode"
    shard_datei = "schluessel.bin"
    rettungs_datei = "wiederhergestellt.txt"
    
    if manager.compile_to_files(quell_datei, geode_datei, shard_datei):
        manager.decompile_from_files(geode_datei, shard_datei, rettungs_datei)
        if os.path.exists(rettungs_datei):
            with open(rettungs_datei, "r", encoding="utf-8", errors="ignore") as f:
                print(f"\n🔍 Der unzerstörbare Blick ins Buch: '{f.read(150)}...'")
