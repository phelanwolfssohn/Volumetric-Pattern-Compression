import numpy as np

# ==========================================
# 1. HARDWARE-SIMULATION & GEOMETRIE (MUSTER)
# ==========================================

def get_spiral_path_2d():
    """MUSTER 0x01: Definiert die 9 Schritte für eine linksdrehende Spirale von außen nach innen (3x3)."""
    return [
        (0,0), (1,0), (2,0),  # Linke Kante abwärts
        (2,1), (2,2),         # Untere Kante nach rechts
        (1,2), (0,2),         # Rechte Kante aufwärts
        (0,1),                # Oben Mitte
        (1,1)                 # ZENTRUM / ANKER
    ]

def get_zigzag_path_2d():
    """MUSTER 0x03: Klassischer Boustrophedon-Scan (Zickzack) für eine 3x3 Ebene."""
    return [
        (0,0), (0,1), (0,2),  # Erste Reihe links -> rechts
        (1,2), (1,1), (1,0),  # Zweite Reihe rechts -> links
        (2,0), (2,1), (2,2)   # Dritte Reihe links -> rechts
    ]

def scan_3d_cube(cube, muster_id=1):
    """
    Tastet den 27-Bit-Würfel auf allen 3 Raumachsen (X, Y, Z) ab.
    Wechselt dynamisch das Abtastmuster basierend auf der MUSTER_ID.
    """
    bit_stream = []
    
    # Pfad-Zuweisung anhand der Inode-Muster-ID
    if muster_id == 1:
        path_2d = get_spiral_path_2d()
    elif muster_id == 3:
        path_2d = get_zigzag_path_2d()
    else:
        raise ValueError(f"Unbekannte Muster-ID: {muster_id}")
    
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
# 2. ADAPTIVE KI-MUSTER-SUCHE
# ==========================================

def find_adaptive_ki_match(cube, needle_stream):
    """
    Das KI-Herzstück: Die KI testet mehrere Muster-IDs nacheinander,
    um die beste Übereinstimmung im Würfel-Schachbrett zu lokalisieren.
    """
    verfuegbare_muster = [1, 3] # Spirale (0x01) und Zickzack (0x03)
    needle_len = len(needle_stream)
    
    for m_id in verfuegbare_muster:
        # Generiere das virtuelle Schachbrett für das aktuelle Muster
        haystack_stream = scan_3d_cube(cube, muster_id=m_id)
        haystack_len = len(haystack_stream)
        
        # Durchsuche den resultierenden Datenstrom
        for i in range(haystack_len - needle_len + 1):
            if haystack_stream[i:i+needle_len] == needle_stream:
                # Match gefunden! Wir geben den erweiterten VOMCS-Pointer aus
                return {
                    "MUSTER_ID": m_id,
                    "START_BIT": i,
                    "LAENGE": needle_len
                }
    return None

# ==========================================
# 3. DER PROOF-OF-CONCEPT TESTLAUF
# ==========================================
if __name__ == "__main__":
    print("--- VOMCS ADAPTIVE PROOF OF CONCEPT LIVE TEST ---")
    
    # Schritt A: Wir initialisieren das Schachbrett (Datei 1)
    cube = np.zeros((3, 3, 3))
    cube[0, :, :] = 1        # Obere Ebene voller Einsen
    cube[1, 1, 1] = 1        # Der schwarze Würfel im exakten Zentrum (Marker)
    
    print("\n[Hardware] 27-Bit-Würfel erfolgreich geladen.")
    print(f"[Hardware] Zentraler Marker bei (1,1,1) ist: {int(cube[1,1,1])} (Schwarz)")
    
    # Schritt B: Zeige die zwei unterschiedlichen Welten desselben Würfels
    stream_spirale = scan_3d_cube(cube, muster_id=1)
    stream_zigzag  = scan_3d_cube(cube, muster_id=3)
    
    print("\n[VOMCS Matrix-Uminterpretierung]")
    print(" Dieselbe Hardware liefert je nach Inode-Muster völlig andere Streams:")
    print(f" -> Stream Muster 0x01 (Spirale): {''.join(map(str, stream_spirale))}")
    print(f" -> Stream Muster 0x03 (Zickzack):{''.join(map(str, stream_zigzag))}")
    
    # Schritt C: Die zweite Datei integrieren (KI-Musterabgleich über alle Geometrien)
    # Wir nehmen eine Kette, die NUR im Zickzack-Muster so existiert:
    zweite_datei = [1, 1, 1, 0, 0, 0, 1] 
    print(f"\n[KI] Versuche zweite Datei {zweite_datei} über adaptiven Muster-Match zu integrieren...")
    
    pointer = find_adaptive_ki_match(cube, zweite_datei)
    
    if pointer:
        print("\n🎉 MATCH GEFUNDEN! Die KI hat die Geometrie erfolgreich optimiert.")
        print("[Inode-Schicht] Folgender Pointer sichert den Zugriff:")
        print(f" -> VOMCS-Pointer: {pointer}")
        
        # Test-Rekonstruktion: Nutze das im Pointer hinterlegte Muster!
        rekonstruktions_schachbrett = scan_3d_cube(cube, muster_id=pointer["MUSTER_ID"])
        start = pointer["START_BIT"]
        ende = start + pointer["LAENGE"]
        rekonstruiert = rekonstruktions_schachbrett[start:ende]
        
        print(f"[Decoder] Erfolgreich über Muster_ID {pointer['MUSTER_ID']} rekonstruiert: {rekonstruiert}")
    else:
        print("\n[KI] Kein Match in den verfügbaren Geometrien gefunden.")
