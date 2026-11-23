# The World in One Day — Monday 23 November 2026

[![news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/surebe/news-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/surebe/news-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123)

One image summing up the world's news of **Monday 23 November 2026**:
41 stories across 7 regions — COP31 collapsing in Antalya, 24 dead in
the Cikande factory fire, Ukraine's drone strike on the Russian corvette
Merkury, Democrats taking 258 House seats, the Iowa blast pushed to
Wednesday, 31 Iranian tankers massing off Hormuz, India giving Nepal
$1.62bn, and more — with a UTC timeline, a stat band keyed to the
stories, a printed certainty legend, a dot-matrix world map, and a
DATE CHECK box naming the other days' stories left out.

Entry for the make.fun bounty
[news-image-20261123](https://make.fun/bounty/news-image-20261123).

## How it is built

`build/build.py` holds the frozen story data (14 leads + 27 briefs from
the 18:55 UTC press freeze), crops the illustrations, assembles
`build/template.html`, and typesets it with WeasyPrint into
`entry.png` (1024×1024, JPEG bytes). The illustrations in `art/` were
generated fresh for this page in one locked flat-editorial palette;
the dot map in `build/` is drawn in code.

## Run

```sh
python3 build/build.py   # rebuild entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py   # write out/entry.png
```

`main.py` uses only the Python standard library, needs no network, and
copies the shipped `entry.png` to the output directory, so both runs
write byte-identical files.
