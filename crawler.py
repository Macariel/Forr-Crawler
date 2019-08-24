#!/usr/bin/env python3
import argparse

parser = argparse.ArgumentParser(description="Forró Crawler")
subparsers = parser.add_subparsers(dest="cmd")

forro_em_vinil = subparsers.add_parser("Vinil", help="Forro Em Vinil crawler")

soundcloud = subparsers.add_parser("soundcloud", help="Soundcloud crawler")

youtube = subparsers.add_parser("youtube", help="YouTube crawler")

parser.parse_args()