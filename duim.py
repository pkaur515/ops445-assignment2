#!/usr/bin/env python3

import subprocess
import sys
import os
import argparse

'''
OPS445 Assignment 2 - Winter 2025
Program: duim.py 
Author: "Prabhjot Kaur"
The python code in this file (duim.py) is original work written by
"Prabhjot Kaur". No code in this file is copied from any other source 
except those provided by the course instructor, including any person, 
textbook, or on-line resource. I have not shared this python script 
with anyone or anything except for submission for grading.  
I understand that the Academic Honesty Policy will be enforced and 
violators will be reported and appropriate action will be taken.

Description: DU Improved -- See Disk Usage Report with bar charts

Date: 12 April,2025.
'''

def parse_command_args():
    """Set up argparse for duim.py and return parsed arguments."""
    parser = argparse.ArgumentParser(
        description="DU Improved -- See Disk Usage Report with bar charts",
        epilog="Copyright 2025"
    )
    parser.add_argument(
        "-l", "--length",
        type=int,
        default=20,
        help="Specify the length of the graph. Default is 20."
    )
    parser.add_argument(
        "-H", "--human-readable",
        action="store_true",
        help="Print sizes in human readable format (e.g. 1K 23M 2G)."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="The directory to scan."
    )
    return parser.parse_args()


def percent_to_graph(percent, total_chars):
    """
    Given a percent (0–100) and total bar length, return a string
    of '=' for the filled portion and spaces for the remainder.
    """
    # Percentage range
    if not isinstance(percent, (int, float)) or percent < 0 or percent > 100:
        sys.stderr.write("Error: percent must be between 0 and 100.\n")
        sys.exit(1)
    filled = round((percent * total_chars) / 100)
    empty = total_chars - filled
    return "=" * filled + " " * empty


def call_du_sub(location, human_readable=False):
    """
    Run `du -d 1 [ -h ] <location>` and return its output as a list of lines.
    """
    cmd = ["du", "-d", "1"]
    if human_readable:
        cmd.append("-h")
    cmd.append(location)
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
    except FileNotFoundError:
        sys.stderr.write("Error: `du` command not found.\n")
        sys.exit(1)

    if proc.returncode != 0:
        # pass through du's error message
        sys.stderr.write(err.decode())

    # split on newlines, drop any empty trailing line
    return [line for line in out.decode().split("\n") if line]


def create_dir_dict(alist):
    """
    Given a list of strings like "1234\t/path", return a dict
    { "/path": 1234, ... } converting sizes to int.
    """
    d = {}
    for entry in alist:
        parts = entry.split("\t", 1)
        if len(parts) != 2:
            continue
        size_str, path = parts
        try:
            size = int(size_str)
        except ValueError:
            # shouldn't happen without -h, but skip if it does
            continue
        d[path] = size
    return d


def main():
    args = parse_command_args()
    target = args.target

    # Target error message if it is invalid
    if not os.path.exists(target):
        sys.stderr.write(f"Error: target '{target}' does not exist.\n")
        sys.exit(1)
    if not os.path.isdir(target):
        sys.stderr.write(f"Error: target '{target}' is not a directory.\n")
        sys.exit(1)

    # get du output
    lines = call_du_sub(target, human_readable=args.human_readable)
    # build dict of { path: size }
    dir_sizes = create_dir_dict(lines)

    # determine total size 
    total = dir_sizes.get(target, None)
    # if du didn't list the parent as final line, sum all subdirs
    if total is None:
        total = sum(dir_sizes.values())

    # sort entries by size descending
    sorted_entries = sorted(dir_sizes.items(), key=lambda kv: kv[1], reverse=True)

    # print subdirectories
    for path, size in sorted_entries:
        if path == target:
            # skip the target itself in per-subdir listing
            continue
        pct = (size / total * 100) if total > 0 else 0
        bar = percent_to_graph(pct, args.length)
        # size display: raw bytes or human-readable
        if args.human_readable:
            # re-run du for this single entry to get its human size
            hr_line = call_du_sub(path, human_readable=True)
            # first line is "<size>\t<path>"
            hr_size = hr_line[0].split("\t", 1)[0]
            size_str = hr_size
        else:
            size_str = str(size)
        # format: " 61% [===   ] 160M  /path"
        print(f"{pct:3.0f}% [{bar}] {size_str}\t{path}")

    # print total line
    if args.human_readable:
        # get human-readable total
        hr_total_line = call_du_sub(target, human_readable=True)[-1]
        hr_total = hr_total_line.split("\t", 1)[0]
        total_str = hr_total
    else:
        total_str = str(total)
    print(f"Total: {total_str}\t{target}")


if __name__ == "__main__":
    main()
