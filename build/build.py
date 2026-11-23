#!/usr/bin/env python3
"""Build the news-image-20261123 front page.

Pipeline (all my own code, written for this entry):
  story data below -> HTML page (build/template.html)
  -> WeasyPrint typesetting -> 2048 px PNG -> 1024 px JPEG-in-entry.png

Content is the frozen pool for Monday 23 November 2026 (press time
18:55 UTC): 14 leads + 27 briefs = 41 stories, 7 regions. Nothing here
is copied from any earlier entry's build code; the layout follows the
same newspaper-front-page architecture (masthead, stat band, region
strip, UTC strip, illustrated leads, dot map, briefs, DATE CHECK).
"""

import html
import os
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ART = ROOT / "art"
CROPS = HERE / "crops"

# ---------------------------------------------------------------- palette
CREAM = "#f5eedd"
INK = "#191512"
NAVY = "#16233f"
CRIMSON = "#b3271e"

# Certainty chips: (label, short code, foreground, background)
CERTAINTY = {
    "CONFIRMED": ("CONFIRMED", "CON", "#ffffff", "#2e7d4f"),
    "REPORTED": ("REPORTED", "REP", "#ffffff", "#a86a12"),
    "CLAIM": ("CLAIM", "CLM", "#ffffff", "#b3271e"),
    "FORECAST": ("FORECAST", "FOR", "#ffffff", "#2b5f8a"),
}

# ------------------------------------------------------------------- leads
# n, kicker banner, location line, headline, 2-3 line summary, source,
# certainty, map longitude/latitude, easing offset in map-% points
# (easing keeps crowded pins readable and every pin on land).
LEADS = [
    dict(n=1, kicker="COP31 FAILS", loc="ANTALYA, TÜRKIYE · CLIMATE",
         head="Climate talks collapse in Antalya as blame flies",
         body=("COP31 ends with no deal — the first COP failure since "
               "Copenhagen 2009 — after a text with no mention of fossil "
               "fuels. Australia's opposition demands minister Bowen "
               "resign; Pacific islands say they were let down on all sides."),
         src="Reuters · 06:18 UTC", cert="CONFIRMED",
         lon=30.7, lat=36.9, ease=(0.0, 0.0)),
    dict(n=2, kicker="24 DEAD, ~30 MISSING", loc="CIKANDE, INDONESIA · FIRE",
         head="Indonesia confirms 24 dead in factory fire",
         body=("24 people died and about 30 are missing after fire tore "
               "through a confectionery factory on Saturday. Rescuers "
               "searched the unstable ruins on Monday as police took DNA "
               "from relatives of the unidentified dead."),
         src="Reuters · by 04:03 UTC", cert="CONFIRMED",
         lon=106.2, lat=-6.3, ease=(0.0, 0.0)),
    dict(n=3, kicker="CLAIM VS CONFIRMED", loc="BENGHAZI, LIBYA · WAR AT SEA",
         head="Ukraine drones hit Russian corvette; Zelenskiy says it sank",
         body=("Naval drones struck the corvette Merkury in Benghazi port; "
               "Zelenskiy says seven drones sank it and hit the MV Angara. "
               "Libya confirmed the attack; satellite images show it "
               "smouldering, partly submerged. Russia has not confirmed "
               "the sinking."),
         src="Reuters / AP / WSJ", cert="CLAIM",
         lon=20.1, lat=32.1, ease=(-1.8, 0.0)),
    dict(n=4, kicker="TOLL 11", loc="DYMER, UKRAINE · WAR",
         head="Death toll in Dymer attack rises to 11",
         body=("Another body pulled from the rubble; at least 15 died "
               "across the Kyiv region overnight."),
         src="Reuters · 06:24 UTC", cert="CONFIRMED",
         lon=30.3, lat=50.8, ease=(0.0, 0.0)),
    dict(n=5, kicker="ALIVE AT 7", loc="KYIV REGION, UKRAINE · RESCUE",
         head="Boy, 7, pulled alive from rubble hours after strike",
         body=("Rescuers freed the boy from a destroyed home in the Kyiv "
               "region."),
         src="BBC · Monday", cert="REPORTED",
         lon=30.5, lat=50.45, ease=(2.4, 2.2)),
    dict(n=6, kicker="258 SEATS", loc="WASHINGTON, US · POLITICS",
         head="Democrats clinch 258 House seats, best since 1992",
         body=("Hubbard beat Foxx by ~330 votes in a recount; Jeffries set "
               "to be first Black speaker."),
         src="AP · Monday", cert="CONFIRMED",
         lon=-77.0, lat=38.9, ease=(0.0, 0.0)),
    dict(n=7, kicker="PUSHED TO WEDNESDAY", loc="MIDDLETOWN, IOWA · STANDOFF",
         head="Army pushes Iowa blast to Wednesday",
         body=("The 9,700 lb blast was delayed for weather and mitigation; "
               "Middletown stayed evacuated."),
         src="Reuters / CNN · Monday", cert="FORECAST",
         lon=-91.4, lat=40.8, ease=(-1.3, 0.0)),
    dict(n=8, kicker="35–10", loc="MEXICO CITY · NFL",
         head="49ers rout Vikings 35–10 as NFL returns to Mexico City",
         body=("Purdy threw three touchdowns before 85,000 fans at 2,200 m; "
               "players used oxygen masks."),
         src="Reuters · kickoff 01:20 UTC", cert="CONFIRMED",
         lon=-99.1, lat=19.4, ease=(0.0, 0.0)),
    dict(n=9, kicker="31 TANKERS", loc="STRAIT OF HORMUZ · BLOCKADE",
         head="Flotilla of 31 Iranian tankers massing to test blockade",
         body=("Most are a day's sailing from the US line; the closest, "
               "Tour 2, was three hours out."),
         src="TradeWinds / Windward · 08:27 UTC", cert="REPORTED",
         lon=56.5, lat=26.5, ease=(0.0, 0.0)),
    dict(n=10, kicker="$1.62BN", loc="NEW DELHI · AID",
         head="India gives $1.62bn package to flood-hit Nepal",
         body=("Modi announced the 240-billion-rupee package after talks "
               "with Nepal's PM Balendra Shah."),
         src="Reuters · Monday", cert="CONFIRMED",
         lon=77.2, lat=28.6, ease=(0.0, 0.0)),
    dict(n=11, kicker="4 DEAD", loc="KHARTOUM, SUDAN · DRONE STRIKES",
         head="UN and US condemn Khartoum drone strikes",
         body=("Four died, including a 10-year-old; Sudan blames Ethiopia, "
               "which denies it — unverified."),
         src="AFP / PANA · 06:55 UTC", cert="REPORTED",
         lon=32.5, lat=15.6, ease=(0.0, 0.0)),
    dict(n=12, kicker="DRAW", loc="WELLINGTON, NZ · CRICKET",
         head="NZ hang on for draw as Australia regain top two",
         body=("India declared 9-720 but ended five wickets short; the "
               "draw lifted Australia into a final spot."),
         src="cricket.com.au · 05:46 UTC", cert="CONFIRMED",
         lon=174.8, lat=-41.3, ease=(-0.6, -1.0)),
    dict(n=13, kicker="KOSPI −3%", loc="SEOUL · MARKETS",
         head="Asia's AI selloff deepens as Kospi falls 3%",
         body=("The Wall Street selloff rolled on in thin trade; China "
               "unveiled support as US futures bounced."),
         src="Reuters · Monday", cert="CONFIRMED",
         lon=127.0, lat=37.5, ease=(0.0, 0.0)),
    dict(n=14, kicker="+31%", loc="SANTA CLARA, US · TECH",
         head="Nvidia reinstates Huang as chief after Trump intervenes",
         body=("The board reversed course after the president called in; "
               "shares surged over 31% premarket."),
         src="Reuters · Monday", cert="CONFIRMED",
         lon=-122.0, lat=37.4, ease=(0.0, 0.0)),
]

# ------------------------------------------------------------------ briefs
# n, region tag, one-line story, certainty. Order: as frozen in the pool.
BRIEFS = [
    (1, "EUR", "Armenia proposes new constitution in peace step", "CONFIRMED"),
    (2, "EUR", "Russia-bound ship towed off after Gulf of Finland attack", "REPORTED"),
    (3, "EUR", "Burnham: his EU deal can make next decade \u201cmuch better\u201d", "CONFIRMED"),
    (4, "EUR", "European gas prices surge on cold-snap shortage fears", "REPORTED"),
    (5, "EUR", "Northern Ireland doctors begin fresh strike over pay", "CONFIRMED"),
    (6, "EUR", "Co-op Live arena evacuated in suspected tear-gas incident", "REPORTED"),
    (7, "EUR", "NHS launches largest AI breast-cancer screening trial", "CONFIRMED"),
    (8, "EUR", "Russian strike on Vyshneve supermarket kills three", "CONFIRMED"),
    (9, "EUR", "Spanish court clears last hurdle to Puigdemont\u2019s return", "CONFIRMED"),
    (10, "EUR", "Czech, Hungarian leaders reject new EU budget proposal", "CONFIRMED"),
    (11, "ASI", "South Korea names first woman spy chief in reshuffle", "CONFIRMED"),
    (12, "ASI", "Bangladesh vows to arrest Hasina if she returns", "CONFIRMED"),
    (13, "ASI", "Prabowo names two VP candidates: Amran Sulaiman, Sugiono", "CONFIRMED"),
    (14, "MDE", "Iran vows to use all tools against US naval blockade", "CONFIRMED"),
    (15, "MDE", "Iran navy: two supertankers hit mines near Hormuz", "CLAIM"),
    (16, "MDE", "Brent near $92 as Hormuz flows slow to 9.5m bpd", "CONFIRMED"),
    (17, "MDE", "US discussing military training for Syrian forces", "REPORTED"),
    (18, "AFR", "UN mission in Libya condemns attacks on Benghazi ship", "CONFIRMED"),
    (19, "AFR", "Africa health conference CPHIA opens in Addis Ababa", "CONFIRMED"),
    (20, "AFR", "Congo halts cobalt exports again to tackle oversupply", "CONFIRMED"),
    (21, "OCE", "Australian music legend Molly Meldrum dies aged 83", "CONFIRMED"),
    (22, "OCE", "Australia\u2019s private sector shrinks fastest in five years", "CONFIRMED"),
    (23, "NAM", "FAA pauses router installation linked to ground stop", "REPORTED"),
    (24, "NAM", "US business growth cools to four-month low, PMI 54.6", "CONFIRMED"),
    (25, "NAM", "CrowdStrike to buy Zscaler in $43.9bn all-stock deal", "CONFIRMED"),
    (26, "NAM", "US files to recover $1bn+ crypto stolen in Binance hack", "CONFIRMED"),
    (27, "LAM", "Brazil\u2019s real hits 5.95 per dollar before stocks reopen", "CONFIRMED"),
]

# ------------------------------------------------------------------- stats
# (big number, caption, story reference)
STATS = [
    ("24", "dead in the Cikande fire, Indonesia", "LEAD 2"),
    ("$1.62bn", "India\u2019s package to flood-hit Nepal", "LEAD 10"),
    ("258", "House seats won by Democrats", "LEAD 6"),
    ("31", "tankers massing off Hormuz", "LEAD 9"),
    ("11", "killed in the Russian attack on Dymer", "LEAD 4"),
    ("720", "India\u2019s 9-720 declared at Wellington", "LEAD 12"),
]

REGIONS = [
    ("NORTH AMERICA", 7, "#5b4a8a"),
    ("LATIN AMERICA", 2, "#2e6f6a"),
    ("EUROPE", 14, "#1f3a5f"),
    ("AFRICA", 4, "#a86a12"),
    ("MIDDLE EAST", 5, "#b3271e"),
    ("ASIA", 6, "#2b5f8a"),
    ("OCEANIA", 3, "#3d7a4a"),
]

# (time, label) — verified UTC times only; the last line is the no-blast note.
UTC_STRIP = [
    ("01:20", "NFL kickoff, Mexico City"),
    ("04:03", "Reuters: 24 dead, Cikande fire"),
    ("05:46", "Wellington Test drawn"),
    ("06:18", "COP31 backlash published"),
    ("06:24", "Dymer toll rises to 11"),
    ("06:41", "UN Libya condemns Benghazi hit"),
    ("06:55", "US condemns Khartoum strikes"),
    ("08:27", "Windward: 31 tankers massing"),
    ("~10:00", "Prabowo names two VP picks"),
    ("14:45", "US flash PMI 54.6"),
    ("18:32", "US files $1bn Binance-hack claim"),
    ("MONDAY", "No blast in Iowa — Wed instead"),
]

DATE_CHECK = (
    "Left out as other days\u2019 news: Alcaraz wins the ATP Finals (Sun) \u00b7 "
    "South Korea\u2019s education minister resigns (Sun) \u00b7 Ethiopia polio "
    "campaign (21 Nov) \u00b7 Lan\u00fas gas blast (13 Nov) \u00b7 Sinaloa kingpin "
    "arrest deaths (21\u201322 Nov) \u00b7 Wall Street correction (Fri) \u00b7 "
    "GTA VI launch (19 Nov) \u00b7 Tankers cross the blockade line "
    "(Tue/Wed \u2014 not Monday) \u00b7 Trump\u2019s post on Huang (Sun)."
)

PRESS_TIME = "WIRES READ TO 18:55 UTC, MONDAY 23 NOVEMBER 2026"

# ------------------------------------------------------------- map pin math
# The dot map is an equirectangular world (1912 x 760). I calibrated the
# projection by eye from the rendered map: Alaska's west tip (-170 deg)
# sits near x=10, Siberia's east tip (+180) near x=1905, the far north
# (+70 deg) near y=65 and South America's tip (-55) near y=745.
MAP_W, MAP_H = 1912, 760


def pin_position(lead):
    """Map percentage (left, top) for a lead's pin, with its easing."""
    x_px = 10.0 + (lead["lon"] + 170.0) * 5.41
    y_px = 65.0 + (70.0 - lead["lat"]) / 0.1838
    dx, dy = lead["ease"]
    left = x_px / MAP_W * 100.0 + dx
    top = y_px / MAP_H * 100.0 + dy
    return round(left, 1), round(top, 1)


# -------------------------------------------------------------- image crops
def crop_art(lead_no, target_w, target_h):
    """Centre-crop (slightly top-biased) a lead's art to target aspect."""
    src = ART / ("lead%02d.jpg" % lead_no)
    out = CROPS / ("lead%02d_%dx%d.jpg" % (lead_no, target_w, target_h))
    if out.exists():
        return out
    im = Image.open(src).convert("RGB")
    want = target_w / target_h
    w, h = im.size
    have = w / h
    if have > want:  # too wide: trim the sides
        nw = int(h * want)
        x0 = (w - nw) // 2
        box = (x0, 0, x0 + nw, h)
    else:  # too tall: trim top/bottom, keeping the upper 40% band
        nh = int(w / want)
        y0 = max(0, int((h - nh) * 0.35))
        box = (0, y0, w, y0 + nh)
    im.crop(box).resize((target_w, target_h), Image.LANCZOS).save(
        out, "JPEG", quality=82, optimize=True)
    return out


# ------------------------------------------------------------ HTML builders
def esc(text):
    return html.escape(text, quote=False)


def chip(cert, big=False):
    label, _code, fg, bg = CERTAINTY[cert]
    cls = "chip" + (" chip-big" if big else "")
    return ('<span class="%s" style="color:%s;background:%s">%s</span>'
            % (cls, fg, bg, label))


def chip_code(cert):
    _label, code, fg, bg = CERTAINTY[cert]
    return ('<span class="chip-code" style="color:%s;background:%s">%s</span>'
            % (fg, bg, code))


def hero_card(lead):
    img = crop_art(lead["n"], 660, 210)
    return (
        '<div class="hero">'
        '<div class="hero-img"><img src="%s">'
        '<div class="kicker">%s</div>'
        '<div class="hero-chip">%s</div></div>'
        '<div class="hero-loc"><b>%d</b> &nbsp;%s</div>'
        '<div class="hero-head">%s</div>'
        '<div class="hero-body">%s</div>'
        '<div class="hero-src">%s</div>'
        '</div>'
        % (img.as_uri(), esc(lead["kicker"]), chip(lead["cert"]),
           lead["n"], esc(lead["loc"]), esc(lead["head"]),
           esc(lead["body"]), esc(lead["src"])))

def mini_card(lead):
    img = crop_art(lead["n"], 340, 104)
    return (
        '<div class="mini">'
        '<div class="mini-img"><img src="%s">'
        '<div class="kicker kicker-sm">%s</div></div>'
        '<div class="mini-loc"><b>%d</b> &nbsp;%s</div>'
        '<div class="mini-head">%s</div>'
        '<div class="mini-body">%s</div>'
        '<div class="mini-meta">%s <span class="mini-src">%s</span></div>'
        '</div>'
        % (img.as_uri(), esc(lead["kicker"]), lead["n"], esc(lead["loc"]),
           esc(lead["head"]), esc(lead["body"]), chip(lead["cert"]),
           esc(lead["src"])))


def stat_cell(number, caption, ref):
    return (
        '<div class="stat"><div class="stat-num">%s</div>'
        '<div class="stat-cap">%s</div>'
        '<div class="stat-ref">%s</div></div>'
        % (esc(number), esc(caption), esc(ref)))


def region_cell(name, count, colour):
    return ('<div class="region" style="background:%s">%s <b>%d</b></div>'
            % (colour, esc(name), count))


def utc_cell(time, label):
    return ('<div class="utc-item"><span class="utc-time">%s</span> '
            '<span class="utc-label-txt">%s</span></div>'
            % (esc(time), esc(label)))


def brief_line(number, tag, text, cert):
    return ('<div class="brief"><span class="brief-num">%d</span> '
            '<span class="brief-tag">%s</span> '
            '<span class="brief-text">%s</span> %s</div>'
            % (number, tag, esc(text), chip_code(cert)))


def build_sections():
    heroes = "".join(hero_card(l) for l in LEADS[:3])
    minis_a = "".join(mini_card(l) for l in LEADS[3:9])
    minis_b = "".join(mini_card(l) for l in LEADS[9:14])
    stats = "".join(stat_cell(*s) for s in STATS)
    regions = "".join(region_cell(*r) for r in REGIONS)
    utc = "".join(utc_cell(*u) for u in UTC_STRIP)
    pins = "".join(
        '<div class="pin" style="left:%s%%;top:%s%%">%d</div>'
        % (left, top, lead["n"])
        for lead in LEADS
        for left, top in [pin_position(lead)])
    half = (len(BRIEFS) + 1) // 2
    briefs_a = "".join(brief_line(*b) for b in BRIEFS[:half])
    briefs_b = "".join(brief_line(*b) for b in BRIEFS[half:])
    legend = "".join(
        '<span class="legend-item">%s&nbsp;=&nbsp;%s</span>'
        % (chip(name), meaning)
        for name, meaning in [
            ("CONFIRMED", "verified by the wires"),
            ("REPORTED", "carried by the day\u2019s wires"),
            ("CLAIM", "one side\u2019s account, labelled as such"),
            ("FORECAST", "still to happen when drawn"),
        ])
    return dict(
        heroes=heroes, minis_a=minis_a, minis_b=minis_b, stats=stats,
        regions=regions, utc=utc, pins=pins, briefs_a=briefs_a,
        briefs_b=briefs_b, legend=legend,
        date_check=esc(DATE_CHECK), press_time=esc(PRESS_TIME),
    )


# -------------------------------------------------------------------- render
def render():
    """Typeset the page and write repo/entry.png (JPEG bytes, .png name).

    WeasyPrint renders a one-page PDF first so an overflow onto a
    second page fails loudly instead of silently clipping the page.
    """
    import subprocess

    from weasyprint import HTML

    CROPS.mkdir(parents=True, exist_ok=True)
    template = (HERE / "template.html").read_text(encoding="utf-8")
    page = template
    for key, value in build_sections().items():
        page = page.replace("<!--" + key.upper() + "-->", value)
    pdf = HERE / "page.pdf"
    HTML(string=page, base_url=str(HERE)).write_pdf(str(pdf))
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True,
                          text=True, check=True).stdout
    pages = int([l for l in info.splitlines()
                 if l.startswith("Pages:")][0].split(":")[1])
    assert pages == 1, "page overflowed to %d pages" % pages
    big = HERE / "page-2048.png"
    subprocess.run(["pdftoppm", "-r", "192", "-png", "-singlefile",
                    str(pdf), str(big.with_suffix(""))],
                   check=True, capture_output=True)
    im = Image.open(big).convert("RGB")
    assert im.size == (2048, 2048), "unexpected raster size %s" % (im.size,)
    small = im.resize((1024, 1024), Image.LANCZOS)
    out = ROOT / "entry.png"
    small.save(out, "JPEG", quality=84, optimize=True, progressive=False)
    size = out.stat().st_size
    print("entry.png: %d bytes, %s" % (size, small.size))
    assert size <= 1048576, "entry.png over the 1 MiB cap"
    assert small.size[0] <= 1024 and small.size[1] <= 1024
    return out


if __name__ == "__main__":
    render()
