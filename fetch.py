# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///

"""Download and extract NOAA Storm Events detail data for one year."""

import gzip
import re
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# The knobs.
# ---------------------------------------------------------------------------

YEAR = 2026
HERE = Path(__file__).parent
DATA_DIR = HERE / "data"
BASE_URL = "https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/"

# ---------------------------------------------------------------------------
# Getting the data. Fetch once, keep the file, parse the file.
# ---------------------------------------------------------------------------


def archive_name():
    """Find the newest published detail archive for YEAR in NOAA's index."""
    index = requests.get(BASE_URL, timeout=30)
    index.raise_for_status()
    pattern = rf"StormEvents_details-ftp_v1\.0_d{YEAR}_c\d{{8}}\.csv\.gz"
    matches = sorted(set(re.findall(pattern, index.text)))
    if not matches:
        raise RuntimeError(f"No details archive found for {YEAR}")
    return matches[-1]


def download_archive(name):
    """Save the compressed archive and its extracted CSV in data/."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    compressed = DATA_DIR / name
    csv_file = DATA_DIR / name.removesuffix(".gz")

    if not compressed.exists():
        response = requests.get(BASE_URL + name, timeout=120)
        response.raise_for_status()
        compressed.write_bytes(response.content)
        print(f"downloaded {compressed.name}")
    else:
        print(f"already downloaded {compressed.name}")

    if not csv_file.exists():
        with gzip.open(compressed, "rb") as source, csv_file.open("wb") as target:
            target.write(source.read())
        print(f"extracted {csv_file.name}")
    else:
        print(f"already extracted {csv_file.name}")


def main():
    name = archive_name()
    print(f"selected {name}")
    download_archive(name)


if __name__ == "__main__":
    main()
