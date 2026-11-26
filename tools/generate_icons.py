#!/usr/bin/env python3
"""Генератор іконок теми Systema. Чистий stdlib, без сторонніх залежностей."""

import math
import os
import struct
import zlib

SS = 4

DENSITIES = {
    "drawable-mdpi": 48,
    "drawable-hdpi": 72,
    "drawable-xhdpi": 96,
    "drawable-xxhdpi": 144,
    "drawable-xxxhdpi": 192,
}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES_DIR = os.path.join(ROOT, "app", "src", "main", "res")

WHITE = (255, 255, 255)


def lerp(a, b, t):
    return (int(round(a[0] + (b[0] - a[0]) * t)),
            int(round(a[1] + (b[1] - a[1]) * t)),
            int(round(a[2] + (b[2] - a[2]) * t)))


class Canvas:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.px = [0.0] * (w * h * 4)

    def blend(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 4
            self.px[i] = float(c[0])
            self.px[i + 1] = float(c[1])
            self.px[i + 2] = float(c[2])
            self.px[i + 3] = 255.0


def _color_at(color, y):
    return color(y) if callable(color) else color


def fill_rounded_rect(cv, x0, y0, x1, y1, r, color):
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    hx, hy = (x1 - x0) / 2.0, (y1 - y0) / 2.0
    for y in range(max(0, int(math.floor(y0)) - 1), min(cv.h, int(math.ceil(y1)) + 2)):
        c = _color_at(color, y)
        for x in range(max(0, int(math.floor(x0)) - 1), min(cv.w, int(math.ceil(x1)) + 2)):
            qx = abs(x - cx) - (hx - r)
            qy = abs(y - cy) - (hy - r)
            if qx <= 0 and qy <= 0:
                dist = min(max(qx, qy), 0.0) - r
            else:
                dist = math.hypot(max(qx, 0.0), max(qy, 0.0)) - r
            if dist <= 0:
                cv.blend(x, y, c)


def fill_circle(cv, cx, cy, r, color):
    for y in range(max(0, int(cy - r) - 1), min(cv.h, int(cy + r) + 2)):
        for x in range(max(0, int(cx - r) - 1), min(cv.w, int(cx + r) + 2)):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                cv.blend(x, y, color)


def ring_circle(cv, cx, cy, r, t, color):
    r_in, r_out = r - t / 2.0, r + t / 2.0
    for y in range(max(0, int(cy - r_out) - 1), min(cv.h, int(cy + r_out) + 2)):
        for x in range(max(0, int(cx - r_out) - 1), min(cv.w, int(cx + r_out) + 2)):
            d = math.hypot(x - cx, y - cy)
            if r_in <= d <= r_out:
                cv.blend(x, y, color)


def fill_line(cv, x0, y0, x1, y1, t, color):
    dx, dy = x1 - x0, y1 - y0
    l2 = dx * dx + dy * dy
    pad = t / 2.0 + 1
    x_lo = max(0, int(min(x0, x1) - pad))
    x_hi = min(cv.w, int(max(x0, x1) + pad) + 2)
    y_lo = max(0, int(min(y0, y1) - pad))
    y_hi = min(cv.h, int(max(y0, y1) + pad) + 2)
    for y in range(y_lo, y_hi):
        for x in range(x_lo, x_hi):
            tt = 0.0 if l2 == 0 else max(0.0, min(1.0, ((x - x0) * dx + (y - y0) * dy) / l2))
            px, py = x0 + tt * dx, y0 + tt * dy
            if (x - px) ** 2 + (y - py) ** 2 <= (t / 2.0) ** 2:
                cv.blend(x, y, color)


def fill_poly(cv, pts, color):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x_lo = max(0, int(min(xs)))
    x_hi = min(cv.w, int(max(xs)) + 2)
    y_lo = max(0, int(min(ys)))
    y_hi = min(cv.h, int(max(ys)) + 2)
    n = len(pts)
    for y in range(y_lo, y_hi):
        yc = y + 0.5
        cross = []
        for i in range(n):
            xa, ya = pts[i]
            xb, yb = pts[(i + 1) % n]
            if (ya <= yc < yb) or (yb <= yc < ya):
                cross.append(xa + (yc - ya) * (xb - xa) / (yb - ya))
        cross.sort()
        for k in range(0, len(cross) - 1, 2):
            for x in range(max(x_lo, int(cross[k])), min(x_hi, int(cross[k + 1]) + 1)):
                cv.blend(x, y, color)


def glyph_dialer(cv, s, bg):
    c = s / 2.0
    fill_rounded_rect(cv, 0.36 * s, 0.24 * s, 0.64 * s, 0.76 * s, 0.07 * s, WHITE)
    fill_rounded_rect(cv, 0.36 * s + 0.05 * s, 0.24 * s + 0.05 * s,
                      0.64 * s - 0.05 * s, 0.76 * s - 0.05 * s, 0.03 * s, bg)
    fill_rounded_rect(cv, c - 0.08 * s, 0.66 * s, c + 0.08 * s, 0.71 * s, 0.02 * s, WHITE)


def glyph_messages(cv, s, bg):
    fill_rounded_rect(cv, 0.24 * s, 0.26 * s, 0.76 * s, 0.66 * s, 0.14 * s, WHITE)
    fill_poly(cv, [(0.30 * s, 0.62 * s), (0.46 * s, 0.62 * s), (0.30 * s, 0.80 * s)], WHITE)


def glyph_camera(cv, s, bg):
    c = s / 2.0
    ring_circle(cv, c, c, 0.26 * s, 0.07 * s, WHITE)
    fill_circle(cv, c, c, 0.085 * s, WHITE)


def glyph_browser(cv, s, bg):
    c = s / 2.0
    ring_circle(cv, c, c, 0.27 * s, 0.055 * s, WHITE)
    fill_line(cv, c - 0.27 * s, c, c + 0.27 * s, c, 0.045 * s, WHITE)
    fill_line(cv, c, c - 0.27 * s, c, c + 0.27 * s, 0.045 * s, WHITE)


def glyph_settings(cv, s, bg):
    for y, kx in ((0.32, 0.60), (0.50, 0.38), (0.68, 0.55)):
        fill_line(cv, 0.26 * s, y * s, 0.74 * s, y * s, 0.05 * s, WHITE)
        fill_circle(cv, kx * s, y * s, 0.085 * s, WHITE)


def glyph_gallery(cv, s, bg):
    q = 0.20 * s
    for cx, cy in ((0.35, 0.35), (0.65, 0.35), (0.35, 0.65)):
        fill_rounded_rect(cv, (cx - 0.5 * q / s) * s, (cy - 0.5 * q / s) * s,
                          (cx + 0.5 * q / s) * s, (cy + 0.5 * q / s) * s, 0.05 * s, WHITE)
    c = 0.65
    fill_poly(cv, [(c * s, (c - 0.14) * s), ((c + 0.14) * s, c * s),
                   (c * s, (c + 0.14) * s), ((c - 0.14) * s, c * s)], WHITE)


def glyph_mail(cv, s, bg):
    fill_rounded_rect(cv, 0.26 * s, 0.32 * s, 0.74 * s, 0.68 * s, 0.06 * s, WHITE)
    fill_rounded_rect(cv, 0.26 * s + 0.05 * s, 0.32 * s + 0.05 * s,
                      0.74 * s - 0.05 * s, 0.68 * s - 0.05 * s, 0.02 * s, bg)
    fill_line(cv, 0.27 * s, 0.34 * s, 0.50 * s, 0.53 * s, 0.045 * s, WHITE)
    fill_line(cv, 0.73 * s, 0.34 * s, 0.50 * s, 0.53 * s, 0.045 * s, WHITE)


def glyph_clock(cv, s, bg):
    c = s / 2.0
    ring_circle(cv, c, c, 0.27 * s, 0.055 * s, WHITE)
    fill_line(cv, c, c, c, c - 0.16 * s, 0.05 * s, WHITE)
    fill_line(cv, c, c, c + 0.13 * s, c + 0.04 * s, 0.05 * s, WHITE)


def glyph_store(cv, s, bg):
    c = s / 2.0
    fill_rounded_rect(cv, 0.30 * s, 0.38 * s, 0.70 * s, 0.72 * s, 0.05 * s, WHITE)
    fill_rounded_rect(cv, 0.30 * s + 0.05 * s, 0.38 * s + 0.05 * s,
                      0.70 * s - 0.05 * s, 0.72 * s - 0.05 * s, 0.02 * s, bg)
    ring_circle(cv, c, 0.42 * s, 0.10 * s, 0.045 * s, WHITE)
    fill_rounded_rect(cv, c - 0.10 * s, 0.42 * s, c + 0.10 * s, 0.55 * s, 0.0, bg)


def glyph_launcher(cv, s, bg):
    c = s / 2.0
    fill_poly(cv, [(c, 0.28 * s), (0.72 * s, c), (c, 0.72 * s), (0.28 * s, c)], WHITE)


ICONS = [
    ("ic_dialer", (52, 168, 83), (27, 94, 32), glyph_dialer),
    ("ic_messages", (66, 133, 244), (21, 77, 180), glyph_messages),
    ("ic_camera", (96, 125, 139), (55, 71, 79), glyph_camera),
    ("ic_browser", (92, 107, 192), (48, 63, 159), glyph_browser),
    ("ic_settings", (120, 144, 156), (69, 90, 100), glyph_settings),
    ("ic_gallery", (236, 64, 122), (173, 20, 87), glyph_gallery),
    ("ic_mail", (239, 83, 80), (198, 40, 40), glyph_mail),
    ("ic_clock", (80, 80, 88), (30, 30, 36), glyph_clock),
    ("ic_store", (41, 182, 246), (2, 119, 189), glyph_store),
    ("ic_launcher", (99, 102, 241), (67, 56, 202), glyph_launcher),
]


def render_icon(name, top, bottom, glyph, size):
    s = size * SS
    cv = Canvas(s, s)

    def bg(y):
        return lerp(top, bottom, y / float(s))

    fill_rounded_rect(cv, 0, 0, s, s, 0.22 * s, bg)
    glyph(cv, s, bg)

    w = h = size
    out = bytearray()
    for y in range(h):
        for x in range(w):
            acc = [0.0, 0.0, 0.0, 0.0]
            for sy in range(SS):
                base = ((y * SS + sy) * s + x * SS) * 4
                for sx in range(SS):
                    i = base + sx * 4
                    acc[0] += cv.px[i]
                    acc[1] += cv.px[i + 1]
                    acc[2] += cv.px[i + 2]
                    acc[3] += cv.px[i + 3]
            n = float(SS * SS)
            out += bytes((int(round(acc[0] / n)), int(round(acc[1] / n)),
                          int(round(acc[2] / n)), int(round(acc[3] / n))))
    return w, h, bytes(out)


def write_png(path, w, h, rgba):
    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    raw = bytearray()
    stride = w * 4
    for y in range(h):
        raw.append(0)
        raw += rgba[y * stride:(y + 1) * stride]
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


def paste(dst, src, w, h, dx, dy):
    for y in range(h):
        for x in range(w):
            si = (y * w + x) * 4
            di = ((dy + y) * dst.w + dx + x) * 4
            a = src[si + 3] / 255.0
            for k in range(3):
                dst.px[di + k] = src[si + k] * a + dst.px[di + k] * (1 - a)
            dst.px[di + 3] = 255.0


def main():
    for folder, size in DENSITIES.items():
        out_dir = os.path.join(RES_DIR, folder)
        os.makedirs(out_dir, exist_ok=True)
        for name, top, bottom, glyph in ICONS:
            w, h, rgba = render_icon(name, top, bottom, glyph, size)
            write_png(os.path.join(out_dir, name + ".png"), w, h, rgba)
            print("wrote %s/%s.png (%dx%d)" % (folder, name, w, h))

    cell, pad, cols = 128, 16, 5
    rows = (len(ICONS) + cols - 1) // cols
    prev = Canvas(cols * cell + (cols + 1) * pad, rows * cell + (rows + 1) * pad)
    for y in range(prev.h):
        for x in range(prev.w):
            i = (y * prev.w + x) * 4
            prev.px[i:i + 4] = [24.0, 26.0, 32.0, 255.0]
    for idx, (name, top, bottom, glyph) in enumerate(ICONS):
        w, h, rgba = render_icon(name, top, bottom, glyph, cell)
        r, c = divmod(idx, cols)
        paste(prev, rgba, w, h, pad + c * (cell + pad), pad + r * (cell + pad))
    out = bytearray()
    for y in range(prev.h):
        for x in range(prev.w):
            i = (y * prev.w + x) * 4
            out += bytes((int(prev.px[i]), int(prev.px[i + 1]),
                          int(prev.px[i + 2]), int(prev.px[i + 3])))
    write_png(os.path.join(ROOT, "preview.png"), prev.w, prev.h, bytes(out))
    print("wrote preview.png")


if __name__ == "__main__":
    main()
