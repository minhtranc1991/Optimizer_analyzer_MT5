"""Run the full analysis on MT5 optimization reports.

python main.py                      # newest XML in data/
python main.py data/a.xml data/b.xml
"""
import argparse
from pathlib import Path

from optimizer_analyzer.pipeline import run


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("xml_files", nargs="*", help="report XML(s); default: newest in data/")
    parser.add_argument("-o", "--output-dir", default="output")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="also print the full report to the console")
    args = parser.parse_args()

    files = args.xml_files or [max(Path("data").glob("*.xml"), key=lambda p: p.stat().st_mtime)]
    for f in files:
        run(f, args.output_dir, verbose=args.verbose)


if __name__ == "__main__":
    main()
