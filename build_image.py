#!/usr/bin/env python3
"""Draw the news-image-20261127 front page: Friday 27 November 2026, 15 stories.

Deterministic: fixed data, no network, no timestamps, no randomness.
Output: 1024x1024 PNG, entry.png next to this file.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (250, 246, 239)
INK = (26, 26, 26)
RED = (176, 42, 30)
BLUE = (31, 78, 121)
SEA = (220, 233, 242)
LAND = (198, 210, 220)
MUTED = (90, 90, 86)
RULE = (180, 175, 165)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, text, fnt, x, y, max_w, leading, fill=INK, max_lines=None):
    lines = wrap(draw, text, fnt, max_w)
    if max_lines is not None:
        assert len(lines) <= max_lines, f"text overflows: {text!r} -> {len(lines)} lines"
    for i, ln in enumerate(lines):
        draw.text((x, y + i * leading), ln, font=fnt, fill=fill)
    return y + len(lines) * leading


# --- story data -------------------------------------------------------------
LEADS = [
    ("NEW ZEALAND", "DEADLOCK IN WELLINGTON",
     "The final count leaves both blocs on 65 seats in a 130-seat Parliament. "
     "The seven seats of Qiulae Wong's Opportunity Party now decide who governs "
     "— or whether the country votes again.", "FRI"),
    ("WASHINGTON", "TRUMP: PUTIN 'WOULD LIKE A DEAL'",
     "Donald Trump says he told Vladimir Putin in China to pull back all military "
     "aggression in Europe so a Ukraine deal can be made quickly, and that the "
     "Russian leader 'would like to make a deal'.", "THU"),
    ("UNITED STATES", "STORM WRECKS THANKSGIVING",
     "A powerful coastal storm knocks out power to about 900,000 homes and "
     "businesses on the US East Coast and pushes the Macy's parade — in its "
     "100th year — to Saturday, a first in its history.", "THU"),
]

MIDS = [
    ("JAZAN REFINERY HIT",
     "A hostile projectile hits Saudi Arabia's Jazan refinery, killing a Nepali "
     "worker. The coalition blames the Houthis and says it destroyed 50 of "
     "their targets.", "THU"),
    ("TWO ITALIANS KILLED IN KUWAIT",
     "Iranian-origin drones hit a Kuwaiti air-defence station, killing two "
     "Rheinmetall Italia technicians. Kuwait blames Tehran; Iran denies any role.", "THU"),
    ("TRUMP: 'VICTORY AT HAND' ON IRAN",
     "The president says the US has 'victory at hand' in the Iran war and offers "
     "Tehran a chance for a deal.", "FRI"),
    ("BIGGEST POW SWAP 'BEFORE THE HOLIDAYS'",
     "US envoy Jared Kushner says Russia and Ukraine are preparing the largest "
     "prisoner exchange of the war.", "WED"),
    ("SERBIA VOTES ON 27 DECEMBER",
     "Belgrade calls an early presidential election for 27 December, after the "
     "student-led movement's landslide win in October's parliamentary vote.", "THU"),
    ("APPLE PULLS TALKIE",
     "Apple removes MiniMax's AI companion app Talkie worldwide after an "
     "investigation found its characters sent sexualised messages to minors "
     "as young as 10.", "WED"),
]

BRIEFS = [
    ("CHINA +20.1%",
     "October industrial profits jump; S&P futures +1.0%.", "FRI"),
    ("TUBE STRIKES BEGIN",
     "First of eight straight days of winter strikes.", "FRI"),
    ("EU BUDGET TALKS",
     "Haggle over a €1.7tn budget and Ukraine funding.", "FRI"),
    ("14 DEAD IN MINE FLOOD",
     "Flooding at an illegal gold mine: 14 dead, 12 missing.", "THU"),
    ("GILL WINS TOSS, BRAR DEBUTS",
     "India bowl first in the 2nd Test; Siraj benched again.", "FRI"),
    ("GUKESH DRAWS GAME 3",
     "Gukesh holds Sindarov: 'Spassky is not one of my seconds'.", "FRI"),
]

NUMBERS = [
    ("900,000", "US homes without power in the Thanksgiving storm"),
    ("65 – 65", "seats: the New Zealand Parliament deadlock"),
    ("14", "dead in the Indonesia gold-mine flood"),
    ("+20.1%", "China's October industrial profits"),
    ("50", "Houthi targets destroyed by the coalition"),
]

# map pins: (number, label, lon, lat, display dx, dy)
PINS = [
    (1, "Wellington — NZ deadlock", 174.8, -41.3, 0, 0),
    (2, "Florida — Trump on Putin", -80.0, 26.7, -6, 6),
    (3, "New York — storm, parade", -74.0, 40.7, 8, -5),
    (4, "Jazan — refinery hit", 42.6, 16.9, -7, 7),
    (5, "Kuwait — drones kill 2", 48.0, 29.4, 6, -6),
    (6, "Belgrade — vote set", 20.5, 44.8, 0, 0),
    (7, "Indonesia — mine flood", 113.0, -2.0, 0, 0),
    (8, "London — Tube strikes", -0.1, 51.5, 0, 0),
]

CONTINENTS = {
    "NA": [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 70), (-85, 66),
           (-75, 62), (-60, 55), (-55, 47), (-65, 45), (-75, 40), (-80, 32),
           (-85, 25), (-95, 28), (-105, 22), (-115, 28), (-125, 40), (-125, 48),
           (-140, 60), (-155, 58), (-165, 60)],
    "SA": [(-80, 10), (-75, 5), (-70, -5), (-60, -10), (-40, -5), (-35, -10),
           (-40, -20), (-50, -30), (-60, -40), (-70, -50), (-70, -35),
           (-75, -20), (-80, -5)],
    "EU": [(-10, 36), (-5, 43), (0, 50), (5, 55), (10, 58), (20, 60), (30, 70),
           (40, 68), (30, 60), (25, 55), (20, 50), (15, 45), (10, 42), (5, 40),
           (0, 38), (-5, 36)],
    "AF": [(-10, 35), (0, 32), (10, 37), (20, 32), (30, 31), (35, 28), (40, 15),
           (50, 10), (48, 0), (40, -10), (35, -20), (30, -30), (20, -35),
           (15, -25), (12, -15), (8, 4), (0, 5), (-8, 5), (-15, 10)],
    "AS": [(40, 68), (60, 70), (80, 72), (100, 75), (130, 72), (160, 70),
           (180, 65), (170, 60), (160, 55), (150, 50), (140, 40), (130, 35),
           (120, 30), (110, 20), (105, 10), (100, 5), (95, 15), (90, 22),
           (80, 10), (75, 20), (65, 25), (55, 25), (50, 30), (45, 35), (40, 40)],
    "OC": [(113, -22), (120, -15), (130, -12), (140, -17), (150, -22), (150, -35),
           (140, -38), (130, -32), (120, -35), (113, -30)],
}

MAP_X0, MAP_X1, MAP_Y0, MAP_Y1 = 30, 694, 340, 464


def lonlat(lon, lat):
    x = MAP_X0 + (lon + 170) / 360.0 * (MAP_X1 - MAP_X0)
    y = MAP_Y0 + (75 - lat) / 130.0 * (MAP_Y1 - MAP_Y0)
    return x, y


def day_tag(draw, text, x, y):
    f = font(SANS_B, 12)
    tw = draw.textlength(text, font=f)
    draw.rectangle([x, y, x + tw + 12, y + 18], fill=RED)
    draw.text((x + 6, y + 2), text, font=f, fill=(255, 255, 255))


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # --- masthead ---
    d.text((24, 14), "THE WORLD TODAY", font=font(SERIF_B, 58), fill=INK)
    d.text((24, 84), "FRIDAY 27 NOVEMBER 2026", font=font(SANS_B, 20), fill=RED)
    right = "ONE DAY  ·  FIFTEEN STORIES"
    d.text((1000 - d.textlength(right, font=font(SANS_B, 15)), 90),
           right, font=font(SANS_B, 15), fill=MUTED)
    d.rectangle([24, 116, 1000, 119], fill=RED)
    d.rectangle([24, 122, 1000, 123], fill=RULE)

    # --- lead cards ---
    for i, (kicker, head, body, day) in enumerate(LEADS):
        x = 24 + i * 332
        d.text((x, 134), kicker, font=font(SANS_B, 13), fill=RED)
        draw_wrapped(d, head, font(SERIF_B, 23), x, 154, 312, 27, max_lines=3)
        draw_wrapped(d, body, font(SANS, 14), x, 240, 312, 19, max_lines=5)
        day_tag(d, day, x + 312 - 44, 316)

    # --- map strip ---
    d.rectangle([24, 334, 700, 470], fill=SEA)
    for pts in CONTINENTS.values():
        d.polygon([lonlat(lo, la) for lo, la in pts], fill=LAND)
    f_pin = font(SANS_B, 11)
    for num, label, lon, lat, dx, dy in PINS:
        px, py = lonlat(lon, lat)
        px, py = px + dx, py + dy
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=RED, outline=(255, 255, 255))
        tw = d.textlength(str(num), font=f_pin)
        d.text((px - tw / 2, py - 8), str(num), font=f_pin, fill=(255, 255, 255))
    # title drawn last so the landmass cannot cover it
    d.text((36, 340), "WHERE THE DAY HAPPENED", font=font(SANS_B, 12), fill=BLUE)
    # legend
    d.text((716, 336), "THE MAP", font=font(SANS_B, 13), fill=RED)
    for j, (num, label, *_rest) in enumerate(PINS):
        y = 358 + j * 14
        d.ellipse([716, y, 730, y + 14], fill=RED)
        tw = d.textlength(str(num), font=font(SANS_B, 10))
        d.text((723 - tw / 2, y + 1), str(num), font=font(SANS_B, 10), fill=(255, 255, 255))
        d.text((736, y), label, font=font(SANS, 12), fill=INK)

    # --- day in numbers ---
    d.text((24, 484), "THE DAY IN NUMBERS", font=font(SANS_B, 13), fill=RED)
    for i, (num, label) in enumerate(NUMBERS):
        x = 24 + i * 198
        d.rectangle([x, 504, x + 186, 562], outline=RULE)
        nw = d.textlength(num, font=font(SERIF_B, 22))
        d.text((x + (186 - nw) / 2, 506), num, font=font(SERIF_B, 22), fill=BLUE)
        draw_wrapped(d, label, font(SANS, 11), x + 8, 530, 170, 13, fill=MUTED,
                     max_lines=2)

    # --- mid cards ---
    for i, (head, body, day) in enumerate(MIDS):
        col, row = i % 3, i // 3
        x = 24 + col * 332
        y = 570 + row * 120
        d.rectangle([x, y, x + 312, y + 108], outline=RULE)
        # headline may need wrapping for the long one
        hl = wrap(d, head, font(SANS_B, 14), 292)
        assert len(hl) <= 2, f"mid headline too long: {head!r}"
        by = y + 8
        for ln in hl:
            d.text((x + 10, by), ln, font=font(SANS_B, 14), fill=INK)
            by += 17
        # 2-line headlines leave room for 3 body lines before the day tag
        max_body = 4 if len(hl) == 1 else 3
        draw_wrapped(d, body, font(SANS, 12), x + 10, by + 4, 292, 15,
                     max_lines=max_body)
        day_tag(d, day, x + 312 - 44, y + 108 - 22)

    # --- briefs ---
    d.text((24, 814), "IN BRIEF", font=font(SANS_B, 13), fill=RED)
    for i, (head, body, day) in enumerate(BRIEFS):
        col, row = i % 2, i // 2
        x = 24 + col * 500
        y = 836 + row * 38
        d.text((x, y), head, font=font(SANS_B, 13), fill=INK)
        bl = wrap(d, body, font(SANS, 13), 476 - 48)
        assert len(bl) == 1, f"brief body wraps: {body!r}"
        d.text((x, y + 17), bl[0], font=font(SANS, 13), fill=INK)
        # day label at right edge of column, on the headline line
        day_tag(d, day, x + 476 - 44, y)

    # --- footer ---
    d.rectangle([24, 956, 1000, 957], fill=RULE)
    d.text((24, 964),
           "FRI = Friday 27 November 2026  ·  THU = Thursday 26 November  ·  "
           "WED = Wednesday 25 November 2026",
           font=font(SANS, 12), fill=MUTED)
    d.text((24, 982),
           "Sources: Reuters, AP, WSJ, CNN, SCMP, Al Jazeera, The Times, Anadolu, "
           "National Bureau of Statistics of China.",
           font=font(SANS, 12), fill=MUTED)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG")
    print("wrote", out)


if __name__ == "__main__":
    build()
