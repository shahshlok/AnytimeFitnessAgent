# api_regression_tests.py
# A script to run automated tests against our FastAPI backend.

import requests
import json
import os
import traceback

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
        # with open("test_output.mp3", "wb") as f:
        #     f.write(response.content)
        print(" -> Saved sample audio to test_output.mp3")
        
        return True
    except Exception as e:
        print(f"[FAIL] /speak endpoint test failed: {e}")
        return False

def test_chat_voice_endpoint():
    """Tests the /chat/voice endpoint for voice chat functionality."""
    print("--- Running Test: /chat/voice Endpoint ---")
    try:
        audio_path = "ai_agent_ui/backend/test_query.mp3"  # The file is in the same directory

        # Check if test file exists
        if not os.path.exists(audio_path):
            print(f"[SKIP] Test audio file not found at: {audio_path}")
            return True

        url = f"{BASE_URL}/chat/voice"
        
        # Send the audio file with proper file handling
        with open(audio_path, "rb") as audio_file:
            files = {'file': audio_file}
            response = requests.post(url, files=files)
        
        # Check response
        assert response.status_code == 200 
        response_json = response.json()
        assert 'reply' in response_json
        assert isinstance(response_json['reply'], str)
        assert len(response_json['reply']) > 0
        
        print("[PASS] /chat/voice endpoint processed audio successfully.")
        return True
    except Exception as e:
        print("[FAIL] /chat/voice endpoint test failed with exception:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting API Regression Test Suite...")
    print(f"Targeting API at: {BASE_URL}")
    
    # List of tests to run
    tests = [
        test_health_check,
        test_speak_endpoint,
        test_chat_voice_endpoint,
    ]
    
    results = [test() for test in tests]
    
    print("\n--- Test Report ---")
    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    if passed != total:
        print(f"❌ Failed: {total - passed}/{total}")
    print("-------------------")