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

    if args.crawler == "vinil":
        downoad_from_forro_em_vinil(args)

    if args.crawler == "soundcloud":
        download_from_soundcloud(args.link)

    if args.crawler == "youtube":
        download_from_youtube(args.link, args.dest)


def downoad_from_forro_em_vinil(args):
    if args.command == "fetch_links":
        forro_em_vinil.fetch_download_links()

    if args.command == "download":
        forro_em_vinil.download()

    if args.command == "extract":
        forro_em_vinil.extract()


def download_from_soundcloud(link):
    return subprocess.run([os.path.join(SCRIPT_DIR, "download_from_soundcloud.sh"), link]).returncode


def download_from_youtube(link, dest):
    return subprocess.run([os.path.join(SCRIPT_DIR, "download_from_youtube.sh"), link, dest]).returncode


def parse_arguments():
    parser = argparse.ArgumentParser(description="Forró Crawler for fetching music from multiple different sources")
    subparsers = parser.add_subparsers(dest="crawler")

    vinil = subparsers.add_parser("vinil", help="Forro Em Vinil crawler and downloader")
    vinil.add_argument("command", choices={"fetch_links", "download", "extract"})

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
