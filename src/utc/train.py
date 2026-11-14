"""Train the U-Net on chips.

Example:
    python -m utc.train --chips-dir data/chips --epochs 20 --out outputs/unet.pt
"""

from __future__ import annotations

import argparse
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from .dataset import ChipDataset, list_chip_files, split_files
from .metrics import scores_from_counts
from .model import bce_dice_loss, build_unet, save_checkpoint


def run_epoch(model, loader, device, optimizer=None):
    training = optimizer is not None
    model.train(training)
    counts = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
    loss_sum, n_batches = 0.0, 0
    with torch.set_grad_enabled(training):
        for x, y, valid in loader:
            x, y, valid = x.to(device), y.to(device), valid.to(device)
            logits = model(x)
            loss = bce_dice_loss(logits, y, valid)
            if training:
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
            pred = torch.sigmoid(logits) > 0.5
            truth, ok = y.bool(), valid.bool()
            counts["tp"] += int((pred & truth & ok).sum())
            counts["fp"] += int((pred & ~truth & ok).sum())
            counts["fn"] += int((~pred & truth & ok).sum())
            counts["tn"] += int((~pred & ~truth & ok).sum())
            loss_sum += float(loss.item())
            n_batches += 1
    return loss_sum / max(n_batches, 1), scores_from_counts(counts)


def fit(
    train_files,
    val_files,
    epochs: int = 10,
    batch_size: int = 8,
    lr: float = 1e-4,
    device: str | None = None,
    out_path: str | Path = "outputs/unet.pt",
    encoder: str = "resnet34",
    pretrained: bool = True,
    in_channels: int = 2,
    log=print,
):
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    model = build_unet(encoder, in_channels, pretrained).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    train_loader = DataLoader(ChipDataset(train_files, augment=True), batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(ChipDataset(val_files), batch_size=batch_size) if val_files else None

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    history, best_iou = [], -1.0
    for epoch in range(1, epochs + 1):
        train_loss, train_scores = run_epoch(model, train_loader, device, optimizer)
        row = {"epoch": epoch, "train_loss": train_loss, "train_iou": train_scores["iou"]}
        if val_loader is not None:
            val_loss, val_scores = run_epoch(model, val_loader, device)
            row.update(val_loss=val_loss, val_iou=val_scores["iou"], val_f1=val_scores["f1"])
            score = val_scores["iou"]
        else:
            score = train_scores["iou"]
        history.append(row)
        log(" ".join(f"{k}={v:.4f}" if isinstance(v, float) else f"{k}={v}" for k, v in row.items()))
        if score > best_iou:
            best_iou = score
            save_checkpoint(out_path, model, encoder, in_channels, {"score": score, "epoch": epoch})
    return history, best_iou


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--chips-dir", default=None, help="one folder of chips; a random 80/20 train/val split is made")
    p.add_argument("--train-dir", default=None, help="folder of training chips (use with --val-dir)")
    p.add_argument("--val-dir", default=None, help="folder of validation chips")
    p.add_argument("--epochs", type=int, default=10)
    p.add_argument("--batch-size", type=int, default=8)
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--encoder", default="resnet34")
    p.add_argument("--no-pretrained", action="store_true", help="skip ImageNet weights (works offline)")
    p.add_argument("--out", default="outputs/unet.pt")
    args = p.parse_args(argv)

    if args.train_dir:
        train_files = list_chip_files(args.train_dir)
        val_files = list_chip_files(args.val_dir) if args.val_dir else []
        if not train_files:
            raise SystemExit(f"no .npz chips found in {args.train_dir}")
    elif args.chips_dir:
        files = list_chip_files(args.chips_dir)
        if not files:
            raise SystemExit(f"no .npz chips found in {args.chips_dir}")
        train_files, val_files = split_files(files)
    else:
        raise SystemExit("give --train-dir (and --val-dir) or --chips-dir")
    print(f"{len(train_files)} train chips, {len(val_files)} val chips")
    _, best = fit(
        train_files,
        val_files,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        out_path=args.out,
        encoder=args.encoder,
        pretrained=not args.no_pretrained,
    )
    print(f"best score (val IoU if available): {best:.4f}; saved to {args.out}")


if __name__ == "__main__":
    main()
