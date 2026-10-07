\# Sahayak Verification Engine



> AI-assisted pre-submission document verification for scholarship applications.



Sahayak is a policy-driven verification engine designed to help students identify document errors, missing records, inconsistent information, and scholarship eligibility issues before submitting an application.



It combines OCR, document classification, structured field extraction, configurable scholarship rules, cross-document consistency checks, and human-in-the-loop resolution.



\---



\## Problem



Scholarship applications can be rejected or delayed because of small but important document issues, such as:



\* Name variations across documents

\* Incorrect or missing documents

\* Incorrect academic percentage formats

\* Income exceeding the scholarship limit

\* Missing mandatory certificates

\* Unclear reasons for application rejection



Students often discover these problems only after submission.



\## Solution



Sahayak acts as a verification layer before submission.



It:



1\. Identifies uploaded document types.

2\. Extracts important fields using OCR.

3\. Applies scholarship-specific eligibility rules.

4\. Compares identity information across documents.

5\. Detects potential mismatches.

6\. Explains why an issue was flagged.

7\. Requests human confirmation when required.

8\. Re-evaluates the application after resolution.

9\. Shows whether the application is ready for submission.



\### Core idea



\*\*AI detects → explains → human confirms → system re-evaluates\*\*



Sahayak assists the applicant; it does not make the final scholarship decision.



\---



\## Key Features



\### Document Verification



Supports verification workflows for documents such as:



\* Aadhaar

\* 12th Marksheet

\* Income Certificate

\* Other scholarship-related documents supported by the configured rules



\### OCR \& Field Extraction



The backend extracts structured information from uploaded documents, including:



\* Student name

\* Date of birth

\* Academic percentage

\* Annual family income

\* Other document-specific fields



\### Scholarship Rule Engine



Scholarship policies are configurable instead of hard-coded into the frontend.



The demo includes a \*\*National Merit-cum-Means Scholarship\*\* profile with:



\* Family income ceiling: ₹2,50,000 per year

\* Minimum academic percentage: 60%

\* Required documents:



&#x20; \* Aadhaar

&#x20; \* 12th Marksheet

&#x20; \* Income Certificate



\### Cross-Document Verification



Sahayak compares extracted identity information across documents and identifies:



\* Consistent values

\* Potential spelling variations

\* Hard mismatches

\* Missing required information



\### Human-in-the-Loop



Sahayak does not silently assume that a mismatch is correct or incorrect.



When a significant discrepancy is detected, the user can provide a human confirmation note.



Example:



\*\*Aadhaar:\*\* Hana Sharma

\*\*12th Marksheet:\*\* Hana Verma



The system flags the discrepancy and waits for human confirmation before considering the application ready.



\### Application Readiness



The dashboard provides a clear final status:



\* `READY\_FOR\_SUBMISSION`

\* `ACTION\_REQUIRED`

\* `INCOMPLETE`

\* `IN\_REVIEW`



\---



\## System Workflow



```text

Uploaded Documents

&#x20;       │

&#x20;       ▼

Document Classification

&#x20;       │

&#x20;       ▼

OCR

&#x20;       │

&#x20;       ▼

Field Extraction

&#x20;       │

&#x20;       ▼

Scholarship Rule Evaluation

&#x20;       │

&#x20;       ▼

Cross-Document Verification

&#x20;       │

&#x20;  ┌────┴────┐

&#x20;  │         │

No Issue  Discrepancy

&#x20;  │         │

&#x20;  ▼         ▼

Ready     Human Review

&#x20;            │

&#x20;            ▼

&#x20;     Confirmation Note

&#x20;            │

&#x20;            ▼

&#x20;       Re-evaluation

&#x20;            │

&#x20;            ▼

&#x20;     Ready for Submission

```



\---



\## Architecture



```text

Frontend

React + Vite

&#x20;   │

&#x20;   │ REST API

&#x20;   ▼

FastAPI Backend

&#x20;   │

&#x20;   ├── Document Detector

&#x20;   ├── OCR Service

&#x20;   ├── Field Extractor

&#x20;   ├── Rule Registry

&#x20;   ├── Verification Service

&#x20;   └── Session / Database Services

```



\### Backend responsibilities



\* API endpoints

\* Session management

\* Document upload handling

\* OCR processing

\* Document classification

\* Field extraction

\* Scholarship rule evaluation

\* Cross-document matching

\* Discrepancy creation and resolution

\* Verification readiness calculation



\### Frontend responsibilities



\* Login/demo entry

\* Verification session creation

\* Document upload

\* Verification dashboard

\* Extracted field display

\* Eligibility results

\* Discrepancy review

\* Human confirmation

\* Final readiness status



\---



\## Technology Stack



\### Frontend



\* React

\* Vite

\* JavaScript

\* HTML

\* CSS

\* Bootstrap-compatible UI



\### Backend



\* Python

\* FastAPI

\* Uvicorn

\* Tesseract OCR

\* SQLite/database services



\### Verification



\* Configurable scholarship rule profiles

\* OCR-based field extraction

\* Cross-document comparison

\* Fuzzy name matching

\* Human-in-the-loop resolution



\### Development



\* Git

\* GitHub

\* Pytest



\---



\## Project Structure



```text

sahayak/

│

├── backend/

│   ├── app/

│   │   ├── api/

│   │   ├── database/

│   │   ├── models/

│   │   └── services/

│   │       ├── document\_detector.py

│   │       ├── field\_extractor.py

│   │       ├── ocr\_service.py

│   │       ├── rule\_registry.py

│   │       └── verification\_service.py

│   │

│   ├── tests/

│   ├── create\_database.py

│   └── requirements.txt

│

├── frontend/

│   ├── src/

│   │   ├── components/

│   │   ├── services/

│   │   ├── App.jsx

│   │   ├── App.css

│   │   └── index.css

│   ├── package.json

│   └── vite.config.js

│

├── docs/

│   └── project-overview.md

│

├── .gitignore

└── README.md

```



\---



\## Running the Project Locally



\### Prerequisites



Install:



\* Python 3.12+

\* Node.js and npm

\* Tesseract OCR

\* Git



\### 1. Clone the repository



```bash

git clone <repository-url>

cd sahayak

```



\### 2. Start the backend



Open a terminal:



```powershell

cd backend

.\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001

```



The backend API will run at:



`http://127.0.0.1:8001`



FastAPI documentation:



`http://127.0.0.1:8001/docs`



\### 3. Start the frontend



Open another terminal:



```powershell

cd frontend

npm.cmd install

npm.cmd run dev

```



Then open:



`http://localhost:5173/`



\---



\## Demo Flow



\### Successful Verification



Use the provided test documents:



```text

fake\_aadhaar.png

test\_marksheet\_12th.jpg

test\_income\_certificate.jpg

```



Expected result:



```text

3/3 Required Documents

6 Fields Extracted

0 Potential Mismatches

0 Required Documents Missing

Ready for Submission

```



\### Human-in-the-Loop Verification



Use:



```text

fake\_aadhaar.png

test\_marksheet\_mismatch.jpg

test\_income\_certificate.jpg

```



The mismatch test intentionally contains:



```text

Aadhaar:

Hana Sharma



12th Marksheet:

Hana Verma

```



Expected behavior:



```text

Student Name Discrepancy

&#x20;       ↓

Action Required

&#x20;       ↓

Human Confirmation

&#x20;       ↓

Discrepancy Resolved

&#x20;       ↓

0 Potential Mismatches

&#x20;       ↓

Ready for Submission

```



This demonstrates the human-in-the-loop verification model.



\---



\## Verification Philosophy



Sahayak is designed as an \*\*assistive pre-submission verification tool\*\*.



It does not:



\* Grant scholarships

\* Make final scholarship decisions

\* Alter official student records

\* Silently override document conflicts



Instead, it helps users identify issues and provides an explainable workflow for resolving them.



Final scholarship decisions remain with the appropriate scholarship authority.



\---



\## Testing



The backend includes integration and verification tests covering:



\* Eligibility evaluation

\* Document upload

\* Verification logic

\* Mismatch detection

\* Discrepancy resolution



Run the backend tests with:



```powershell

cd backend

.\\.venv\\Scripts\\python.exe -m pytest

```



\---



\## Current Verification States



| Status                 | Meaning                                    |

| ---------------------- | ------------------------------------------ |

| `READY\_FOR\_SUBMISSION` | Required checks passed                     |

| `ACTION\_REQUIRED`      | A discrepancy requires human action        |

| `INCOMPLETE`           | Required information/documents are missing |

| `IN\_REVIEW`            | Application requires review                |



\---



\## Why Sahayak?



Traditional document submission systems often tell applicants that something is wrong only after submission.



Sahayak moves verification earlier in the process.



Instead of:



```text

Submit → Rejection → Find the problem

```



Sahayak aims for:



```text

Upload → Understand → Verify → Resolve → Submit

```



The goal is simple:



\*\*Help students catch avoidable document problems before they become scholarship application problems.\*\*



\---



\## Team



\## Team



Built as a hackathon project by our team.



\---



\## Disclaimer



This project is a hackathon prototype intended to demonstrate an AI-assisted document verification workflow.



It should not be treated as an official scholarship eligibility authority or a replacement for government or institutional verification systems.



