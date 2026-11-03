# Provisional class-to-output mapping — verification required

At the user's request, this app shows the four human-readable class names in the same configured order already recorded in `model/model_manifest.json`:

| Zero-based output | Human-readable name |
|---|---|
| 0 | Glioma |
| 1 | Meningioma |
| 2 | No tumor |
| 3 | Pituitary |

This is **not an assertion** that those names are correctly aligned with the trained model's output neurons. The Keras archive stores four output neurons but no trustworthy text labels. The supplied screenshot displays these four names, but that screenshot is not proof of class ordering for this specific saved model. The manifest deliberately retains `"class_order_verified_from_training_records": false`. The UI/PDF/CSV show an explicit unverified mapping warning.

To verify: locate the original model-training notebook and read the exact training generator's `class_indices`, dataset class-to-index dictionary, `class_names`/`ImageDataGenerator` directory order, or another immutable, sourced training artifact associated with these precise weights. Compare all four positions with the mapping above. Only after confirmation should `class_order_verified_from_training_records` be changed to `true`. Do not infer output mapping from predictions on selected images or a generic alphabetical convention.

The labels are research-only. Model scores are not clinically calibrated probabilities. In particular, a "No tumor" score does not rule out disease.
