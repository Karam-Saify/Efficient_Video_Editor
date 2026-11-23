// Every external URL the bench loads. Exact versions and Hugging Face commit revisions only (H-0030).
// bench/README.md lists the same URLs; tests/unit/test_bench_static.py checks that the two agree.

export const TRANSFORMERS_URL = "https://cdn.jsdelivr.net/npm/@huggingface/transformers@4.3.2/dist/transformers.min.js";
// transformers.min.js fetches its ONNX Runtime wasm from this pinned package (its package.json dependency).
export const ORT_WASM_BASE = "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.31.0-dev.20260914-8d85527a0/dist/";
export const MP4_MUXER_URL = "https://cdn.jsdelivr.net/npm/mp4-muxer@5.2.2/build/mp4-muxer.mjs";

export const FONT_ARABIC_URL = "https://cdn.jsdelivr.net/npm/@fontsource/noto-sans-arabic@5.3.0/files/noto-sans-arabic-arabic-400-normal.woff2";
export const FONT_LATIN_URL = "https://cdn.jsdelivr.net/npm/@fontsource/noto-sans@5.3.0/files/noto-sans-latin-400-normal.woff2";

// Whisper weights: Hugging Face hub, Apache-2.0, pinned to a commit so every phone loads the same bytes.
export const MODELS = {
  "whisper-base": { id: "Xenova/whisper-base", revision: "64da57285918e20ea79ea5c88eed7197933abaa8" },
  "whisper-tiny": { id: "Xenova/whisper-tiny", revision: "5332fcc35e32a33b86612b9a57a89be7906102b1" },
};

// Speech sample: JFK inaugural address excerpt (11 s), the sample used by the Whisper and transformers.js
// examples. Licence reasoning in bench/README.md ("Test media").
export const SPEECH_SAMPLE_URL = "https://huggingface.co/datasets/Xenova/transformers.js-docs/resolve/542437c29cc5273cfd29e25c77696f2b349badd7/jfk.wav";
export const SPEECH_SAMPLE_REFERENCE = "And so my fellow Americans, ask not what your country can do for you, ask what you can do for your country.";
