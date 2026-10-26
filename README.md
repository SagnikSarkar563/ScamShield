# ScamShield 🛡️

**An AI-powered scam detection and analysis platform focused on scams affecting users in India.**

ScamShield is a work-in-progress project that combines machine learning, text analysis, URL analysis, and a Flutter application to help users identify potentially fraudulent messages and suspicious online content.

> **Project status:** Under active development. Detection models are experimental and must not be treated as a guarantee that a message, link, or transaction is safe.

## Table of Contents

- [Overview](#overview)
- [Current Features](#current-features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Running the Application](#running-the-application)
- [Machine Learning](#machine-learning)
- [Testing and Evaluation](#testing-and-evaluation)
- [Limitations](#limitations)
- [Roadmap](#roadmap)
- [Contributing](#contributing)

## Overview

Online scams frequently use urgency, impersonation, suspicious links, fake rewards, and requests for sensitive information to manipulate users.

ScamShield aims to help users evaluate suspicious messages and understand potential warning signs through an accessible mobile interface backed by a Python API and machine learning models.

The project is designed with the Indian context in mind, with multilingual scam detection and broader fraud analysis planned as part of its development.

## Current Features

- **Message analysis:** Classifies submitted text using the existing machine learning pipeline.
- **URL analysis:** Uses heuristic analysis to identify potentially suspicious URL patterns.
- **Flutter interface:** Provides a mobile interface for submitting content and viewing analysis results.
- **FastAPI backend:** Exposes API functionality to the frontend.
- **Analysis history and settings UI:** Includes screens for history and settings.
- **Model evaluation tools:** Includes scripts for evaluating detection performance, language-specific behaviour, and unseen scam campaigns.
- **Experimental multilingual model:** Includes a candidate model using word-level and character-level TF-IDF features.

Features and detection quality are still being tested and improved.

## Technology Stack

| Component | Technologies |
|---|---|
| Mobile frontend | Flutter, Dart |
| Backend API | Python, FastAPI, Uvicorn |
| Machine learning | Scikit-learn, Logistic Regression, TF-IDF |
| Model storage | Joblib |
| Data processing | Pandas and Python ML tooling |
| Testing | Pytest and custom evaluation scripts |
| Version control | Git and GitHub |

## Architecture

```text
┌──────────────────────────┐
│     Flutter Frontend     │
│ Message input and results│
└────────────┬─────────────┘
             │ HTTP requests
             ▼
┌──────────────────────────┐
│      FastAPI Backend     │
│       /analyze API       │
└────────────┬─────────────┘
             │
       ┌─────┴──────┐
       ▼            ▼
┌────────────┐ ┌─────────────┐
│ Text-based │ │ URL heuristic│
│ ML model   │ │ analysis     │
└─────┬──────┘ └──────┬──────┘
      └───────┬───────┘
              ▼
┌──────────────────────────┐
│ Analysis response to app │
└──────────────────────────┘
```

This is a high-level representation of the current design. The exact analysis flow depends on the backend implementation and submitted content.

## Project Structure

```text
ScamShield/
├── backend/
│   ├── app/
│   │   ├── api/routes/
│   │   │   └── analyze.py
│   │   └── main.py
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── datasets/
│   ├── ScamShield_Benign_Control_Examples_5.csv
│   ├── independent_validation_pilot.csv
│   └── independent_validation_template.csv
├── dl/
│   └── scripts/
├── experiments/
│   ├── multilingual_candidate_smoke_tests.csv
│   ├── multilingual_candidate_summary.json
│   └── v5_evaluation_metrics.csv
├── frontend/
│   ├── lib/
│   │   ├── screens/
│   │   ├── services/
│   │   └── widgets/
│   └── pubspec.yaml
├── ml/
│   ├── models/
│   └── scripts/
├── check_models_recovery.py
├── test_model_inference.py
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

Install the following tools:

- Python 3.11 or a compatible Python version supported by the backend dependencies
- Flutter SDK and Dart
- Git
- Android Studio or another supported Flutter development environment
- An Android device or emulator for mobile testing

### 1. Clone the repository

```bash
git clone https://github.com/sagniksarkar563-ship-it/ScamShield.git
cd ScamShield
```

### 2. Set up the backend

From the project root, create and activate a Python virtual environment.

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
```

If PowerShell blocks virtual-environment activation, use the Python executable directly at `.venv\Scripts\python.exe`.

### 3. Start the backend

```powershell
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API should be available at:

- API base: `http://127.0.0.1:8000`
- Interactive API documentation: `http://127.0.0.1:8000/docs`
- Health endpoint: `http://127.0.0.1:8000/health`

These URLs assume the server starts successfully with the current configuration.

### 4. Set up the Flutter frontend

Open a second terminal at the repository root:

```powershell
cd frontend
flutter pub get
flutter doctor
```

To run on an Android emulator or connected device, configure the backend URL for that environment.

For an Android emulator, the backend host is commonly:

```text
http://10.0.2.2:8000
```

For a physical Android phone, use your computer's reachable local network IP address, for example:

```text
http://192.168.1.10:8000
```

Replace the example address with your actual computer IP. The phone and computer must be able to communicate over the network, and the firewall must permit the connection.

Run the app from the `frontend` directory:

```powershell
flutter run --dart-define=BACKEND_BASE_URL=http://10.0.2.2:8000
```

Use the appropriate URL for your device. Do not use the emulator address when testing on a physical phone.

## Machine Learning

### Existing baseline

The current baseline uses Logistic Regression with word-level TF-IDF features to classify text. Trained model artifacts and related utilities are stored under `ml/models/` and `ml/scripts/`.

### Experimental multilingual candidate

ScamShield also contains an experimental candidate using word-level and character-level TF-IDF features. It has undergone initial smoke testing, but further validation is needed.

The candidate should not replace the existing baseline until it performs reliably across representative languages, benign messages, and unseen scam campaigns.

### Model evaluation goals

- Accuracy, precision, recall, and F1-score
- Confusion matrix and false-positive/false-negative analysis
- Language-specific performance
- Performance on previously unseen scam campaigns
- Robustness against spelling variations and obfuscated text
- Comparison between the baseline and candidate models

Reported results should always specify the dataset, evaluation split, sample size, and test methodology.

## Testing and Evaluation

Run the backend regression tests from the `backend` directory:

```powershell
cd backend
python -m pytest -q
```

The current backend test suite covers the health endpoint, analysis response fields, empty input, URL-only requests, safe error handling, and risk-level thresholds.

### Pilot model comparison

The saved production V2 model and experimental multilingual candidate can be compared without retraining them. From the repository root, run:

```powershell
python ml/scripts/evaluate_pilot_models.py
```

The script reads `datasets/independent_validation_pilot.csv` and writes:

- `experiments/pilot_model_comparison_predictions.csv`
- `experiments/pilot_model_comparison_summary.json`

It refuses to overwrite existing output files. Review or archive previous results before rerunning it.

The pilot contains only 10 examples, and all independent-review statuses are pending. Its metrics are preliminary and must not be interpreted as estimates of real-world detection accuracy. The review workflow is tracked in `datasets/independent_validation_review_checklist.csv`.

Additional model and experiment scripts are available in `ml/scripts/` and `dl/scripts/`. Review each script's dataset requirements before running it.

## Limitations

- Scam detection is probabilistic and may produce false positives and false negatives.
- Multilingual performance has not yet been established across all intended languages.
- Experimental results require larger, more diverse, and independently evaluated datasets.
- URL heuristics cannot guarantee that a website is malicious or safe.
- The current project should not be used as the sole basis for financial, security, or law-enforcement decisions.
- Do not submit real passwords, OTPs, banking credentials, or other sensitive personal information during testing.

If a message appears suspicious, verify it through the organisation's official contact channels rather than using links or phone numbers supplied in the message.

## Roadmap

### Phase 1 — Foundation

- [x] Establish the monorepo structure
- [x] Create the FastAPI backend
- [x] Create the Flutter frontend
- [x] Integrate the baseline ML model
- [x] Establish Git and GitHub version control

### Phase 2 — Detection and evaluation

- [x] Implement the baseline text-classification pipeline
- [x] Connect the Flutter frontend to the backend
- [x] Add initial URL analysis
- [x] Create model evaluation scripts and pilot datasets
- [x] Train an experimental multilingual candidate
- [ ] Independently review pilot labels and improve multilingual classification reliability
- [ ] Expand and validate representative scam and benign datasets
- [ ] Evaluate false positives and false negatives systematically
- [ ] Validate performance on unseen campaigns
- [x] Add backend regression tests (6 tests currently pass)
- [x] Complete full frontend-to-backend end-to-end verification

### Future phases

- Add richer scam-category and tactic explanations
- Explore model compression and mobile inference where appropriate
- Investigate OCR-based analysis of scam screenshots
- Improve language coverage and handling of code-mixed text
- Add more robust evaluation, monitoring, and model versioning

Roadmap items are plans, not claims that those features are already implemented.

## Contributing

ScamShield is under active development. Contributions may include bug fixes, test cases, dataset documentation, evaluation improvements, and implementation of planned features.

Before contributing:

1. Create a branch for your change.
2. Keep experimental models separate from production inference.
3. Add or update tests where appropriate.
4. Document dataset sources, permissions, and limitations.
5. Never commit credentials, private user data, or unlicensed datasets.

## License

No license has been specified in this repository yet. Until a license is added, do not assume that the code is available for unrestricted reuse or redistribution.

## Repository

GitHub: https://github.com/sagniksarkar563-ship-it/ScamShield
