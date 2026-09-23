import requests

BASE_URL = "http://127.0.0.1:8000"


def test_endpoints():
    print("--- 1. Testing /health ---")
    r_health = requests.get(f"{BASE_URL}/health")
    assert r_health.status_code == 200, f"Expected 200, got {r_health.status_code}"
    print(f"Status: {r_health.status_code}")
    print(f"Response: {r_health.json()}")

    print("\n--- 2. Testing /docs ---")
    r_docs = requests.get(f"{BASE_URL}/docs")
    assert r_docs.status_code == 200, f"Expected 200, got {r_docs.status_code}"
    print(f"Status: {r_docs.status_code} (HTML length: {len(r_docs.text)} bytes)")

    print("\n--- 3. Testing GET /api/scholarships ---")
    r_schol = requests.get(f"{BASE_URL}/api/scholarships")
    assert r_schol.status_code == 200, f"Expected 200, got {r_schol.status_code}"
    schemes = r_schol.json()
    print(f"Status: {r_schol.status_code}")
    print(f"Available schemes count: {len(schemes)}")
    for s in schemes:
        print(f"  * {s['name']} (ID: {s['scholarship_id']})")
        print(f"    Required Docs: {s['required_documents']}")
        print(f"    Income Ceiling: {s['income_ceiling']}")
        print(f"    Min Marks: {s['min_academic_percentage']}%")
        print(f"    Matching Thresholds: {s['matching_thresholds']}")

    print("\n--- 4. Testing POST /api/sessions/create (Preset Scheme) ---")
    payload = {
        "student_name": "Hana Sharma",
        "scholarship_id": "merit-cum-means"
    }
    r_create = requests.post(f"{BASE_URL}/api/sessions/create", json=payload)
    assert r_create.status_code == 201, f"Expected 201, got {r_create.status_code}"
    sess = r_create.json()
    session_id = sess["session_id"]
    print(f"Status: {r_create.status_code}")
    print(f"Session ID created: {session_id}")
    print(f"Student: {sess['student_name']}")
    print(f"Applied Rule: {sess['rule_config']['name']}")
    print(f"Readiness Scorecard: {sess['readiness']}")

    print(f"\n--- 5. Testing GET /api/sessions/{session_id} ---")
    r_get = requests.get(f"{BASE_URL}/api/sessions/{session_id}")
    assert r_get.status_code == 200, f"Expected 200, got {r_get.status_code}"
    fetched_sess = r_get.json()
    assert fetched_sess["session_id"] == session_id
    print(f"Status: {r_get.status_code}")
    print(f"Successfully retrieved session: {fetched_sess['session_id']}")

    print("\n--- 6. Testing POST /api/sessions/create (Custom Dynamic Rules) ---")
    custom_payload = {
        "student_name": "Aarav Patel",
        "custom_rules": {
            "scholarship_id": "custom-trust-fund",
            "name": "Patel Foundation Scholarship",
            "description": "Custom trust scholarship with specific requirements",
            "required_documents": ["aadhaar", "marksheet_12th", "domicile_certificate"],
            "income_ceiling": 500000.0,
            "min_academic_percentage": 70.0,
            "matching_thresholds": {
                "auto_approve_threshold": 0.95,
                "human_review_threshold": 0.85
            }
        }
    }
    r_custom = requests.post(f"{BASE_URL}/api/sessions/create", json=custom_payload)
    assert r_custom.status_code == 201, f"Expected 201, got {r_custom.status_code}"
    custom_sess = r_custom.json()
    print(f"Status: {r_custom.status_code}")
    print(f"Custom Session ID: {custom_sess['session_id']}")
    print(f"Custom Scheme Name: {custom_sess['rule_config']['name']}")
    print(f"Custom Missing Docs Initialized: {custom_sess['readiness']['required_documents_missing']}")

    print("\n--- 7. Testing 404 Error Handling ---")
    r_bad_session = requests.get(f"{BASE_URL}/api/sessions/non_existent_id")
    assert r_bad_session.status_code == 404
    print(f"Non-existent session returned 404 as expected: {r_bad_session.json()}")

    print("\n================ ALL TESTS PASSED SUCCESSFULLY! ================")


if __name__ == "__main__":
    test_endpoints()
