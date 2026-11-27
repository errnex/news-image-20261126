#!/usr/bin/env python3
"""Draw Thursday 26 November 2026's world news as one 1024x1024 front page.

Broadsheet style: cream paper, navy masthead, 13 illustrated lead stories,
a world map with numbered pins, the 30 remaining stories, a UTC timeline,
region counts, numbers strip and a date check. All pictures are drawn in
code with PIL (geometric shapes only, no photos). Deterministic: no random
numbers, no timestamps, no network.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 16
CW = W - 2 * MARGIN  # 992

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")

NAVY = (27, 42, 74)
NAVY_D = (18, 30, 56)
RED = (164, 31, 31)
CREAM = (250, 246, 232)
PAPER = (253, 250, 240)
INK = (32, 32, 32)
GRAY = (100, 100, 100)
LINE = (200, 192, 172)
GOLD = (212, 175, 55)
GREEN = (30, 125, 50)
GREEN_BG = (223, 240, 226)
BLUE = (21, 101, 192)
BLUE_BG = (221, 234, 247)
CLAIM_BG = (251, 227, 227)
SEA = (207, 224, 232)
LAND = (183, 200, 163)
LAND_EDGE = (143, 163, 124)


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if fnt.getlength(t) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(d, x, y, lines, fnt, fill, leading):
    for i, ln in enumerate(lines):
        d.text((x, y + i * leading), ln, font=fnt, fill=fill)
    return y + len(lines) * leading


def badge(d, x_right, y, label):
    """Small coloured badge chip, right-aligned at x_right. Returns left x."""
    if label == "OFFICIAL":
        bg, fg = GREEN, (255, 255, 255)
    elif label == "REPORTED":
        bg, fg = BLUE, (255, 255, 255)
    else:
        bg, fg = RED, (255, 255, 255)
    fnt = font(SANS_B, 8)
    tw = fnt.getlength(label)
    bw, bh = int(tw) + 8, 12
    d.rounded_rectangle([x_right - bw, y, x_right, y + bh], radius=3, fill=bg)
    d.text((x_right - bw + 4, y + 1), label, font=fnt, fill=fg)
    return x_right - bw


# ---------------------------------------------------------------- leads
# (number, kicker, headline, body, source, badge, illustration key)
LEADS = [
    (1, "EUROPE · UKRAINE LOAN", "EU splits over $49bn Ukraine loan",
     "Leaders divide over budget spending and a $49bn loan to Kyiv as the summit strains.",
     "WSB", "REPORTED", "eu"),
    (2, "NORTH AMERICA · PARADE", "Macy's 100th parade postponed by storm",
     "First postponement in 100 years; the parade moves to Saturday 28 November.",
     "Macy's", "OFFICIAL", "parade"),
    (3, "EAST ASIA · CHESS", "Gukesh–Sindarov Game 3 drawn in 60 moves",
     "Berlin thriller in Geneva; Sindarov makes move 40 with seconds left; level at 1.5–1.5.",
     "Chess.com", "OFFICIAL", "chess"),
    (4, "MIDDLE EAST · GAZA", "Israeli strikes kill 10 in Gaza",
     "Overnight strikes kill 10 across Gaza.", "WSB", "REPORTED", "blast"),
    (5, "MIDDLE EAST · KUWAIT", "Iranian drones kill 2 Italians in Kuwait",
     "Two technicians are killed; Italy and Kuwait blame Iran, which denies any role.",
     "WSB", "REPORTED", "drone"),
    (6, "SOUTH ASIA · MUMBAI", "India marks 18 years since 26/11",
     "Tributes at the Taj hotel in Mumbai and the French Embassy in New Delhi, 18 years on.",
     "WebIndia123", "OFFICIAL", "taj"),
    (7, "AFRICA · CAIRO", "Cairo tanker blast kills 31",
     "Tanker explodes on Giza's Ring Road, charring 27 vehicles; driver held, doing 110 km/h.",
     "AP", "OFFICIAL", "tanker"),
    (8, "EUROPE · ECB", "Spain's Hernandez de Cos to lead the ECB",
     "Eurozone leaders pick the ex-Spanish central bank chief to succeed Christine Lagarde.",
     "Reuters", "OFFICIAL", "euro"),
    (9, "EAST ASIA · KOREA", "Kim vows more nuclear weapons",
     "North Korea's leader pledges a bigger arsenal after ignoring Trump's overture.",
     "WSB", "REPORTED", "missile"),
    (10, "SOUTHEAST ASIA · BOGOR", "Bogor mine flood kills 13, 13 missing",
     "An illegal gold mine floods 100m underground after heavy rain; 13 dead, 13 missing.",
     "World Now", "OFFICIAL", "mine"),
    (11, "MIDDLE EAST · TANKER", "Iran claims supertanker hit by mine",
     "IRGC: tanker with 2m barrels hit near Khasab; Britain reports a blast west of Dubai.",
     "World Now", "CLAIM", "ship"),
    (12, "AFRICA · CONGO", "Congo Ebola cases pass 12,000",
     "The second-largest outbreak on record; violence forces some responders to evacuate.",
     "WSB", "OFFICIAL", "virus"),
    (13, "EUROPE · KYIV", "Russian missiles hit Kyiv mall, 7 hurt",
     "Desnianskyi mall struck as 113 drones launch overnight; grain ships hit near Odesa.",
     "World Now", "REPORTED", "mall"),
]

TAIL = [
    (14, "Mexico blasts the DEA over tip lines; says it does too little on fentanyl inside the US.", "REPORTED"),
    (15, "Brazil condemns US 10% tariff on Embraer jets and higher sugar duties; calls plan unacceptable.", "REPORTED"),
    (16, "Chile's Senate approves the Finance Ministry's part of the 2027 budget, 14-6.", "REPORTED"),
    (17, "Washington and Caracas operationalise a new counter-cartel pact.", "REPORTED"),
    (18, "GAO warns Pentagon munitions will take years to rebuild after the Iran war.", "OFFICIAL"),
    (19, "FAA grounds Miami airport after a FedEx cargo jet overruns the runway.", "OFFICIAL"),
    (20, "Senator Van Hollen blames Trump's Iran war and tariffs for dearer holiday groceries.", "REPORTED"),
    (21, "UK net migration falls to 77,000, the lowest since 1997 outside the pandemic.", "OFFICIAL"),
    (22, "Depardieu is ordered to stand trial for rape and sexual assault.", "OFFICIAL"),
    (23, "Germany arrests two Iraqi suspects over a March plot to attack synagogues.", "OFFICIAL"),
    (24, "Diesel tanker Med Emre capsizes off Ibiza with 7,000 tonnes of diesel; one crew member dies.", "OFFICIAL"),
    (25, "Kyiv's forces have struck 15 Russian oil refineries in November, ISW confirms.", "REPORTED"),
    (26, "Russia fires 112 strike drones overnight, 66 of them jet-powered.", "REPORTED"),
    (27, "Houthis hit Saudi Red Sea port Jizan; drone stopped near Jeddah, missiles over Riyadh.", "REPORTED"),
    (28, "Iran tightens Hormuz transit controls and denounces US AI targeting.", "CLAIM"),
    (29, "US pulls bombers from a UK base after two men are charged with national-security offences.", "REPORTED"),
    (30, "Guinea-Bissau's junta postpones elections to 2028, extending its rule by two years.", "OFFICIAL"),
    (31, "Drone attacks kill at least 15 in Sudan's Blue Nile state.", "REPORTED"),
    (32, "A cheaper twice-yearly HIV prevention jab reaches Africa.", "OFFICIAL"),
    (33, "Taiwan jails a former navy sergeant for six years for spying for China.", "OFFICIAL"),
    (34, "South Korea extends its K-ETA visa-free exemption through 2027.", "OFFICIAL"),
    (35, "A blast and fire at a Bangkok oil facility injures at least 9.", "REPORTED"),
    (36, "The Philippine Coast Guard commissions three new patrol vessels.", "OFFICIAL"),
    (37, "Maldives opens automated immigration e-Gates to 46 nationalities on 31 airlines.", "OFFICIAL"),
    (38, "India eyes first Test series win in New Zealand in 17 years as Christchurch Test looms.", "REPORTED"),
    (39, "Flight Centre investigates a mass cyber breach.", "REPORTED"),
    (40, "Authorities seize 3+ tonnes of meth from a Pacific mothership.", "OFFICIAL"),
    (41, "Australia sets working-holiday quotas from Mar 2027: 45,000 second, 25,000 third visas.", "OFFICIAL"),
    (42, "FinCEN confirms an internal cyber breach and disconnects systems.", "OFFICIAL"),
    (43, "Switzerland confirms first autonomous AI-agent cyberattacks; CISA adds 10 flaws to exploited list.", "OFFICIAL"),
]

NUMBERS = [
    ("$49bn", "EU loan at stake"),
    ("77,000", "UK net migration"),
    ("12,000", "Ebola cases in Congo"),
    ("31", "killed in Cairo blast"),
    ("112", "Russian drones overnight"),
    ("13+13", "Bogor dead & missing"),
]

TIMELINE = [
    ("04:11", "FAA grounds Miami"),
    ("04:47", "Brazil hits back at tariffs"),
    ("05:41", "Houthis hit Jizan"),
    ("07:11", "Cairo toll reaches 31"),
    ("18:57", "Mexico blasts DEA"),
    ("20:09", "Gaza strikes kill 10"),
    ("21:27", "EU splits on Ukraine loan"),
]

REGIONS = [("NORTH AMERICA", 4), ("LATIN AMERICA", 4), ("EUROPE", 9),
           ("MIDDLE EAST", 6), ("AFRICA", 5), ("EAST ASIA", 4),
           ("SOUTHEAST ASIA", 3), ("SOUTH ASIA", 3), ("OCEANIA", 3),
           ("GLOBAL", 2)]

DATE_CHECK = [
    "Mon 23 Nov: Nvidia brings back Jensen Huang; shares soar 31%",
    "Tue 24 Nov: Nvidia falls 5.9% · Taiex +8.99% record · Shanghai party chief Chen Jining probed · Sanofi buys Insmed for $41bn · Brazil withdraws its ambassador to Argentina",
    "Wed 25 Nov: US proposes tariffs on 14 partners · Netanyahu trial judges urge dropping the bribery charge · Solomon Islands signs Australia security treaty · Heavy rains kill 8 in Brazil",
    "Thu 19 Nov: Lula signs decree recognising Raoni's Kapot Nhinore land",
    "Sun 22 Nov: COP31 ends with no deal",
    "Sat 21 Nov: Indonesia candy-factory fire breaks out",
    "Fri 20 Nov: Argentina approves LNG exports",
]


# ---------------------------------------------------------------- pictures
def draw_illustration(d, key, x, y, s):
    """Draw a small geometric illustration in the s x s box at (x, y)."""
    if key == "eu":  # EU flag, split by a crack
        d.rectangle([x, y, x + s, y + s], fill=(0, 51, 153))
        cx, cy, r = x + s // 2, y + s // 2, s // 3
        for i in range(12):
            import math
            a = math.pi * 2 * i / 12 - math.pi / 2
            d.ellipse([cx + r * math.cos(a) - 2, cy + r * math.sin(a) - 2,
                       cx + r * math.cos(a) + 2, cy + r * math.sin(a) + 2],
                      fill=(255, 204, 0))
        d.line([x + s // 2 - 6, y + 4, x + s // 2 + 8, y + s - 4],
               fill=(255, 255, 255), width=3)
    elif key == "parade":  # balloon over skyline, storm cloud
        d.rectangle([x, y, x + s, y + s], fill=(135, 190, 230))
        d.ellipse([x + 4, y + 2, x + 24, y + 12], fill=(120, 120, 120))
        d.ellipse([x + 16, y + 6, x + 34, y + 15], fill=(150, 150, 150))
        for bx, bw, bh in ((2, 10, 26), (14, 8, 18), (24, 12, 30), (38, 9, 20), (49, 11, 28)):
            d.rectangle([x + bx, y + s - bh, x + bx + bw, y + s], fill=(70, 80, 95))
        d.ellipse([x + s // 2 - 11, y + 14, x + s // 2 + 11, y + 36],
                  fill=(200, 40, 40), outline=(140, 20, 20), width=2)
        d.line([x + s // 2, y + 36, x + s // 2 - 4, y + s - 26], fill=(90, 40, 40), width=2)
    elif key == "chess":
        d.rectangle([x, y, x + s, y + s], fill=(240, 217, 181))
        cell = s // 4
        for r in range(4):
            for c in range(4):
                if (r + c) % 2:
                    d.rectangle([x + c * cell, y + r * cell,
                                 x + (c + 1) * cell, y + (r + 1) * cell],
                                fill=(120, 72, 40))
        d.ellipse([x + 6, y + 6, x + 22, y + 22], fill=(255, 255, 255),
                  outline=(60, 60, 60), width=2)
        d.ellipse([x + s - 24, y + s - 24, x + s - 8, y + s - 8],
                  fill=(30, 30, 30), outline=(0, 0, 0), width=2)
    elif key == "blast":  # explosion over skyline
        d.rectangle([x, y, x + s, y + s], fill=(40, 40, 60))
        for bx, bw, bh in ((2, 12, 18), (16, 10, 26), (28, 12, 15), (42, 10, 22)):
            d.rectangle([x + bx, y + s - bh, x + bx + bw, y + s], fill=(20, 20, 30))
        cx, cy = x + s // 2, y + s // 2 - 6
        for r, col in ((16, (255, 140, 0)), (11, (255, 200, 0)), (6, (255, 240, 150))):
            d.polygon([(cx, cy - r), (cx + r // 2, cy - r // 2), (cx + r, cy),
                       (cx + r // 2, cy + r // 2), (cx, cy + r),
                       (cx - r // 2, cy + r // 2), (cx - r, cy),
                       (cx - r // 2, cy - r // 2)], fill=col)
    elif key == "drone":
        d.rectangle([x, y, x + s, y + s], fill=(222, 196, 150))
        d.rectangle([x, y + s - 10, x + s, y + s], fill=(190, 150, 100))
        cx, cy = x + s // 2, y + s // 2 - 4
        d.ellipse([cx - 10, cy - 5, cx + 10, cy + 5], fill=(40, 40, 40))
        for dx, dy in ((-16, -12), (16, -12), (-16, 12), (16, 12)):
            d.line([cx, cy, cx + dx, cy + dy], fill=(40, 40, 40), width=2)
            d.ellipse([cx + dx - 6, cy + dy - 2, cx + dx + 6, cy + dy + 2],
                      fill=(120, 120, 120))
        d.ellipse([cx - 3, cy - 2, cx + 3, cy + 2], fill=(255, 60, 60))
    elif key == "taj":  # domed hotel + candle
        d.rectangle([x, y, x + s, y + s], fill=(245, 230, 200))
        d.rectangle([x + 6, y + s - 22, x + s - 6, y + s], fill=(150, 90, 60))
        d.ellipse([x + s // 2 - 10, y + 12, x + s // 2 + 10, y + 32], fill=(150, 90, 60))
        d.ellipse([x + 10, y + 22, x + 22, y + 34], fill=(150, 90, 60))
        d.ellipse([x + s - 24, y + 22, x + s - 12, y + 34], fill=(150, 90, 60))
        d.rectangle([x + s - 12, y + s - 14, x + s - 8, y + s - 4], fill=(255, 255, 255))
        d.ellipse([x + s - 12, y + s - 19, x + s - 8, y + s - 13], fill=(255, 180, 0))
    elif key == "tanker":  # tanker truck + flames
        d.rectangle([x, y, x + s, y + s], fill=(200, 210, 220))
        d.rectangle([x, y + s - 12, x + s, y + s], fill=(90, 90, 90))
        d.rounded_rectangle([x + 6, y + 26, x + 42, y + 42], radius=8, fill=(220, 120, 20))
        d.rectangle([x + 42, y + 28, x + 54, y + 42], fill=(180, 60, 20))
        d.ellipse([x + 12, y + 40, x + 20, y + 48], fill=(20, 20, 20))
        d.ellipse([x + 44, y + 40, x + 52, y + 48], fill=(20, 20, 20))
        cx, cy = x + 24, y + 16
        d.polygon([(cx, cy - 12), (cx + 5, cy - 4), (cx + 11, cy - 8),
                   (cx + 7, cy + 2), (cx + 11, cy + 8), (cx, cy + 4),
                   (cx - 8, cy + 8), (cx - 5, cy), (cx - 11, cy - 6)],
                  fill=(255, 140, 0))
    elif key == "euro":
        d.rectangle([x, y, x + s, y + s], fill=NAVY)
        d.text((x + 8, y + 2), "€", font=font(SERIF_B, 34), fill=GOLD)
        for i in range(4):
            bx = x + 6 + i * 13
            d.rectangle([bx, y + s - 16, bx + 8, y + s - 4], fill=(230, 230, 230))
        d.rectangle([x + 4, y + s - 18, x + s - 4, y + s - 16], fill=(230, 230, 230))
    elif key == "missile":
        d.rectangle([x, y, x + s, y + s], fill=(30, 40, 55))
        d.polygon([(x + 44, y + 6), (x + 52, y + 22), (x + 44, y + 30),
                   (x + 36, y + 22)], fill=(200, 200, 200))
        d.polygon([(x + 38, y + 28), (x + 50, y + 28), (x + 46, y + 44),
                   (x + 42, y + 44)], fill=(160, 160, 160))
        d.polygon([(x + 20, y + 50), (x + 30, y + 44), (x + 34, y + 54)],
                  fill=(255, 140, 0))
        d.polygon([(x + 10, y + 12), (x + 13, y + 20), (x + 5, y + 20)],
                  fill=(255, 60, 60))
    elif key == "mine":  # mine shaft + flood water
        d.rectangle([x, y, x + s, y + s], fill=(150, 110, 70))
        d.pieslice([x + 12, y + 8, x + s - 12, y + s - 8], 180, 360, fill=(40, 25, 15))
        d.rectangle([x + 12, y + s // 2, x + s - 12, y + s - 8], fill=(40, 25, 15))
        d.rectangle([x, y + s - 14, x + s, y + s], fill=(40, 110, 180))
        d.arc([x - 4, y + s - 18, x + 18, y + s - 4], 200, 340, fill=(255, 255, 255), width=2)
        d.arc([x + 20, y + s - 18, x + 42, y + s - 4], 200, 340, fill=(255, 255, 255), width=2)
    elif key == "ship":  # supertanker + spiky mine
        d.rectangle([x, y, x + s, y + s], fill=(120, 170, 200))
        d.rectangle([x, y + s - 12, x + s, y + s], fill=(40, 100, 160))
        d.polygon([(x + 6, y + 30), (x + s - 6, y + 30), (x + s - 14, y + 44),
                   (x + 14, y + 44)], fill=(30, 30, 30))
        d.rectangle([x + 34, y + 18, x + 44, y + 30], fill=(200, 60, 60))
        mx, my = x + s - 16, y + 12
        d.ellipse([mx - 6, my - 6, mx + 6, my + 6], fill=(20, 20, 20))
        for dx, dy in ((-8, 0), (8, 0), (0, -8), (0, 8), (-6, -6), (6, -6), (-6, 6), (6, 6)):
            d.line([mx, my, mx + dx, my + dy], fill=(20, 20, 20), width=2)
    elif key == "virus":
        d.rectangle([x, y, x + s, y + s], fill=(190, 220, 190))
        cx, cy = x + s // 2, y + s // 2
        for i in range(10):
            import math
            a = math.pi * 2 * i / 10
            d.line([cx + 12 * math.cos(a), cy + 12 * math.sin(a),
                    cx + 18 * math.cos(a), cy + 18 * math.sin(a)],
                   fill=(30, 100, 40), width=2)
        d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(40, 130, 60))
        d.ellipse([cx - 5, cy - 7, cx + 1, cy - 1], fill=(120, 200, 130))
        d.ellipse([cx + 2, cy + 2, cx + 8, cy + 8], fill=(120, 200, 130))
    elif key == "mall":  # shopping centre + blast
        d.rectangle([x, y, x + s, y + s], fill=(180, 200, 220))
        d.rectangle([x + 6, y + 18, x + s - 6, y + s - 6], fill=(220, 225, 235))
        for i in range(4):
            d.rectangle([x + 10 + i * 12, y + 24, x + 18 + i * 12, y + 36],
                        fill=(60, 120, 180))
        d.rectangle([x + 22, y + s - 18, x + 38, y + s - 6], fill=(90, 90, 100))
        cx, cy = x + s - 12, y + 12
        d.polygon([(cx, cy - 8), (cx + 3, cy - 3), (cx + 8, cy - 5),
                   (cx + 4, cy + 1), (cx + 7, cy + 6), (cx, cy + 3),
                   (cx - 5, cy + 7), (cx - 3, cy + 1), (cx - 8, cy - 3)],
                  fill=(255, 140, 0))


# ---------------------------------------------------------------- map
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
     (-80, 73), (-65, 62), (-55, 52), (-60, 47), (-70, 42), (-75, 35),
     (-80, 26), (-85, 30), (-90, 21), (-95, 19), (-97, 16), (-105, 20),
     (-115, 28), (-125, 40), (-125, 49), (-140, 60), (-155, 58), (-165, 60)],
    [(-80, 10), (-75, 5), (-70, 0), (-60, -5), (-50, -5), (-35, -8),
     (-40, -20), (-48, -28), (-55, -35), (-65, -45), (-70, -52), (-73, -40),
     (-72, -20), (-80, -5)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (3, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 60), (28, 62), (30, 70), (40, 68), (45, 65),
     (40, 55), (35, 50), (30, 45), (28, 41), (23, 40), (19, 42), (15, 44),
     (12, 44), (8, 44), (3, 42), (0, 39), (-2, 37), (-6, 36)],
    [(-17, 15), (-16, 20), (-10, 30), (-5, 35), (10, 37), (20, 32),
     (32, 31), (35, 28), (43, 12), (51, 11), (48, 0), (40, -10),
     (35, -20), (32, -29), (25, -34), (18, -35), (15, -27), (12, -18),
     (9, -1), (9, 4), (-8, 5), (-13, 8), (-17, 12)],
    [(30, 70), (45, 68), (60, 70), (75, 73), (90, 75), (110, 76), (130, 72),
     (150, 70), (170, 67), (178, 65), (170, 60), (160, 55), (150, 60),
     (140, 50), (135, 43), (127, 40), (122, 38), (120, 32), (110, 20),
     (105, 10), (100, 8), (98, 15), (95, 20), (90, 22), (85, 20), (80, 15),
     (77, 8), (72, 20), (66, 25), (60, 25), (55, 26), (50, 29), (48, 30),
     (45, 35), (40, 38), (35, 36), (30, 36), (28, 41), (30, 45), (35, 50),
     (40, 55), (38, 60), (35, 65)],
    [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -10),
     (125, -9), (130, -4), (135, -3), (140, -8), (138, -6), (130, -2),
     (120, 0), (113, 3), (105, 2), (100, 5)],
    [(109, 1), (113, 4), (117, 6), (119, 0), (117, -3), (112, -3), (109, 0)],
    [(131, -1), (136, -2), (141, -3), (147, -6), (150, -9), (146, -8),
     (141, -8), (136, -6), (131, -3)],
    [(130, 31), (133, 34), (137, 35), (140, 38), (142, 42), (144, 44),
     (141, 45), (139, 40), (136, 37), (132, 33)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (129, -32), (132, -32),
     (136, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27),
     (150, -22), (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
     (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)],
]

# (number, lon, lat) — nudged slightly so neighbouring pins do not collide
PINS = [
    (1, -8, 58), (2, -74, 41), (3, 6, 42), (4, 38, 27), (5, 46, 30),
    (6, 73, 19), (7, 27, 34), (8, 16, 55), (9, 126, 39), (10, 107, -7),
    (11, 60, 22), (12, 25, 0), (13, 31, 50),
]


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- top banner
    d.rectangle([0, 0, W, 20], fill=NAVY)
    d.text((MARGIN, 4), "THE WORLD IN ONE DAY", font=font(SANS_B, 11), fill=(255, 255, 255))
    right = "43 STORIES · 10 REGIONS · EVERY ONE DATED THURSDAY 26 NOVEMBER 2026"
    d.text((W - MARGIN - font(SANS_B, 10).getlength(right), 5), right,
           font=font(SANS_B, 10), fill=(255, 255, 255))

    # ---- masthead
    title = "Thursday 26 November 2026"
    tf = font(SERIF_B, 44)
    d.text(((W - tf.getlength(title)) / 2, 20), title, font=tf, fill=NAVY)
    d.line([MARGIN, 70, W - MARGIN, 70], fill=NAVY, width=2)
    d.line([MARGIN, 73, W - MARGIN, 73], fill=NAVY, width=1)

    # ---- subhead: the three hero leads
    sub = "EU split on $49bn Ukraine loan · Macy's 100th parade postponed · Gukesh–Sindarov Game 3 drawn"
    sf = font(SERIF, 15)
    d.text(((W - sf.getlength(sub)) / 2, 78), sub, font=sf, fill=RED)

    # ---- numbers strip
    y0, y1 = 96, 140
    d.rectangle([MARGIN, y0, W - MARGIN, y1], fill=CREAM, outline=LINE)
    cell_w = CW / 6
    for i, (num, label) in enumerate(NUMBERS):
        cx = MARGIN + cell_w * (i + 0.5)
        nf = font(SERIF_B, 22)
        d.text((cx - nf.getlength(num) / 2, y0 + 3), num, font=nf, fill=NAVY)
        lf = font(SANS, 9)
        d.text((cx - lf.getlength(label) / 2, y0 + 27), label, font=lf, fill=INK)
        if i:
            d.line([MARGIN + cell_w * i, y0 + 5, MARGIN + cell_w * i, y1 - 5],
                   fill=LINE, width=1)

    # ---- UTC timeline (dark bar, two lines per entry)
    y0, y1 = 142, 172
    d.rectangle([MARGIN, y0, W - MARGIN, y1], fill=NAVY_D)
    cell_w = CW / 7
    for i, (t, ev) in enumerate(TIMELINE):
        cx = MARGIN + cell_w * i + 6
        d.text((cx, y0 + 3), t, font=font(SANS_B, 10), fill=GOLD)
        d.text((cx, y0 + 16), ev, font=font(SANS, 9), fill=(255, 255, 255))
        if i:
            d.line([MARGIN + cell_w * i, y0 + 4, MARGIN + cell_w * i, y1 - 4],
                   fill=(70, 85, 120), width=1)

    # ---- region tabs
    parts = []
    for name, n in REGIONS:
        parts.append(f"{name} {n}")
    reg = "  ·  ".join(parts)
    rf = font(SANS, 11)
    d.text(((W - rf.getlength(reg)) / 2, 176), reg, font=rf, fill=NAVY)
    d.line([MARGIN, 192, W - MARGIN, 192], fill=NAVY, width=1)

    # ---- lead grid: 3 columns x 5 rows
    card_w, card_h, gap = (CW - 2 * 6) // 3, 72, 6
    grid_y = 194
    for idx, lead in enumerate(LEADS):
        num, kicker, headline, body, source, bdg, key = lead
        row, col = divmod(idx, 3)
        cx = MARGIN + col * (card_w + gap)
        cy = grid_y + row * (card_h + gap)
        d.rectangle([cx, cy, cx + card_w, cy + card_h], fill=(255, 255, 255),
                    outline=LINE, width=1)
        # illustration + number badge
        draw_illustration(d, key, cx + 4, cy + 4, 60)
        d.ellipse([cx + 1, cy + 1, cx + 19, cy + 19], fill=NAVY,
                  outline=(255, 255, 255), width=1)
        nf = font(SANS_B, 10)
        ns = str(num)
        d.text((cx + 10 - nf.getlength(ns) / 2, cy + 3), ns, font=nf,
               fill=(255, 255, 255))
        tx = cx + 70
        tw = card_w - 70 - 6
        # kicker line: kicker left, source + badge right
        kf = font(SANS_B, 9)
        d.text((tx, cy + 5), kicker, font=kf, fill=RED)
        bx = badge(d, cx + card_w - 5, cy + 4, bdg)
        sf2 = font(SANS, 8)
        d.text((bx - 4 - sf2.getlength(source), cy + 5), source, font=sf2, fill=GRAY)
        # headline (up to 2 lines)
        hf = font(SERIF_B, 13)
        hl = wrap(headline, hf, tw)[:2]
        hy = cy + 17
        for i, ln in enumerate(hl):
            d.text((tx, hy + i * 14), ln, font=hf, fill=INK)
        # body (fills remaining space, up to 3 lines)
        by = hy + len(hl) * 14 + 1
        bf = font(SANS, 10)
        max_lines = max(1, (cy + card_h - 2 - by) // 11)
        bl = wrap(body, bf, tw)[:max_lines]
        for i, ln in enumerate(bl):
            d.text((tx, by + i * 11), ln, font=bf, fill=(60, 60, 60))

    # last row, columns 2-3: editor's note
    nx = MARGIN + 1 * (card_w + gap)
    ny = grid_y + 4 * (card_h + gap)
    nw = 2 * card_w + gap
    d.rectangle([nx, ny, nx + nw, ny + card_h], fill=CREAM, outline=LINE)
    note = ("Thirteen stories lead the front page; thirty more fill the columns "
            "below — every one of them first reported on Thursday 26 November 2026.")
    nf2 = font(SERIF, 13)
    nl = wrap(note, nf2, nw - 24)
    text_block(d, nx + 12, ny + 10, nl, nf2, NAVY, 17)

    # ---- map section header
    my = 582
    d.text((MARGIN, my), "WHERE IT HAPPENED", font=font(SANS_B, 13), fill=NAVY)
    d.text((W - MARGIN - font(SANS, 10).getlength("Pins 1–13 match the lead stories above"),
            my + 2), "Pins 1–13 match the lead stories above",
           font=font(SANS, 10), fill=GRAY)
    d.line([MARGIN, my + 16, W - MARGIN, my + 16], fill=LINE, width=1)

    # ---- world map (centred, flanked by legend / note)
    map_x0, map_y0, map_w, map_h = 212, 602, 600, 134
    d.rectangle([map_x0, map_y0, map_x0 + map_w, map_y0 + map_h], fill=SEA)
    d.rectangle([map_x0, map_y0, map_x0 + map_w, map_y0 + map_h], outline=LINE)

    def px(lon, lat):
        return (map_x0 + (lon + 180) / 360 * map_w,
                map_y0 + (82 - lat) / 140 * map_h)

    for lon in range(-150, 181, 30):
        x = map_x0 + (lon + 180) / 360 * map_w
        d.line([x, map_y0, x, map_y0 + map_h], fill=(190, 208, 216), width=1)
    for lat in (-30, 0, 30, 60):
        _, yy = px(0, lat)
        for xx in range(map_x0, map_x0 + map_w, 8):
            d.line([xx, yy, xx + 4, yy], fill=(190, 208, 216), width=1)
    for poly in CONTINENTS:
        d.polygon([px(lon, lat) for lon, lat in poly], fill=LAND, outline=LAND_EDGE)
    d.text((map_x0 + 12, map_y0 + map_h - 16), "ATLANTIC",
           font=font(SANS, 9), fill=(120, 140, 150))
    d.text((map_x0 + map_w - 62, map_y0 + map_h - 16), "PACIFIC",
           font=font(SANS, 9), fill=(120, 140, 150))
    pf = font(SANS_B, 8)
    for n, lon, lat in PINS:
        x, y = px(lon, lat)
        d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=RED, outline=(255, 255, 255), width=1)
        s = str(n)
        d.text((x - pf.getlength(s) / 2, y - 5), s, font=pf, fill=(255, 255, 255))

    # legend, left flank
    lx = MARGIN
    d.text((lx, 610), "HOW SURE", font=font(SANS_B, 11), fill=NAVY)
    legend = [("OFFICIAL", GREEN, "on the record"),
              ("REPORTED", BLUE, "wires / outlets"),
              ("CLAIM", RED, "one side, unverified")]
    for i, (lab, col, desc) in enumerate(legend):
        yy = 630 + i * 34
        d.ellipse([lx, yy, lx + 10, yy + 10], fill=col)
        d.text((lx + 15, yy - 1), lab, font=font(SANS_B, 10), fill=INK)
        for j, ln in enumerate(wrap(desc, font(SANS, 9), 180)):
            d.text((lx + 15, yy + 12 + j * 11), ln, font=font(SANS, 9), fill=GRAY)

    # note, right flank
    rx = 824
    d.text((rx, 610), "13 PINS · 10 REGIONS", font=font(SANS_B, 11), fill=NAVY)
    rnote = ("Every pin is a lead story above. "
             "Every story on this page was first reported on Thursday 26 November 2026.")
    rl = wrap(rnote, font(SANS, 10), 184)
    text_block(d, rx, 628, rl, font(SANS, 10), INK, 13)

    # ---- also on Thursday: stories 14-43, two columns
    ay = 740
    d.text((MARGIN, ay), "ALSO ON THURSDAY — STORIES 14–43",
           font=font(SANS_B, 12), fill=NAVY)
    d.line([MARGIN, ay + 17, W - MARGIN, ay + 17], fill=LINE, width=1)
    col_w = (CW - 16) // 2
    row_h = 11
    ly = ay + 22
    tf2 = font(SANS, 9)
    nf3 = font(SANS_B, 10)
    bf3 = font(SANS_B, 7)
    for i, (n, text, bdg) in enumerate(TAIL):
        col, row = divmod(i, 15)
        x = MARGIN + col * (col_w + 16)
        y = ly + row * row_h
        d.text((x, y), str(n), font=nf3, fill=RED)
        tx2 = x + 20
        # tiny badge at right end of the column
        bcol = GREEN if bdg == "OFFICIAL" else (BLUE if bdg == "REPORTED" else RED)
        blab = {"OFFICIAL": "OFF", "REPORTED": "REP", "CLAIM": "CLM"}[bdg]
        bw = int(bf3.getlength(blab)) + 6
        bx2 = x + col_w - bw
        d.rounded_rectangle([bx2, y + 1, bx2 + bw, y + 10], radius=2, fill=bcol)
        d.text((bx2 + 3, y + 1), blab, font=bf3, fill=(255, 255, 255))
        # trim text to fit before the badge
        max_w = bx2 - 4 - tx2
        t = text
        while tf2.getlength(t) > max_w and len(t) > 10:
            t = t.rsplit(" ", 1)[0]
        if t != text:
            t += "…"
        d.text((tx2, y), t, font=tf2, fill=INK)

    # ---- date check box
    dy = 926
    d.rectangle([MARGIN, dy, W - MARGIN, 1012], outline=RED, width=2)
    d.rectangle([MARGIN, dy, W - MARGIN, dy + 15], fill=RED)
    d.text((MARGIN + 8, dy + 2), "DATE CHECK — LEFT OUT: HAPPENED OTHER DAYS",
           font=font(SANS_B, 10), fill=(255, 255, 255))
    df = font(SANS, 10)
    for i, ln in enumerate(DATE_CHECK):
        d.text((MARGIN + 8, dy + 18 + i * 10), ln, font=df, fill=INK)

    # ---- footer
    foot = "Compiled after Thursday ended in UTC  ·  Pictures drawn in code, not photos"
    ff = font(SERIF, 9)
    d.text(((W - ff.getlength(foot)) / 2, 1014), foot, font=ff, fill=GRAY)

    return img


def main():
    img = build()
    img.save("entry.png", optimize=True)
    print("saved entry.png", img.size)


if __name__ == "__main__":
    main()
