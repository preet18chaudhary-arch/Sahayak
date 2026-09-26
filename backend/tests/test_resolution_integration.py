import requests

BASE_URL = "http://127.0.0.1:8000"


def test_resolve_dob_discrepancy():
    print("\n--- Creating resolution test session ---")

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

    print("\n--- Checking discrepancy ---")

    session = requests.get(
        f"{BASE_URL}/api/sessions/{session_id}"
    ).json()

    discrepancies = session["discrepancies"]

    assert len(discrepancies) == 1

    discrepancy = discrepancies[0]

    assert discrepancy["field_name"] == "date_of_birth"
    assert discrepancy["resolved"] is False

    discrepancy_id = discrepancy["id"]

    print(f"Discrepancy ID: {discrepancy_id}")
    print(f"Resolved before action: {discrepancy['resolved']}")

    print("\n--- Resolving discrepancy ---")

    resolve_response = requests.post(
        f"{BASE_URL}/api/sessions/{session_id}/discrepancies/{discrepancy_id}/resolve",
        json={
            "resolution_note": "Human review confirmed the correct date of birth."
        }
    )

    assert resolve_response.status_code == 200

    resolution_data = resolve_response.json()

    print(f"Resolution response: {resolution_data}")

    assert resolution_data["resolved"] is True
    assert (
        resolution_data["resolution_note"]
        == "Human review confirmed the correct date of birth."
    )

    print("\n--- Checking updated session ---")

    updated_session = requests.get(
        f"{BASE_URL}/api/sessions/{session_id}"
    ).json()

    updated_discrepancy = updated_session["discrepancies"][0]

    assert updated_discrepancy["resolved"] is True
    assert (
        updated_discrepancy["resolution_note"]
        == "Human review confirmed the correct date of birth."
    )

    print(f"Resolved after action: {updated_discrepancy['resolved']}")
    print(
        f"Readiness status: "
        f"{updated_session['readiness']['overall_status']}"
    )

    print("\n=========== DISCREPANCY RESOLUTION TEST PASSED ===========")
