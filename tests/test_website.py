"""Lightweight tests that run without Streamlit or TensorFlow installed."""
import ast
import hashlib
import io
import json
import unittest
from pathlib import Path

from contact_service import ContactMessage, make_eml, make_mailto, valid_email, verify_message, ContactConfigurationError
from backend import MODEL_PATH, MANIFEST_PATH, hash_file, model_output_names

ROOT = Path(__file__).resolve().parents[1]

class WebsiteTests(unittest.TestCase):
    def test_model_integrity_and_class_order_warning(self):
        manifest=json.loads(MANIFEST_PATH.read_text())
        self.assertEqual(hash_file(MODEL_PATH),manifest["sha256"])
        labels,verified=model_output_names(manifest)
        self.assertEqual(labels,("Glioma","Meningioma","No tumor","Pituitary"))
        self.assertFalse(verified)

    def test_multipage_routes_present(self):
        entry=(ROOT/"app.py").read_text()
        for path in ("home.py","analyze.py","about.py","contact.py","privacy.py"):
            self.assertIn(f'site_pages/{path}',entry)
            self.assertTrue((ROOT/"site_pages"/path).exists())
        self.assertIn('position="top"',entry)

    def test_all_source_files_compile(self):
        for fp in [ROOT/"app.py",ROOT/"site_theme.py",ROOT/"contact_service.py", *sorted((ROOT/"site_pages").glob("*.py"))]:
            with self.subTest(fp=fp.name):
                ast.parse(fp.read_text(encoding="utf-8"),filename=str(fp))

    def test_contact_valid_email(self):
        self.assertTrue(valid_email("hello@example.org"))
        for bad in ("", "a@", "abc\r\nBCC:bad@x.com", "Joe <joe@example.org>","not-an-email"):
            self.assertFalse(valid_email(bad))

    def test_contact_mailto_and_eml(self):
        message=ContactMessage("Researcher A","a@example.org","Project inquiry","I would like to discuss an academic evaluation.")
        draft=make_mailto("contact@example.org",message)
        self.assertTrue(draft.startswith("mailto:contact@example.org?"))
        self.assertIn("Project%20inquiry",draft)
        raw=make_eml(message,"contact@example.org")
        self.assertIn(b"Subject: Project inquiry",raw)
        self.assertIn(b"To: contact@example.org",raw)

    def test_contact_rejects_forged_headers(self):
        msg=ContactMessage("Student","a@example.org","Hi\nBcc: attacker@example.com","This is a legitimate length of message.")
        with self.assertRaises(ValueError):verify_message(msg)
        with self.assertRaises(ContactConfigurationError):make_mailto("not-an-email",ContactMessage("Student","a@example.org","Research question","This is a long enough question."))

if __name__ == "__main__":
    unittest.main()
