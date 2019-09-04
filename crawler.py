#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys

from forro_em_vinil import forro_em_vinil

DIR = os.path.dirname(__file__)
MUSIC_DIR = os.path.join(DIR, "music")
SCRIPT_DIR = os.path.join(DIR, "scripts")


def main():
    args = parse_arguments()

    if args.type == "vinil":
        downoad_from_forro_em_vinil(args)

    if args.type == "soundcloud":
        download_from_soundcloud(args.link)

    if args.type == "youtube":
        download_from_youtube(args.link, args.dest)


def downoad_from_forro_em_vinil(args):
    if args.cmd == "fetch_links":
        forro_em_vinil.CACHING = args.cache

        if args.option == "category":
            forro_em_vinil.fetch_category_links()
        elif args.option == "year":
            forro_em_vinil.fetch_year_links()
        elif args.option == "artist":
            forro_em_vinil.fetch_artist_links()
        else:
            forro_em_vinil.fetch_all()

    if args.cmd == "download":
        forro_em_vinil.download()

    if args.cmd == "extract":
        forro_em_vinil.extract()


def download_from_soundcloud(link):
    return subprocess.run([os.path.join(SCRIPT_DIR, "download_from_soundcloud.sh"), link]).returncode


def download_from_youtube(link, dest):
    return subprocess.run([os.path.join(SCRIPT_DIR, "download_from_youtube.sh"), link, dest]).returncode


def parse_arguments():
    parser = argparse.ArgumentParser(description="Forró Crawler for fetching music from multiple different sources")
    subparsers = parser.add_subparsers(dest="type")

    vinil = subparsers.add_parser("vinil", help="Forro Em Vinil crawler and downloader")
    vinil_sub = vinil.add_subparsers(dest="cmd")
    fetch = vinil_sub.add_parser("fetch_links", help="Fetch download links from website")
    fetch.add_argument("--cache", action="store_true",
                       help="Activate the caching of websites downloaded from forró em vinil")
    fetch.add_argument("--all", dest="option", action="store_const", const="all", default="all",
                       help="Fetch links from all sources (default option if none is given")
    fetch.add_argument("--category", dest="option", action="store_const", const="category",
                       help="Fetch links by categories")
    fetch.add_argument("--year", dest="option", action="store_const", const="year", help="Fetch links by years")
    fetch.add_argument("--artist", dest="option", action="store_const", const="artist", help="Fetch links by artists")

    vinil_sub.add_parser("download", help="Download all provided by the fetched links")

    vinil_sub.add_parser("extract", help="Extract all downloaded archives")

    soundcloud = subparsers.add_parser("soundcloud", help="Soundcloud music downloader")
    soundcloud.add_argument("link", help="Link to a soundcloud playlist")

    youtube = subparsers.add_parser("youtube", help="YouTube music downloader")
    youtube.add_argument("link", help="Link to a video or a playlist")
    youtube.add_argument("dest", help="Name of the folder which will contain the music")

    if len(sys.argv) < 2:
        parser.print_help()
        exit(0)

    return parser.parse_args()


if __name__ == '__main__':
    main()
