import requests

BASE_URL = "http://127.0.0.1:8000"


def test_aadhaar_upload_pipeline():
    print("--- Creating a test session ---")

    session_payload = {
        "student_name": "Hana Sharma",
        "scholarship_id": "merit-cum-means"
    }

    response = requests.post(
        f"{BASE_URL}/api/sessions/create",
        json=session_payload
    )

    assert response.status_code == 201, (
        f"Expected 201, got {response.status_code}: {response.text}"
    )

    session = response.json()
    session_id = session["session_id"]

    print(f"Session created: {session_id}")

    print("\n--- Uploading fake Aadhaar ---")

    file_path = r"..\fake_aadhaar.png"

    with open(file_path, "rb") as image_file:
        upload_response = requests.post(
            f"{BASE_URL}/api/sessions/{session_id}/documents/upload",
            files={
                "file": (
                    "fake_aadhaar.png",
                    image_file,
                    "image/png"
                )
            }
        )

    assert upload_response.status_code == 200, (
        f"Expected 200, got {upload_response.status_code}: "
        f"{upload_response.text}"
    )

    upload_data = upload_response.json()

    print(f"Upload status: {upload_response.status_code}")
    print(f"Detected type: {upload_data['detected_type']}")
    print(f"Extracted OCR text:\n{upload_data['extracted_text']}")

    assert upload_data["detected_type"] == "aadhaar"

    print("\n--- Checking updated session ---")

    session_response = requests.get(
        f"{BASE_URL}/api/sessions/{session_id}"
    )

    assert session_response.status_code == 200

    updated_session = session_response.json()

    assert len(updated_session["documents"]) == 1

    assert updated_session["documents"][0]["detected_type"] == "aadhaar"

    extracted_fields = updated_session["extracted_fields"]

    field_names = [field["field_name"] for field in extracted_fields]

    assert "name" in field_names
    assert "date_of_birth" in field_names

    print(f"Documents checked: {updated_session['readiness']['documents_checked']}")
    print(f"Fields extracted: {updated_session['readiness']['fields_extracted']}")
    print(f"Readiness status: {updated_session['readiness']['overall_status']}")

    print("\n================ UPLOAD INTEGRATION TEST PASSED ================")


if __name__ == "__main__":
    test_aadhaar_upload_pipeline()


def test_complete_scholarship_document_pipeline():
    print("\n--- Creating complete scholarship test session ---")

    session_payload = {
        "student_name": "Hana Sharma",
        "scholarship_id": "merit-cum-means"
    }

    response = requests.post(
        f"{BASE_URL}/api/sessions/create",
        json=session_payload
    )

    assert response.status_code == 201, (
        f"Expected 201, got {response.status_code}: {response.text}"
    )

    session_id = response.json()["session_id"]

    documents = [
        ("fake_aadhaar.png", "aadhaar"),
        ("fake_marksheet.png", "marksheet_12th"),
        ("fake_income_certificate.png", "income_certificate"),
    ]

    for file_name, expected_type in documents:
        print(f"\n--- Uploading {file_name} ---")

        file_path = f"..\\{file_name}"

        with open(file_path, "rb") as image_file:
            upload_response = requests.post(
                f"{BASE_URL}/api/sessions/{session_id}/documents/upload",
                files={
                    "file": (
                        file_name,
                        image_file,
                        "image/png"
                    )
                }
            )

        assert upload_response.status_code == 200, (
            f"Upload failed for {file_name}: "
            f"{upload_response.status_code}: {upload_response.text}"
        )

        upload_data = upload_response.json()

        print(f"Detected type: {upload_data['detected_type']}")
        print(f"OCR text:\n{upload_data['extracted_text']}")

        assert upload_data["detected_type"] == expected_type

    print("\n--- Checking complete session ---")

    session_response = requests.get(
        f"{BASE_URL}/api/sessions/{session_id}"
    )

    assert session_response.status_code == 200

    updated_session = session_response.json()

    assert len(updated_session["documents"]) == 3

    detected_types = [
        document["detected_type"]
        for document in updated_session["documents"]
    ]

    assert "aadhaar" in detected_types
    assert "marksheet_12th" in detected_types
    assert "income_certificate" in detected_types

    extracted_fields = updated_session["extracted_fields"]

    field_names = [
        field["field_name"]
        for field in extracted_fields
    ]

    assert "name" in field_names
    assert "date_of_birth" in field_names
    assert "percentage" in field_names
    assert "income" in field_names

    assert updated_session["readiness"]["required_documents_missing"] == []

    print(
        f"Documents checked: "
        f"{updated_session['readiness']['documents_checked']}"
    )

    print(
        f"Fields extracted: "
        f"{updated_session['readiness']['fields_extracted']}"
    )

    print(
        f"Required documents missing: "
        f"{updated_session['readiness']['required_documents_missing']}"
    )

    print(
        f"Readiness status: "
        f"{updated_session['readiness']['overall_status']}"
    )

    print(
        "\n=========== COMPLETE SCHOLARSHIP PIPELINE PASSED ==========="
    )
