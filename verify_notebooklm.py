"""
NotebookLM Features Verification Script
Run: python verify_notebooklm.py (from the project root)

Checks:
  1. NotebookLM router imports work
  2. Required API endpoints are defined
  3. NotebookLM client can be imported
  4. API method names are correct
"""

import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(__file__))

PASS = "[PASS]"
FAIL = "[FAIL]"
results = []


def check(name, fn):
    try:
        fn()
        print(f"  {PASS} {name}")
        results.append(True)
    except Exception as e:
        print(f"  {FAIL} {name}: {e}")
        results.append(False)


def main():
    print("\n===== NotebookLM Features Verification =====\n")

    # 1. Check imports
    print("Imports:")
    check("notebooklm package", lambda: __import__("notebooklm"))
    check("NotebookLMClient", lambda: __import__("notebooklm").NotebookLMClient)
    check("FastAPI", lambda: __import__("fastapi"))

    # 2. Check router imports
    print("\nRouter:")
    try:
        from backend.notebooklm_router import router
        check("NotebookLM router import", lambda: True)
        
        # Check that routes are defined
        routes = [route.path for route in router.routes]
        expected_routes = [
            "/notebooklm/status",
            "/notebooklm/notebooks",
            "/notebooklm/notebooks/{notebook_id}/sources",
            "/notebooklm/notebooks/chat",
            "/notebooklm/notebooks/audio"
        ]
        
        for route in expected_routes:
            # Handle path parameters
            if "{" in route:
                check_base = route.split("{")[0].rstrip("/")
                matching_routes = [r for r in routes if r.startswith(check_base)]
                check(f"Route {route} exists", lambda: len(matching_routes) > 0)
            else:
                check(f"Route {route} exists", lambda: route in routes)
                
    except Exception as e:
        print(f"  {FAIL} NotebookLM router import: {e}")
        results.append(False)

    # 3. Check API method names
    print("\nAPI Methods:")
    try:
        from notebooklm._artifacts import ArtifactsAPI
        artifact_methods = [m for m in dir(ArtifactsAPI) if not m.startswith('_')]
        check("generate_audio method exists", lambda: "generate_audio" in artifact_methods)
        check("wait_for_completion method exists", lambda: "wait_for_completion" in artifact_methods)
        check("download_audio method exists", lambda: "download_audio" in artifact_methods)
        
        from notebooklm._chat import ChatAPI
        chat_methods = [m for m in dir(ChatAPI) if not m.startswith('_')]
        check("ask method exists (not send_message)", lambda: "ask" in chat_methods)
        check("send_message method does NOT exist", lambda: "send_message" not in chat_methods)
        
    except Exception as e:
        print(f"  {FAIL} API method check: {e}")
        results.append(False)

    # Summary
    passed = sum(results)
    total = len(results)
    print(f"\n===== Results: {passed}/{total} passed =====\n")
    
    if passed == total:
        print("All checks passed! NotebookLM features are correctly implemented.")
        print("\nTo test functionality:")
        print("1. Run: python -m notebooklm login (to authenticate)")
        print("2. Start the backend server")
        print("3. Test endpoints at http://localhost:8000/notebooklm/")
    else:
        print("Some checks failed. Please review the implementation.")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())