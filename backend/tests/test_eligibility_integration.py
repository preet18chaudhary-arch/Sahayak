import requests

BASE_URL = "http://127.0.0.1:8000"


def test_high_income_rejected():
    print("\n--- Creating eligibility test session ---")

    response = requests.post(
        f"{BASE_URL}/api/sessions/create",
        json={
            "student_name": "Hana Sharma",
            "scholarship_id": "merit-cum-means"
        }
    )

    assert response.status_code == 201

    session_id = response.json()["session_id"]

    print(f"Session created: {session_id}")

    documents = [
        ("fake_aadhaar.png", "image/png"),
        ("fake_marksheet.png", "image/png"),
        ("test_income_high.jpg", "image/jpeg"),
    ]

    for file_name, content_type in documents:
        print(f"\n--- Uploading {file_name} ---")

        file_path = (
            f"..\\{file_name}"
            if file_name != "test_income_high.jpg"
            else file_name
        )

        with open(file_path, "rb") as image_file:
            upload_response = requests.post(
                f"{BASE_URL}/api/sessions/{session_id}/documents/upload",
                files={
                    "file": (
                        file_name,
                        image_file,
                        content_type
                    )
                }
            )

        assert upload_response.status_code == 200, (
            f"Upload failed for {file_name}: "
            f"{upload_response.status_code}: "
            f"{upload_response.text}"
        )

        upload_data = upload_response.json()

        print(f"Detected type: {upload_data['detected_type']}")
        print(f"OCR text:\n{upload_data['extracted_text']}")

    print("\n--- Checking eligibility result ---")

    session = requests.get(
        f"{BASE_URL}/api/sessions/{session_id}"
    ).json()

    readiness = session["readiness"]

    print(f"Documents checked: {readiness['documents_checked']}")
    print(
        f"Required documents missing: "
        f"{readiness['required_documents_missing']}"
    )
    print(f"Readiness status: {readiness['overall_status']}")
    print(f"Status message: {readiness['status_message']}")

    assert readiness["required_documents_missing"] == []

    assert readiness["overall_status"] == "ACTION_REQUIRED"

    assert "Income exceeds" in readiness["status_message"]

    print("\n=========== HIGH INCOME TEST PASSED ===========")
