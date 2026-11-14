"""U-Net water segmentation model and loss."""

from __future__ import annotations

import torch
import torch.nn.functional as F


def build_unet(encoder: str = "resnet34", in_channels: int = 2, pretrained: bool = True):
    """U-Net with a ResNet encoder (default ResNet-34).

    pretrained=True downloads ImageNet weights (needs internet). The first layer is adapted to
    `in_channels` (2 for VV + VH). Output is one logit per pixel (water vs not water).
    """
    import segmentation_models_pytorch as smp

    return smp.Unet(
        encoder_name=encoder,
        encoder_weights="imagenet" if pretrained else None,
        in_channels=in_channels,
        classes=1,
    )


def bce_dice_loss(
    logits: torch.Tensor,
    targets: torch.Tensor,
    valid: torch.Tensor | None = None,
    dice_weight: float = 1.0,
    eps: float = 1e-6,
) -> torch.Tensor:
    """Binary cross-entropy plus Dice loss, ignoring pixels where `valid` is 0.

    All tensors have shape (B, 1, H, W). Dice helps when water is a small share of the pixels.
    """
    if valid is None:
        valid = torch.ones_like(targets)
    valid = valid.float()
    bce = F.binary_cross_entropy_with_logits(logits, targets, reduction="none")
    bce = (bce * valid).sum() / valid.sum().clamp(min=1.0)

    p = torch.sigmoid(logits) * valid
    t = targets * valid
    inter = (p * t).sum(dim=(1, 2, 3))
    denom = p.sum(dim=(1, 2, 3)) + t.sum(dim=(1, 2, 3))
    dice = 1.0 - (2.0 * inter + eps) / (denom + eps)
    return bce + dice_weight * dice.mean()


def save_checkpoint(path, model, encoder: str, in_channels: int, extra: dict | None = None) -> None:
    payload = {"state_dict": model.state_dict(), "encoder": encoder, "in_channels": in_channels}
    if extra:
        payload.update(extra)
    torch.save(payload, path)


def load_model(path, device: str = "cpu"):
    """Load a model saved by `save_checkpoint` (no internet needed)."""
    ckpt = torch.load(path, map_location=device)
    model = build_unet(ckpt["encoder"], ckpt["in_channels"], pretrained=False)
    model.load_state_dict(ckpt["state_dict"])
    return model.to(device).eval()
