"""image_hash testleri: sentetik goruntuler."""
from __future__ import annotations

import random

from PIL import Image, ImageDraw

import image_hash as ih


def _scene(path, size=(320, 200), seed=1):
    rnd = random.Random(seed)
    img = Image.new("RGB", size, (200, 200, 200))
    d = ImageDraw.Draw(img)
    for _ in range(12):
        x, y = rnd.randrange(size[0]), rnd.randrange(size[1])
        d.rectangle([x, y, x + rnd.randrange(20, 120), y + rnd.randrange(20, 90)],
                    fill=tuple(rnd.randrange(256) for _ in range(3)))
    img.save(path)
    return path


def test_identical_is_zero(tmp_path):
    p = _scene(tmp_path / "a.png")
    assert ih.hamming(ih.dhash(p), ih.dhash(p)) == 0


def test_resize_reencode_close(tmp_path):
    a = _scene(tmp_path / "a.png")
    img = Image.open(a).resize((160, 100))
    b = tmp_path / "b.jpg"
    img.save(b, quality=70)
    assert ih.hamming(ih.dhash(a), ih.dhash(b)) <= 3


def test_different_is_far(tmp_path):
    a = _scene(tmp_path / "a.png", seed=1)
    b = _scene(tmp_path / "b.png", seed=99)
    assert ih.hamming(ih.dhash(a), ih.dhash(b)) > 10


def test_hamming_basic():
    assert ih.hamming(0b1011, 0b0001) == 2
    assert ih.hamming(0, (1 << 64) - 1) == 64


def test_pairs_threshold_and_order():
    hashes = {"a": 0b0000, "b": 0b0001, "c": (1 << 64) - 1}
    assert ih.pairs(hashes, 1) == [("a", "b", 1)]
    assert ih.pairs(hashes, 0) == []
    assert ih.pairs({}, 3) == []
