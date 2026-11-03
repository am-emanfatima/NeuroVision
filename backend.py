"""Checked, in-memory inference with the original locally shipped Keras model.

No model scores are fabricated. This is research software, not a diagnostic tool.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

ROOT = Path(__file__).resolve().parent
MODEL_DIR = ROOT / "model"
MODEL_PATH = MODEL_DIR / "BRISC2025_EfficientNetB0_finetuned.keras"
MANIFEST_PATH = MODEL_DIR / "model_manifest.json"
APP_VERSION = "2.0.0"
MAX_BYTES = 30 * 1024 * 1024
Image.MAX_IMAGE_PIXELS = 60_000_000
UNVERIFIED_LABELS = tuple(f"Model output {i}" for i in range(1, 5))
# The supplied application manifest and example screenshot use these four names.
# Displaying the configured names does NOT prove their alignment with the
# particular output neurons. That requires the original training class_indices.
KNOWN_LABELS = {
    "glioma": "Glioma",
    "meningioma": "Meningioma",
    "no_tumor": "No tumor",
    "pituitary": "Pituitary",
}
RESEARCH_NOTICE = (
    "Research and educational use only. Not a medical device. Model scores are not "
    "calibrated clinical probabilities and must not be used to diagnose, rule out, "
    "monitor or make treatment decisions."
)


class AnalysisError(ValueError):
    pass


@dataclass(frozen=True)
class ImageDetails:
    filename: str
    width: int
    height: int
    format: str
    bytes_count: int


@dataclass(frozen=True)
class Prediction:
    image: ImageDetails
    scores: tuple[float, float, float, float]
    primary_index: int
    secondary_index: int
    model_sha256: str
    time_utc: str
    output_names: tuple[str, str, str, str]
    labels_verified: bool

    @property
    def top_score(self) -> float:
        return self.scores[self.primary_index] * 100

    @property
    def margin(self) -> float:
        return (self.scores[self.primary_index] - self.scores[self.secondary_index]) * 100


def read_image_bytes(content: bytes, name: str) -> tuple[Image.Image, ImageDetails]:
    if not content or len(content) > MAX_BYTES:
        raise AnalysisError("Image must be nonempty and at most 30 MB.")
    if not name.lower().endswith((".png", ".jpg", ".jpeg")):
        raise AnalysisError("Upload a JPEG or PNG file. DICOM is not supported.")
    try:
        with Image.open(io.BytesIO(content)) as source:
            if source.format not in ("JPEG", "PNG"):
                raise AnalysisError("Only actual JPEG and PNG images are supported.")
            fmt = source.format
            source.load()
            image = ImageOps.exif_transpose(source).convert("RGB")
    except (OSError, UnidentifiedImageError, Image.DecompressionBombError) as exc:
        raise AnalysisError("The image could not be safely decoded.") from exc
    if image.width < 32 or image.height < 32:
        raise AnalysisError("Images must be at least 32 by 32 pixels.")
    # The name is metadata only; no file is written to disk.
    safe_name = Path(name.replace('\\', '/')).name[:180]
    return image, ImageDetails(safe_name, image.width, image.height, fmt, len(content))


def preprocess(image: Image.Image) -> np.ndarray:
    # Saved model includes its own EfficientNetB0 scaling; do not divide by 255.
    image = image.resize((224, 224), resample=Image.Resampling.BILINEAR)
    return np.asarray(image, dtype=np.float32)[None, :, :, :]


def check_scores(raw: object) -> tuple[float, float, float, float]:
    arr = np.asarray(raw, dtype=np.float64)
    if arr.shape == (1, 4):
        arr = arr[0]
    if arr.shape != (4,) or not np.isfinite(arr).all():
        raise AnalysisError("The model returned an invalid prediction array.")
    if (arr < -1e-6).any() or (arr > 1 + 1e-6).any() or not np.isclose(arr.sum(), 1.0, atol=0.03):
        raise AnalysisError("The model did not return valid four-class normalized scores.")
    return tuple(float(val) for val in np.clip(arr, 0.0, 1.0))  # type: ignore[return-value]


def read_manifest() -> dict:
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise AnalysisError("The model manifest is unavailable or invalid.") from exc
    checksum = manifest.get("sha256")
    if not isinstance(checksum, str) or len(checksum) != 64:
        raise AnalysisError("The model manifest does not have a valid SHA-256 digest.")
    return manifest


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def model_output_names(manifest: dict) -> tuple[tuple[str, str, str, str], bool]:
    verified = manifest.get("class_order_verified_from_training_records") is True
    labels = manifest.get("class_order_in_application")
    # The application is now permitted to display the four configured class
    # names even before independent training-record verification. Keep the
    # verified flag FALSE, visibly labelled provisional, on every report.
    if (isinstance(labels, list) and len(labels) == 4 and
        all(isinstance(x, str) and x in KNOWN_LABELS for x in labels) and
        set(labels) == set(KNOWN_LABELS)):
        return tuple(KNOWN_LABELS[x] for x in labels), verified  # type: ignore[return-value]
    # If the manifest is incomplete or unsafe, do not guess medical names.
    return UNVERIFIED_LABELS, False


class InferenceEngine:
    """One shared, lock-protected Keras model instance for concurrent web sessions."""

    def __init__(self, path: Path = MODEL_PATH):
        self.path = path
        self._lock = threading.Lock()
        self.model = None
        self.sha256 = ""
        self.names = UNVERIFIED_LABELS
        self.labels_verified = False

    def load(self) -> "InferenceEngine":
        if not self.path.is_file():
            raise AnalysisError("The trained model file is missing from the deployment.")
        manifest = read_manifest()
        expected = manifest["sha256"]
        checksum = hash_file(self.path)
        if checksum.lower() != expected.lower():
            raise AnalysisError("The model file does not match the integrity manifest.")
        os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
        os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
        import tensorflow as tf  # noqa: delayed heavy import

        model = tf.keras.models.load_model(str(self.path), compile=False)
        if isinstance(model.input_shape, list) or tuple(model.input_shape[1:]) != (224, 224, 3):
            raise AnalysisError(f"Unexpected input tensor dimensions: {model.input_shape}")
        if isinstance(model.output_shape, list) or tuple(model.output_shape[1:]) != (4,):
            raise AnalysisError(f"Unexpected output dimensions: {model.output_shape}")
        self.model = model
        self.sha256 = checksum
        self.names, self.labels_verified = model_output_names(manifest)
        return self

    def analyze(self, image: Image.Image, details: ImageDetails) -> Prediction:
        if self.model is None:
            raise AnalysisError("The model has not loaded.")
        pixels = preprocess(image)
        with self._lock:
            raw_scores = self.model.predict(pixels, verbose=0)
        scores = check_scores(raw_scores)
        ordered = np.argsort(np.asarray(scores))[::-1]
        return Prediction(
            details, scores, int(ordered[0]), int(ordered[1]), self.sha256,
            datetime.now(timezone.utc).isoformat(timespec="seconds"),
            self.names, self.labels_verified,
        )
