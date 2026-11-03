# NeuroVision AI — Premium Streamlit Research Website

A modern, responsive, multi-page Streamlit application powered by the **original user-supplied EfficientNetB0 `.keras` model**. Includes a polished home page, a real MRI research inference workflow, an explanatory About page, a functional Contact workflow, and a Privacy & Ethics page.

**This is educational/research software—not an approved medical device and not a tool for diagnosis, screening or treatment.** A patient-style PDF produced here is always **unsigned and non-diagnostic**.

## Website pages

| Page | What works |
| --- | --- |
| **Home** | Responsive hero, navigation/CTAs, overview, workflow, four configured class names, trust notices |
| **MRI Analysis** | Validated PNG/JPEG upload, image preview, original model inference, normalized score visualization, class rankings, optional patient fields, research PDF and CSV downloads |
| **About** | Architecture, data flow, model file checksum, configured class names, limitations |
| **Contact** | Validated contact form, optional SMTP delivery, mailto handoff, or `.eml` draft download when unconfigured |
| **Privacy & Ethics** | Data handling, constraints and responsible-use disclosures |

## 1. Run locally

Install **Python 3.12, 64-bit**, then from this extracted project folder:

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

Use a browser to visit the local address printed by Streamlit (commonly `http://localhost:8501`). The initial load of TensorFlow may be slower than subsequent inferences. CPU inference is supported. Internet access may be needed to install Python packages and fetch the optional web fonts; system fonts are used if web fonts cannot load.

The root `app.py` uses `st.Page` and `st.navigation(position="top")`; keep the `site_pages/` folder intact.

## 2. Deploy on Streamlit Community Cloud

1. Create a new GitHub repository and upload **all project files**, including `model/BRISC2025_EfficientNetB0_finetuned.keras` (Git LFS may be used if you prefer; ensure the actual binary is available to the deployed app rather than an unresolved pointer).
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) and select **Create app** from your repository.
3. Main module path: `app.py`. Python environment: **3.12** (or a compatible version available in your deployment).
4. Deploy. The model is not downloaded remotely; it is read from the included `model/` folder and SHA-256 verified before inference.
5. Optional contact email: add the following settings in **App settings → Secrets**. Do **not** commit real passwords to GitHub.

```toml
[contact]
recipient = "project-contact@example.com"
sender = "project-contact@example.com"
host = "smtp.your-mail-provider.example"
port = 587
username = "project-contact@example.com"
password = "YOUR_PROVIDER_APP_PASSWORD"
use_ssl = false
```

**Replace all example values with real information from your own mail provider.** For SSL on port 465 use `use_ssl = true`. With **only** `recipient`, the Contact form opens a prepared mailto draft; it **does not** claim it sent an email. With no email settings, users can download a prepared `.eml` draft. For real SMTP sending, all required secrets must be set and the host must permit outbound SMTP connections. Some cloud hosting providers block SMTP ports; test your chosen provider after deploying.

> Public hosting is not a regulated clinical environment. Avoid identifiable patient data and use de-identified examples unless appropriate consent, institutional approval and a privacy/security program are established.

## 3. Model mapping — important caveat

The existing manifest in `model/model_manifest.json` configures four classes in this order:

| Output index | Configured label |
| --- | --- |
| 0 | Glioma |
| 1 | Meningioma |
| 2 | No tumor |
| 3 | Pituitary |

**This order is provisional.** We verified that the model binary matches the shipped manifest hash. **The `.keras` archive does not itself establish the training class-index order.** Obtain the `class_names` or `class_indices` variable from the exact Kaggle training notebook before changing the manifest field `class_order_verified_from_training_records` to `true`. Do not assume matching dataset category names proves a correct output-to-category mapping.

Use `python check_model.py` for the provided model check (requires TensorFlow).

## 4. Files

```text
app.py                          # Main Streamlit page router / theme
site_theme.py                   # Shared premium design system
site_pages/
  home.py                       # Landing page
  analyze.py                    # Real model inference + exports
  about.py                      # Methodology/model transparency
  contact.py                    # Contact form with delivery fallback
  privacy.py                    # Privacy and ethical use
backend.py                      # Validated image processing + Keras inference
web_reports.py                  # Safe ReportLab PDF + CSV generator
contact_service.py              # SMTP/mailto/.eml contact helpers
model/
  BRISC2025_EfficientNetB0_finetuned.keras
  model_manifest.json
.streamlit/
  config.toml                   # Dark theme and upload limits
  secrets.example.toml          # Example, no real credentials
assets/                         # Original application branding
requirements.txt
START_HERE.txt
run_windows.bat / run_linux_mac.sh
docs/                           # Sample report and model/privacy notes
tests/                          # Source, data, report and integrity tests
```

## 5. Testing

```bash
python -m unittest discover -s tests -v
python -m compileall -q app.py site_theme.py contact_service.py backend.py web_reports.py site_pages
```

Tests cover original model-file hash, image processing, fake model-interface testing, class-label behavior, CSV and PDF exports, safe text output, contact validation, navigation presence and Python syntax. **Running these tests does not establish clinical accuracy or replace a live browser/deployment test.** Test Streamlit pages and email delivery on your chosen deployment to confirm network and provider compatibility.

## 6. Data handling and safety

- Predictions: generated by the **real bundled Keras model** when an image is analyzed.
- Image processing: performed in memory; the app source does not intentionally save uploads to disk.
- Patient fields: optional and used only in the PDF; nothing is inferred or invented by the app.
- CSV: contains the four scores and model metadata, not patient identity fields.
- Contact: SMTP when configured; otherwise email draft only. No deceptive “message sent” confirmation.
- Research report: clinician findings **not assessed**; unsigned, non-diagnostic with research disclaimer.
- Limitations: single uploaded raster image; no DICOM or whole-examination interpretation; no validated clinical probabilities.

## 7. Research publication readiness

The UI is designed for professional presentation, but a **scientifically publishable medical AI study** requires more than a good interface. Before making claims of clinical readiness, obtain a documented training class mapping, dataset source approval, independent validation, patient-data governance, quantitative performance including uncertainty and subgroup assessment, clinician oversight and institutional review as applicable.

© NeuroVision AI research prototype. No institutional affiliation or clinical authorization is implied.
