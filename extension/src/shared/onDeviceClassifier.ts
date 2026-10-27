// Runs the ONNX email classifier inside the extension with onnxruntime-web. No server needed,
// and the email text never leaves the browser.
import * as ort from "onnxruntime-web/wasm";
import type { EmailData } from "./types";
import { DIM, emailText, featurize } from "./featurize";

export interface Prediction {
  label: string;
  confidence: number;
  scores: Record<string, number>;
}

const MODEL_DIR = "models/classifier/";
let ready: Promise<{ session: ort.InferenceSession; labels: string[] }> | null = null;

function load() {
  if (!ready) {
    ort.env.wasm.wasmPaths = chrome.runtime.getURL("ort/"); // WASM files are copied there at build
    ort.env.wasm.numThreads = 1; // extensions don't get SharedArrayBuffer, so no threads
    ready = (async () => {
      const meta = await (await fetch(chrome.runtime.getURL(MODEL_DIR + "labels.json"))).json();
      if (meta.dim !== DIM) throw new Error(`Model expects ${meta.dim} features, featurizer makes ${DIM}`);
      const bytes = await (await fetch(chrome.runtime.getURL(MODEL_DIR + "model.onnx"))).arrayBuffer();
      const session = await ort.InferenceSession.create(bytes, { executionProviders: ["wasm"] });
      return { session, labels: meta.labels as string[] };
    })();
    ready.catch(() => { ready = null; }); // allow a retry after a failure
  }
  return ready;
}

export async function classifyOnDevice(email: EmailData): Promise<Prediction> {
  const { session, labels } = await load();
  const input = new ort.Tensor("float32", featurize(emailText(email.subject, email.body)), [1, DIM]);
  const out = await session.run({ input });
  const probs = out[session.outputNames[1]].data as Float32Array; // [label, probabilities]
  const scores = Object.fromEntries(labels.map((l, i) => [l, probs[i]]));
  const best = labels.reduce((a, b) => (scores[b] > scores[a] ? b : a));
  return { label: best, confidence: scores[best], scores };
}

// Handy for debugging from the popup's DevTools console: await __classifyOnDevice({subject, body})
(globalThis as Record<string, unknown>).__classifyOnDevice = classifyOnDevice;
