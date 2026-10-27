// Verifies the extension computes the same features and predictions as Python.
// Run from the project root:
//   python ml/evaluation/export_reference.py
//   node --experimental-strip-types ml/evaluation/check_parity.mjs
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { DIM, emailText, featurize } from "../../extension/src/shared/featurize.ts";

const require = createRequire(import.meta.url + "/../../../extension/");
const ort = require("onnxruntime-web");
const ref = JSON.parse(readFileSync(new URL("./reference.json", import.meta.url)));
const model = readFileSync(new URL("../../extension/public/models/classifier/model.onnx", import.meta.url));
const session = await ort.InferenceSession.create(model);

let worstFeature = 0, worstProb = 0, labelMismatches = 0;
const argmax = (a) => a.indexOf(Math.max(...a));
for (const r of ref) {
  const v = featurize(emailText(r.subject, r.body));
  for (let i = 0; i < DIM; i++) worstFeature = Math.max(worstFeature, Math.abs(v[i] - (r.features[i] ?? 0)));
  const out = await session.run({ input: new ort.Tensor("float32", v, [1, DIM]) });
  const probs = Array.from(out[session.outputNames[1]].data);
  probs.forEach((p, i) => (worstProb = Math.max(worstProb, Math.abs(p - r.probs[i]))));
  if (argmax(probs) !== argmax(r.probs)) labelMismatches++;
}
console.log(`${ref.length} emails | max feature diff ${worstFeature.toExponential(2)} | max probability diff ${worstProb.toExponential(2)} | label mismatches ${labelMismatches}`);
process.exit(worstFeature < 1e-5 && labelMismatches === 0 ? 0 : 1);
