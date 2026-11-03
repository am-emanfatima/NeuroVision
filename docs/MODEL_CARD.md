# Included model — release information

| Item | Current implementation |
|---|---|
| Architecture | Keras EfficientNetB0 transfer-learning classifier |
| Included artifact | `BRISC2025_EfficientNetB0_finetuned.keras` |
| Model input | RGB image, 224 × 224 × 3, float32 |
| Image preprocessing | JPEG/PNG decode, apply EXIF orientation, RGB conversion, bilinear resize, retain 0–255 pixel range |
| Built-in scaling | The saved EfficientNetB0 backbone includes a Rescaling layer |
| Output | Four softmax model scores, not calibrated clinical probabilities |
| Labels displayed by web app | Glioma, Meningioma, No tumor, Pituitary (provisional mapping; unverified class indices) |
| Intended use | Research and education only, not patient care |
| Clinical performance | **Not verified in this package** |

## Required release review

- **The app's class-index order has not been verified against the original training program**. The Keras file contains a four-neuron output layer but does not independently prove the text mapping. Category names are now displayed as **provisional configured labels** at the user's request. Confirm the output order against the training data generator's `class_indices` or an equivalent original artifact **before treating the labels as reliably mapped**. The deployed app, exported CSV and report must continue to show the unverified-label warning until then.
- Confirm the training/validation image pipeline, including interpolation, colour channels, normalization and external validation on previously unseen data. A successful model load or prediction on a synthetic array does **not** measure accuracy.
- Assess provenance, weights/dataset redistribution rights, leakage/bias, representativeness, failure cases, performance, limitations and appropriate regulatory classification for intended jurisdictions.
- Never interpret the `no_tumor` class as medically excluding a tumour. Retain the research-only warnings in any derivative product.

`model/model_manifest.json` includes the actual included file's SHA-256 hash for file-integrity checking. The hash alone does not establish ownership, accuracy or safety.
