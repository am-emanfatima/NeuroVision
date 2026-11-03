"""Execute on the target server after installing dependencies to verify the real .keras file."""
import numpy as np
from backend import InferenceEngine, check_scores

engine = InferenceEngine().load()
scores = engine.model.predict(np.zeros((1, 224, 224, 3), dtype=np.float32), verbose=0)
check_scores(scores)
print("PASS: saved model loaded, integrity verified and actual TensorFlow forward pass completed")
print("Class labels verified:", engine.labels_verified)
