"""Trains the email classifier and exports it to ONNX for the Chrome extension.

Run from the project root:
    python ml/data/build_dataset.py
    python ml/training/train_classifier.py
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np
from scipy.sparse import csr_matrix
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ml"))
from featurize import DIM, email_text, sparse_features  # noqa: E402

DATA = ROOT / "ml" / "data"
OUT_DIR = ROOT / "extension" / "public" / "models" / "classifier"
LABELS = ["Urgent", "Opportunity", "Meeting", "Promotional", "Normal"]


def load(name: str):
    with open(DATA / name, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    data, cols, ptr = [], [], [0]
    for r in rows:
        for k, x in sparse_features(email_text(r["subject"], r["body"])).items():
            cols.append(k)
            data.append(x)
        ptr.append(len(cols))
    X = csr_matrix((np.array(data, dtype=np.float32), cols, ptr), shape=(len(rows), DIM))
    y = np.array([LABELS.index(r["label"]) for r in rows])
    return X, y


def evaluate(model, name: str) -> dict:
    X, y = load(name)
    pred = model.predict(X)
    print(f"\n=== {name} ({len(y)} emails) ===")
    print(classification_report(y, pred, target_names=LABELS, digits=3, zero_division=0))
    return {"accuracy": round(float((pred == y).mean()), 3),
            "macro_f1": round(float(f1_score(y, pred, average="macro")), 3)}


def main():
    X, y = load("train.csv")
    model = LogisticRegression(max_iter=3000, C=16.0, class_weight="balanced")
    model.fit(X, y)

    report = {"test": evaluate(model, "test.csv"), "realistic": evaluate(model, "realistic_eval.csv")}

    # Export: input is the featurized vector, outputs are the label index and class probabilities.
    onnx_model = convert_sklearn(
        model,
        initial_types=[("input", FloatTensorType([None, DIM]))],
        options={id(model): {"zipmap": False}},
        target_opset=15,
    )
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "model.onnx").write_bytes(onnx_model.SerializeToString())
    (OUT_DIR / "labels.json").write_text(json.dumps({"labels": LABELS, "dim": DIM, "metrics": report}, indent=2))
    print(f"\nSaved {OUT_DIR / 'model.onnx'} ({(OUT_DIR / 'model.onnx').stat().st_size // 1024} KB)")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
