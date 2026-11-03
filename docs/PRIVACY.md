# NeuroVision AI — Streamlit hosting privacy notice

This edition is a **server-hosted** application, which is different from the original desktop application. When you upload a JPEG/PNG, the selected image is transmitted to the Streamlit host for processing. A hosted deployment may have platform logs, access records, administrators or retention rules not controlled by the project author.

The application itself processes uploaded image bytes in memory, does not intentionally write them to the server filesystem, does not include telemetry, and does not create a patient database. The uploaded file may remain in Streamlit session memory while your session is active. TensorFlow weights are loaded locally by the host. PDF and CSV reports are created in memory after a real completed prediction. The PDF includes any patient information typed into the form and the uploaded filename, dimensions, time, model checksum and numeric scores. The original image pixels are included in the PDF **only** if the user explicitly opts in to the optional image appendix. The CSV contains prediction data but **no patient form details**. The app does **not** remove personal identifiers from image pixels or filenames.

Use only authorized images suitable for the server where the app is deployed. For public hosted apps, do not upload identifiable patient data unless a properly reviewed environment, lawful basis, privacy controls and approvals are in place. No clinical use is authorized or established by this package.

Typed patient metadata is kept in Streamlit session state and may remain in the server-hosted session memory while the session is active. The software does not create a patient database or write patient details to disk. Do not use a public host as a clinical patient record system.
