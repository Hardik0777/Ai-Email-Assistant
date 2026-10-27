"""Writes reference features + predictions from Python, for the TypeScript parity check."""
import csv
import json
import sys
from pathlib import Path

import numpy as np
import onnxruntime as rt

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ml"))
from featurize import email_text, sparse_features  # noqa: E402

rows = []
for name in ["test.csv", "realistic_eval.csv"]:
    with open(ROOT / "ml" / "data" / name, encoding="utf-8") as f:
        rows += list(csv.DictReader(f))

model = rt.InferenceSession(str(ROOT / "extension/public/models/classifier/model.onnx"))
out = []
for r in rows:
    feats = sparse_features(email_text(r["subject"], r["body"]))
    x = np.zeros((1, 4096), dtype=np.float32)
    for k, v in feats.items():
        x[0, k] = v
    _, probs = model.run(None, {"input": x})
    out.append({"subject": r["subject"], "body": r["body"],
                "features": {str(k): v for k, v in feats.items()}, "probs": probs[0].tolist()})

dest = ROOT / "ml" / "evaluation" / "reference.json"
dest.write_text(json.dumps(out))
print(f"wrote {len(out)} reference emails to {dest.name}")
