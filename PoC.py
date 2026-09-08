import numpy as np

# ==========================================
# 1. HARDWARE-SIMULATION & GEOMETRIE (MUSTER)
# ==========================================

def get_spiral_path_2d():
    """Definiert die 9 Schritte für eine linksdrehende Spirale von außen nach innen (3x3)."""
    return [
        (0,0), (1,0), (2,0),  # Linke Kante abwärts
        (2,1), (2,2),         # Untere Kante nach rechts
        (1,2), (0,2),         # Rechte Kante aufwärts
        (0,1),                # Oben Mitte
        (1,1)                 # ZENTRUM / ANKER
    ]

def scan_3d_cube(cube):
    """
    Tastet den 27-Bit-Würfel auf allen 3 Achsen (X, Y, Z) mit der Spirale ab.
    Erzeugt die von dir berechnete Kette von 81 Bits.
    """
    bit_stream = []
    path_2d = get_spiral_path_2d()
    
    # Achse 1: Scanne Scheiben entlang der X-Achse
    for x in range(3):
        for y, z in path_2d:
            bit_stream.append(int(cube[x, y, z]))
            
    # Achse 2: Scanne Scheiben entlang der Y-Achse
    for y in range(3):
        for x, z in path_2d:
            bit_stream.append(int(cube[x, y, z]))
            
    # Achse 3: Scanne Scheiben entlang der Z-Achse
    for z in range(3):
        for x, y in path_2d:
            bit_stream.append(int(cube[x, y, z]))
            
    return bit_stream

# ==========================================
# 2. KI-MUSTER-SUCHE (KOMPRESSION / INDEX)
# ==========================================

def find_ki_match(haystack_stream, needle_stream):
    """
    Simuliert die KI: Sucht nach übereinstimmenden Bitsequenzen (needle)
    im generierten 3D-Schachbrett-Stream (haystack).
    Gibt den Pointer [Muster_ID, Start-Bit, Länge] zurück.
    """
    needle_len = len(needle_stream)
    haystack_len = len(haystack_stream)
    
    # Die KI durchsucht den Stream des Schachbretts
    for i in range(haystack_len - needle_len + 1):
        if haystack_stream[i:i+needle_len] == needle_stream:
            # Match gefunden! Wir nutzen Muster_ID 1 für unsere Spirale
            pointer = {
                "MUSTER_ID": 1,
                "START_BIT": i,
                "LAENGE": needle_len
            }
            return pointer
    return None

# ==========================================
# 3. DER PROOF-OF-CONCEPT TESTLAUF
# ==========================================
if __name__ == "__main__":
    print("--- VOMCS PROOF OF CONCEPT LIVE TEST ---")
    
    # Schritt A: Wir initialisieren das Schachbrett (Datei 1)
    # 27-Bit-Würfel: Oben (Ebene 0) alle 1, Mitte alle 0 (außer Zentrum), Unten alle 0
    cube = np.zeros((3, 3, 3))
    cube[0, :, :] = 1        # Obere Ebene voller Einsen
    cube[1, 1, 1] = 1        # Der schwarze Würfel im exakten Zentrum (Marker)
    
    print("\n[Hardware] 27-Bit-Würfel erfolgreich geladen.")
    print(f"[Hardware] Zentraler Marker bei (1,1,1) ist: {int(cube[1,1,1])} (Schwarz)")
    
    # Schritt B: Datenstrom über deine Spirale extrahieren
    gesamter_datenstrom = scan_3d_cube(cube)
    print(f"\n[Scanner] 3-Achsen-Musterscan abgeschlossen.")
    print(f"[Scanner] Generierte Bit-Kette ({len(gesamter_datenstrom)} Bits):")
    print("".join(map(str, gesamter_datenstrom)))
    
    # Byte-Berechnung nach unserer Korrektur: 81 Bits = 10 Bytes + 1 Bit Rest
    bytes_anzahl = len(gesamter_datenstrom) // 8
    rest_bits = len(gesamter_datenstrom) % 8
    print(f"[Logik] Entspricht exakt: {bytes_anzahl} Bytes und {rest_bits} Bit.")
    
    # Schritt C: Die zweite, kleinere Datei integrieren (KI-Musterabgleich)
    # Nehmen wir an, Datei 2 ist die Bit-Kette für ein Sonderzeichen oder Kommando: [0, 0, 0, 0, 1]
    zweite_datei = [0, 0, 0, 0, 1]
    print(f"\n[KI] Versuche zweite Datei {zweite_datei} ohne physischen Speicherplatz zu integrieren...")
    
    pointer = find_ki_match(gesamter_datenstrom, zweite_datei)
    
    if pointer:
        print("\n🎉 MATCH GEFUNDEN! Die KI hat das Muster im Schachbrett lokalisiert.")
        print("[Inode-Schicht] Folgender Pointer wird extern/im Index abgelegt:")
        print(f" -> VOMCS-Pointer: {pointer}")
        
        # Test-Rekonstruktion aus dem Pointer
        start = pointer["START_BIT"]
        ende = start + pointer["LAENGE"]
        rekonstruiert = gesamter_datenstrom[start:ende]
        print(f"[Decoder] Datei erfolgreich über Pointer rekonstruiert: {rekonstruiert}")
    else:
        print("\n[KI] Kein Match gefunden. (Muster muss erweitert oder Original-Bitstrom angepasst werden).")
