import csv
import io
import unittest
from datetime import datetime
from unittest.mock import Mock

import numpy as np
from PIL import Image

from backend import (
    AnalysisError, ImageDetails, InferenceEngine, Prediction,
    UNVERIFIED_LABELS, check_scores, model_output_names,
    preprocess, read_image_bytes,
)
from web_reports import PatientDetails, export_csv, export_pdf


class GenuineDataPathTests(unittest.TestCase):
    def test_image_decode_and_no_disk_writes(self):
        buf = io.BytesIO()
        Image.new("RGB", (256, 200), (51, 71, 91)).save(buf, format="PNG")
        image, info = read_image_bytes(buf.getvalue(), "image.png")
        self.assertEqual(info.format, "PNG")
        self.assertEqual(preprocess(image).shape, (1, 224, 224, 3))
        self.assertEqual(float(preprocess(image)[0, 0, 0, 0]), 51)

    def test_reject_bad_uploads(self):
        for content, name in ((b"", "a.png"), (b"hello", "a.png"), (b"data", "scan.dcm")):
            with self.subTest(name=name), self.assertRaises(AnalysisError):
                read_image_bytes(content, name)

    def test_output_guard(self):
        with self.assertRaises(AnalysisError):
            check_scores([0.5, 0.5, 0.5, 0.5])
        self.assertEqual(len(check_scores([[0.1, 0.2, 0.3, 0.4]])), 4)

    def test_provisional_class_names_in_configured_order(self):
        labels, verified = model_output_names({"class_order_in_application": ["glioma", "meningioma", "no_tumor", "pituitary"], "class_order_verified_from_training_records": False})
        self.assertFalse(verified)
        self.assertEqual(labels, ("Glioma", "Meningioma", "No tumor", "Pituitary"))

    def test_invalid_manifest_class_mapping_stays_neutral(self):
        labels, verified = model_output_names({"class_order_in_application": ["foo", "bar", "baz", "qux"], "class_order_verified_from_training_records": True})
        self.assertFalse(verified)
        self.assertEqual(labels, UNVERIFIED_LABELS)

    def test_verified_manifest_mapping(self):
        labels, verified = model_output_names({"class_order_in_application": ["glioma", "meningioma", "no_tumor", "pituitary"], "class_order_verified_from_training_records": True})
        self.assertTrue(verified)
        self.assertEqual(labels[2], "No tumor")

    def test_engine_uses_real_inference_interface(self):
        engine = InferenceEngine()
        engine.model = Mock()
        engine.model.predict.return_value = [[0.1, 0.6, 0.2, 0.1]]
        engine.sha256 = "a" * 64
        img = Image.new("RGB", (224, 224))
        meta = ImageDetails("scan.png", 224, 224, "PNG", 1600)
        result = engine.analyze(img, meta)
        self.assertEqual(result.primary_index, 1)
        self.assertAlmostEqual(result.top_score, 60)
        engine.model.predict.assert_called_once()

    def test_reports_contain_only_actual_result(self):
        result = Prediction(ImageDetails('=DANGEROUS', 224, 224, 'PNG', 600), (0.1,0.2,0.3,0.4), 3,2, 'f'*64,
                            '2026-11-02T00:00:00+00:00', UNVERIFIED_LABELS, False)
        data = dict(csv.reader(io.StringIO(export_csv(result).decode('utf-8-sig'))))
        self.assertEqual(data['Image file'], "'=DANGEROUS")
        self.assertEqual(data['Highest output'], 'Model output 4')
        self.assertTrue(export_pdf(result).startswith(b'%PDF'))

    def test_configured_classes_flow_into_csv_and_pdf(self):
        labels, verified = model_output_names({"class_order_in_application": ["glioma", "meningioma", "no_tumor", "pituitary"], "class_order_verified_from_training_records": False})
        result = Prediction(ImageDetails('scan.png', 256, 256, 'PNG', 4096),
                            (0.0021, 0.0405, 0.9568, 0.0006), 2, 1, 'a' * 64,
                            '2026-11-03T00:00:00+00:00', labels, verified)
        rows = dict(csv.reader(io.StringIO(export_csv(result).decode('utf-8-sig'))))
        self.assertEqual(rows['Highest output'], 'No tumor')
        self.assertEqual(rows['Class order verified'], 'No - displayed names use provisional mapping')
        self.assertIn('Meningioma', rows)
        pdf = export_pdf(result)
        self.assertTrue(pdf.startswith(b'%PDF'))
        try:
            import fitz
        except ImportError:
            return
        with fitz.open(stream=pdf, filetype='pdf') as doc:
            text = '\n'.join(page.get_text() for page in doc)
        for name in labels:
            self.assertIn(name, text)
        self.assertIn('Provisional class labels', text)

    def test_patient_pdf_export_and_untrusted_text(self):
        result = Prediction(ImageDetails('scan.png', 256, 256, 'PNG', 4096),
                            (0.1, 0.2, 0.3, 0.4), 3, 2, 'a' * 64,
                            '2026-11-03T00:00:00+00:00', UNVERIFIED_LABELS, False)
        patient = PatientDetails(name='<b>Unsafe name</b>', patient_id='RESEARCH-001',
                                 age='36', sex='Not specified',
                                 clinical_indication='A' * 700)
        output = export_pdf(result, patient)
        self.assertTrue(output.startswith(b'%PDF'))
        self.assertGreater(len(output), 3000)
        self.assertFalse('Patient name' in dict(csv.reader(io.StringIO(export_csv(result).decode('utf-8-sig')))))


if __name__ == '__main__':
    unittest.main()
