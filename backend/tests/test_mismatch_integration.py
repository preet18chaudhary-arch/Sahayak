import requests

BASE_URL = "http://127.0.0.1:8000"


def test_dob_mismatch_detection():
    print("\n--- Creating mismatch test session ---")

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

    print("\n--- Uploading correct Aadhaar ---")

    with open(r"..\fake_aadhaar.png", "rb") as image_file:
        response = requests.post(
            f"{BASE_URL}/api/sessions/{session_id}/documents/upload",
            files={
                "file": (
                    "fake_aadhaar.png",
                    image_file,
                    "image/png"
                )
            }
        )

    assert response.status_code == 200

    print(f"Detected type: {response.json()['detected_type']}")

    print("\n--- Uploading mismatched Aadhaar ---")

    with open(r"..\fake_aadhaar_mismatch.png", "rb") as image_file:
        response = requests.post(
            f"{BASE_URL}/api/sessions/{session_id}/documents/upload",
            files={
                "file": (
                    "fake_aadhaar_mismatch.png",
                    image_file,
                    "image/png"
                )
            }
        )

    assert response.status_code == 200

    print(f"Detected type: {response.json()['detected_type']}")

    print("\n--- Checking session for DOB discrepancy ---")

    session_response = requests.get(
        f"{BASE_URL}/api/sessions/{session_id}"
    )

    assert session_response.status_code == 200

    session = session_response.json()

    discrepancies = session["discrepancies"]

    print(f"Discrepancies found: {len(discrepancies)}")

    for discrepancy in discrepancies:
        print(
            f"{discrepancy['field_name']}: "
            f"{discrepancy['value_a']} vs "
            f"{discrepancy['value_b']}"
        )

    assert any(
        discrepancy["field_name"] == "date_of_birth"
        for discrepancy in discrepancies
    )

    print("\n=========== DOB MISMATCH TEST PASSED ===========")
