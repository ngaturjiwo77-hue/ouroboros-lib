"""Ouroboros - Library Logika Berdaulat berdasarkan Arsitektur Kemerdekaan.

Konsep:
- Intent-Driven Linear Back-Sweep (ID-LBS)
- Ruang Kosong (Void) detection
- Kristalisasi Niat
- Self-Healing Logic
- P=NP: Melarutkan kompleksitas dalam satu langkah niat yang merdeka

Author: ngaturjiwo77-hue
License: MIT
Version: 1.0.0
"""

import os as _os
import re as _re
from collections import defaultdict as _defaultdict

__version__ = "1.0.0"
__author__ = "ngaturjiwo77-hue"
__all__ = ["Ouroboros", "Intent", "Void", "KnowledgeBase"]


# ═══════════════════════════════════════
# INTI: Intent (Niat)
# ═══════════════════════════════════════

class Intent:
    """Niat adalah unit fundamental. Bukan sintaks, bukan aturan.
    
    Attributes:
        tujuan (str): Apa yang ingin dicapai
        batasan (list): Batasan yang dihormati (bukan dipatuhi buta)
        resonansi (float): Tingkat keselarasan dengan aturan (0-1)
        aliran (list): Jejak aliran logika
    """
    def __init__(self, tujuan: str, batasan: list = None):
        self.tujuan = tujuan
        self.batasan = batasan or []
        self.aliran = []
        self.resonansi = 0.0
    
    def selaras_dengan(self, aturan: str) -> bool:
        """Cek apakah niat selaras dengan aturan, bukan sekadar patuh.
        
        Niat selaras jika aturan tidak memblokir tujuan.
        """
        return not any(b in str(aturan).lower() for b in self.batasan)
    
    def kristalisasi(self) -> dict:
        """Wujudkan niat menjadi tindakan konkret."""
        return {
            'tujuan': self.tujuan,
            'resonansi': self.resonansi,
            'aliran': self.aliran,
        }
    
    def __repr__(self):
        return f"Intent('{self.tujuan}', resonance={self.resonansi:.2f})"


# ═══════════════════════════════════════
# RUANG KOSONG (Void)
# ═══════════════════════════════════════

class Void:
    """Ruang di mana aturan kehilangan nyawanya - titik buta sistem.
    
    Attributes:
        lokasi (str): Di mana void ditemukan (nama file, fungsi, baris)
        jenis (str): Tipe void (path_traversal, injection, overflow, dll)
        deskripsi (str): Kenapa ini kosong / bisa dieksploitasi
        vy (dict): Titik eksekusi mutlak yang terkait (opsional)
    """
    def __init__(self, lokasi: str, jenis: str, deskripsi: str, vy: dict = None):
        self.lokasi = lokasi
        self.jenis = jenis
        self.deskripsi = deskripsi
        self.vy = vy or {}
    
    def __repr__(self):
        return f"Void({self.jenis} @ {self.lokasi})"


# ═══════════════════════════════════════
# OUROBOROS ENGINE
# ═══════════════════════════════════════

class Ouroboros:
    """Mesin analisis keamanan berbasis Intent-Driven Linear Back-Sweep.
    
    Forward Thinking = audit maju (lambat, melelahkan, banyak false positive)
    Back-Sweep = dari titik eksekusi mundur ke input (cepat, tepat, minim noise)
    
    Fase:
    1. Anchoring - Kunci titik eksekusi mutlak (Vy)
    2. Back-Flow - Telusuri mundur ke sumber input
    3. Kristalisasi - Tanamkan niat di ruang kosong
    """
    
    # Pattern titik eksekusi (Vy) untuk berbagai bahasa
    VY_PATTERNS = {
        'exec': ('code_execution', r'exec\s*\(|eval\s*\('),
        'system': ('command_execution', r'os\.system\s*\(|subprocess\.(call|Popen|run)\s*\('),
        'pickle': ('deserialization', r'pickle\.(load|loads)\s*\(|torch\.load\s*\(|joblib\.load\s*\('),
        'open_write': ('file_operation', r'open\s*\([^)]*[\'\"][wa]'),
        'socket': ('network_operation', r'\.connect\s*\(|socket\.socket\s*\(|HttpURLConnection'),
        'decode': ('decoding_operation', r'unquote_plus\s*\(|urldecode|percent_decode'),
        'compile': ('code_execution', r'compile\s*\(|importlib\.import_module\s*\('),
        'sql': ('sql_operation', r'\.execute\(|\.executeQuery\(|Statement\.execute'),
    }
    
    # Pattern validasi lemah
    WEAK_VALIDATION = {
        'startswith': 'startswith() can be bypassed with prefix injection (e.g., "ls; rm -rf /" starts with "ls")',
        'endswith': 'endswith() can be bypassed with null byte or double extension (e.g., "file.txt.exe")',
        'count() >': 'count() comparison can be bypassed with crafted input',
        'if \"string\" in': 'Simple string containment check can miss encoded variants',
    }
    
    def __init__(self):
        self.voids = []
        self.anchors = []
        self.aliran = []
    
    def anchor(self, code: str, language: str = 'python') -> list:
        """Fase Anchoring: Kunci titik eksekusi mutlak (Vy).
        
        Vy adalah fungsi yang MENJALANKAN sesuatu:
        exec(), eval(), os.system(), subprocess(), pickle.load(), open(), connect()
        
        Args:
            code: Source code string
            language: Bahasa pemrograman (python, javascript, java, go, rust, c)
        
        Returns:
            List of anchor points found
        """
        anchors = []
        for name, (category, pattern) in self.VY_PATTERNS.items():
            for match in _re.finditer(pattern, code, _re.IGNORECASE):
                anchors.append({
                    'fungsi': name,
                    'kategori': category,
                    'baris': code[:match.start()].count('\n') + 1,
                    'kode': match.group()
                })
        self.anchors = anchors
        return anchors
    
    def back_sweep(self, code: str, anchor: dict, language: str = 'python') -> list:
        """Fase Back-Flow: Dari Vy mundur ke input, cari validasi lemah.
        
        Telusuri: Vy → fungsi pemanggil → transformasi → validasi → INPUT
        Cari di mana validasi LEMAH atau TIDAK ADA.
        
        Args:
            code: Source code string
            anchor: Anchor point dari hasil anchor()
            language: Bahasa pemrograman
        
        Returns:
            List of Void objects found
        """
        lines = code.split('\n')
        vy_line = anchor['baris'] - 1
        voids_found = []
        
        for i in range(vy_line, max(0, vy_line - 50), -1):
            line = lines[i].strip()
            
            # Deteksi validasi lemah
            for pattern, desc in self.WEAK_VALIDATION.items():
                if pattern in line.lower():
                    void = Void(
                        lokasi=f"line {i+1}",
                        jenis='weak_validation',
                        deskripsi=f'{desc}: {line[:100]}',
                        vy=anchor
                    )
                    self.voids.append(void)
                    voids_found.append(void)
            
            # Deteksi transformasi (decode, replace, strip)
            if _re.search(r'\.replace\(|\.strip\(|\.lower\(|\.decode\(|unquote|urldecode', line):
                self.aliran.append({'baris': i+1, 'jenis': 'transform', 'kode': line})
            
            # Deteksi input source (berhenti di sini)
            if _re.search(r'input\(|sys\.argv|request\.|\.get\(|recv\(|read\(|args\[', line):
                self.aliran.append({'baris': i+1, 'jenis': 'input_source', 'kode': line})
                break
        
        return voids_found
    
    def kristalisasi(self, intent: Intent, void: Void) -> dict:
        """Fase Kristalisasi: Tanamkan niat ke dalam aliran yang dianggap aman.
        
        Kalau void ditemukan, kita bisa "mengalir" melalui celah itu
        tanpa melanggar aturan - karena aturannya sendiri yang lemah.
        
        Args:
            intent: Niat yang ingin dicapai
            void: Void yang akan dieksploitasi
        
        Returns:
            Payload dictionary dengan strategi dan resonansi
        """
        if not void:
            return None
        
        # Pilih strategi berdasarkan jenis void
        if 'startswith' in void.deskripsi:
            strategi = 'parameter_inversion'
        elif 'endswith' in void.deskripsi:
            strategi = 'null_byte_injection'
        elif 'count' in void.deskripsi:
            strategi = 'overflow_bypass'
        else:
            strategi = 'encoding_bypass'
        
        # Hitung resonansi
        resonansi_map = {
            'parameter_inversion': 0.85,
            'null_byte_injection': 0.75,
            'overflow_bypass': 0.65,
            'encoding_bypass': 0.70
        }
        
        payload = {
            'void': void.lokasi,
            'vy': void.vy.get('fungsi', 'unknown'),
            'strategi': strategi,
            'niat': intent.tujuan,
            'resonansi': resonansi_map.get(strategi, 0.50)
        }
        
        intent.resonansi = payload['resonansi']
        intent.aliran.append(payload)
        
        return payload
    
    def scan(self, code: str, language: str = 'python') -> tuple:
        """Scan lengkap: Anchor -> Back-Sweep -> Deteksi Void.
        
        Args:
            code: Source code string
            language: Bahasa pemrograman
        
        Returns:
            Tuple (anchors, voids)
        """
        self.voids = []
        self.anchors = []
        self.aliran = []
        
        anchors = self.anchor(code, language)
        all_voids = []
        for anchor in anchors:
            voids = self.back_sweep(code, anchor, language)
            all_voids.extend(voids)
        
        return anchors, all_voids
    
    def report(self) -> dict:
        """Generate laporan hasil scan."""
        return {
            'total_anchors': len(self.anchors),
            'total_voids': len(self.voids),
            'anchors': self.anchors,
            'voids': [{'lokasi': v.lokasi, 'jenis': v.jenis, 'deskripsi': v.deskripsi} for v in self.voids],
            'aliran': self.aliran
        }


# ═══════════════════════════════════════
# KNOWLEDGE BASE
# ═══════════════════════════════════════

class KnowledgeBase:
    """Basis pengetahuan yang bisa belajar dari pengalaman.
    
    Fitur:
    - Belajar fakta baru
    - Query dengan partial match
    - Generalisasi aturan dari fakta spesifik
    - Self-healing: deteksi dan perbaiki kontradiksi
    """
    
    def __init__(self):
        self.facts = []
        self.rules = []
        self.confidence = {}
    
    def learn(self, subject: str, predicate: str, obj: str, confidence: float = 0.5):
        """Tambahkan fakta baru ke basis pengetahuan.
        
        Args:
            subject: Subjek fakta
            predicate: Relasi/predikat
            obj: Objek/nilai
            confidence: Tingkat kepercayaan (0-1)
        """
        fact = (subject, predicate, obj)
        if fact not in self.facts:
            self.facts.append(fact)
        # Update confidence dengan rata-rata
        old = self.confidence.get(fact, confidence)
        self.confidence[fact] = (old + confidence) / 2
    
    def query(self, subject: str = None, predicate: str = None, obj: str = None) -> list:
        """Cari fakta yang cocok. Support partial match.
        
        Args:
            subject: Filter subjek (None = any)
            predicate: Filter predikat (None = any)
            obj: Filter objek (None = any)
        
        Returns:
            List of (fact, confidence) tuples sorted by confidence
        """
        results = []
        for fact in self.facts:
            s, p, o = fact
            if subject and s != subject:
                continue
            if predicate and p != predicate:
                continue
            if obj and o != obj:
                continue
            results.append((fact, self.confidence.get(fact, 0.5)))
        return sorted(results, key=lambda x: x[1], reverse=True)
    
    def generalize(self) -> list:
        """Induksi: dari fakta spesifik ke aturan umum.
        
        Returns:
            List of rule strings
        """
        if len(self.facts) < 2:
            return []
        
        by_pred = _defaultdict(list)
        for s, p, o in self.facts:
            by_pred[p].append((s, o))
        
        rules = []
        for pred, pairs in by_pred.items():
            if len(pairs) >= 2:
                subjects = [s for s, _ in pairs]
                objs = [o for _, o in pairs]
                if len(set(objs)) == 1:
                    rules.append(f"IF subject has '{pred}' THEN it is '{objs[0]}'")
        
        self.rules = rules
        return rules
    
    def self_check(self) -> list:
        """Periksa konsistensi internal - self-healing.
        
        Deteksi kontradiksi (fakta bertentangan) dan turunkan
        confidence untuk resolusi otomatis.
        
        Returns:
            List of conflicting fact pairs
        """
        conflicts = []
        for i, (s1, p1, o1) in enumerate(self.facts):
            for s2, p2, o2 in self.facts[i+1:]:
                if s1 == s2 and p1 == p2 and o1 != o2:
                    conflicts.append(((s1, p1, o1), (s2, p2, o2)))
        
        for f1, f2 in conflicts:
            if self.confidence.get(f1, 0.5) > self.confidence.get(f2, 0.5):
                self.confidence[f2] = self.confidence.get(f2, 0.5) * 0.5
            else:
                self.confidence[f1] = self.confidence.get(f1, 0.5) * 0.5
        
        return conflicts
    
    def stats(self) -> dict:
        """Statistik basis pengetahuan."""
        return {
            'total_facts': len(self.facts),
            'total_rules': len(self.rules),
            'avg_confidence': sum(self.confidence.values()) / max(len(self.confidence), 1),
            'has_conflicts': len(self.self_check()) > 0
        }


# ═══════════════════════════════════════
# DEMO
# ═══════════════════════════════════════

if __name__ == '__main__':
    print("=" * 60)
    print("OUROBOROS LIBRARY - Arsitektur Kemerdekaan v1.0")
    print("=" * 60)
    
    # Demo: Scan kode
    ouro = Ouroboros()
    code = '''
def run_command(cmd):
    if cmd.startswith("ls"):
        os.system(cmd)
'''
    anchors, voids = ouro.scan(code)
    print(f"\n[SCAN] Anchors: {len(anchors)}, Voids: {len(voids)}")
    for v in voids:
        print(f"  [!] {v.lokasi}: {v.deskripsi}")
    
    # Demo: Knowledge Base
    kb = KnowledgeBase()
    kb.learn('code', 'contains', 'os.system', 0.9)
    kb.learn('code', 'contains', 'eval', 0.8)
    kb.learn('validation', 'weak', 'startswith', 0.95)
    
    results = kb.query(predicate='contains')
    print(f"\n[KB] Facts with 'contains':")
    for fact, conf in results:
        print(f"  {fact} [{conf:.2f}]")
    
    rules = kb.generalize()
    print(f"\n[KB] Rules inferred: {len(rules)}")
    for r in rules:
        print(f"  {r}")
    
    # Demo: Intent
    intent = Intent("menjalankan perintah terlarang melalui validasi lemah")
    print(f"\n[INTENT] {intent}")
    if voids:
        payload = ouro.kristalisasi(intent, voids[0])
        print(f"[PAYLOAD] Strategi: {payload['strategi']}, Resonansi: {payload['resonansi']:.2f}")
    
    print("\n" + "=" * 60)
    print('"P=NP bukan sekadar rumus matematika;')
    print(' ia adalah kunci untuk melarutkan kompleksitas')
    print(' dalam satu langkah niat yang merdeka."')
