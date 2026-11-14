"""Command-line helpers for Sen1Floods11.

    python scripts/sen1floods11.py download --root data/sen1floods11
    python scripts/sen1floods11.py prepare  --root data/sen1floods11 --out data/chips
    python scripts/sen1floods11.py evaluate --root data/sen1floods11 --split test --checkpoint outputs/unet.pt
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .sen1floods11 import SPLIT_FILES, Paths, download, evaluate_split, prepare_chips


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("download", help="download split CSVs and chips (about 650 MB for everything)")
    d.add_argument("--root", default="data/sen1floods11")
    d.add_argument("--limit", type=int, default=None, help="only the first N pairs per split (quick test)")
    d.add_argument(
        "--splits", nargs="+", default=["train", "valid", "test"], choices=list(SPLIT_FILES),
        help="which splits to download (add 'bolivia' for the out-of-event test)",
    )

    pr = sub.add_parser("prepare", help="cut scenes into training chips, one folder per split")
    pr.add_argument("--root", default="data/sen1floods11")
    pr.add_argument("--out", default="data/chips")
    pr.add_argument("--size", type=int, default=256)

    e = sub.add_parser("evaluate", help="scene-level IoU/F1 for baselines and (optionally) the CNN")
    e.add_argument("--root", default="data/sen1floods11")
    e.add_argument("--split", default="test", choices=list(SPLIT_FILES))
    e.add_argument("--checkpoint", default=None)
    e.add_argument("--limit", type=int, default=None)
    e.add_argument("--device", default="cpu")
    e.add_argument("--out", default=None, help="optional JSON file for the results")

    args = p.parse_args(argv)
    if args.cmd == "download":
        download(args.root, splits=tuple(args.splits), limit=args.limit)
    elif args.cmd == "prepare":
        print(json.dumps(prepare_chips(Paths.from_root(args.root), args.out, args.size), indent=2))
    else:
        res = evaluate_split(Paths.from_root(args.root), args.split, args.checkpoint, args.device, args.limit)
        text = json.dumps(res, indent=2)
        print(text)
        if args.out:
            Path(args.out).parent.mkdir(parents=True, exist_ok=True)
            Path(args.out).write_text(text)


if __name__ == "__main__":
    main()
