"""Saf dHash yardimcilari (yalniz Pillow): yakin-kopya tespiti icin 64 bit algisal ozet."""
from __future__ import annotations

from itertools import combinations
from pathlib import Path
from typing import Hashable, Mapping

from PIL import Image

HASH_W, HASH_H = 8, 8  # 9x8 gri resim -> 8 satir x 8 karsilastirma = 64 bit


def dhash(path: Path | str) -> int:
    """Standart dHash: 9x8 gri, her satirda komsu piksel karsilastirmasi (sol > sag)."""
    with Image.open(path) as img:
        small = img.convert("L").resize((HASH_W + 1, HASH_H), Image.Resampling.LANCZOS)
        px = small.tobytes()
    value = 0
    for row in range(HASH_H):
        for col in range(HASH_W):
            left, right = px[row * (HASH_W + 1) + col], px[row * (HASH_W + 1) + col + 1]
            value = (value << 1) | (1 if left > right else 0)
    return value


def hamming(a: int, b: int) -> int:
    return (a ^ b).bit_count()


def pairs(hashes: Mapping[Hashable, int], threshold: int) -> list[tuple[Hashable, Hashable, int]]:
    """Hamming <= threshold olan (anahtar_a, anahtar_b, mesafe) uclulari; girdi sirasi korunur."""
    found = []
    for (ka, ha), (kb, hb) in combinations(hashes.items(), 2):
        distance = hamming(ha, hb)
        if distance <= threshold:
            found.append((ka, kb, distance))
    return found
