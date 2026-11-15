import re
from pathlib import Path


def test_honest_paragraph_does_not_claim_moroccan_cnn_iou_or_nearby_dates():
    report_path = (
        Path(__file__).resolve().parents[1]
        / "experiments"
        / "HONEST_PARAGRAPH.md"
    )
    text = report_path.read_text(encoding="utf-8")

    moroccan_cnn_iou = re.compile(
        r"(?is)(?:morocc\w*.{0,80}cnn.{0,40}iou|"
        r"cnn.{0,40}iou.{0,80}morocc\w*)"
    )
    assert not moroccan_cnn_iou.search(text)
    assert "nearby dates" not in text.lower()
