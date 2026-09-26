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
