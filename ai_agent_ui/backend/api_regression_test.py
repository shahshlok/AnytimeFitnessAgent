# api_regression_tests.py
# A script to run automated tests against our FastAPI backend.

import requests
import json

# The base URL of our running FastAPI application
BASE_URL = "http://127.0.0.1:8000"

def test_health_check():
    """Tests if the root endpoint is running."""
    print("--- Running Test: Health Check ---")
    try:
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
        print("[PASS] Health check successful.")
        return True
    except Exception as e:
        print(f"[FAIL] Health check failed: {e}")
        return False

def test_speak_endpoint():
    """Tests the /speak TTS endpoint."""
    print("--- Running Test: /speak Endpoint ---")
    try:
        url = f"{BASE_URL}/speak"
        payload = {"text": "This is a regression test."}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        
        # 1. Check for a successful status code
        assert response.status_code == 200
        
        # 2. Check if the response content type is audio
        assert response.headers['content-type'] == 'audio/mpeg'
        
        # 3. Check if we actually received some audio data (more than 0 bytes)
        assert len(response.content) > 0
        
        print("[PASS] /speak endpoint returned audio successfully.")
        
        # Optional: Save the audio file to manually verify it
        with open("test_output.mp3", "wb") as f:
            f.write(response.content)
        print(" -> Saved sample audio to test_output.mp3")
        
        return True
    except Exception as e:
        print(f"[FAIL] /speak endpoint test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting API Regression Test Suite...")
    print(f"Targeting API at: {BASE_URL}")
    
    # List of tests to run
    tests = [
        test_health_check,
        test_speak_endpoint,
    ]
    
    results = [test() for test in tests]
    
    print("\n--- Test Report ---")
    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    if passed != total:
        print(f"❌ Failed: {total - passed}/{total}")
    print("-------------------")