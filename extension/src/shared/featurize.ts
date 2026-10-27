// TypeScript copy of ml/featurize.py. It MUST produce exactly the same numbers as the Python
// version the model was trained with; ml/evaluation/check_parity.mjs verifies this.
export const DIM = 4096;
const TOKEN_RE = /[a-z0-9]+/g;
const encoder = new TextEncoder();

export function fnv1a(text: string): number {
  let h = 0x811c9dc5;
  for (const byte of encoder.encode(text)) {
    h ^= byte;
    h = Math.imul(h, 0x01000193) >>> 0; // 32-bit multiply, kept unsigned like Python's & 0xFFFFFFFF
  }
  return h >>> 0;
}

export function tokens(text: string): string[] {
  const words = text.toLowerCase().match(TOKEN_RE) ?? [];
  const out = [...words];
  for (let i = 0; i + 1 < words.length; i++) out.push(`${words[i]}_${words[i + 1]}`);
  for (const word of words) {
    const w = `<${word}>`;
    for (let i = 0; i < Math.max(1, w.length - 3); i++) out.push(w.slice(i, i + 4));
  }
  return out;
}

export function featurize(text: string): Float32Array {
  const v = new Float32Array(DIM);
  for (const tok of tokens(text)) v[fnv1a(tok) % DIM] += 1;
  let norm = 0;
  for (let i = 0; i < DIM; i++) {
    if (v[i]) {
      v[i] = Math.log1p(v[i]);
      norm += v[i] * v[i];
    }
  }
  norm = Math.sqrt(norm);
  if (norm) for (let i = 0; i < DIM; i++) v[i] /= norm;
  return v;
}

export const emailText = (subject: string, body: string) => `${subject} ${subject} ${body}`;
