import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

PASS = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"
results = []

def check(name, fn):
    try:
        fn()
        print(f"  {PASS} {name}")
        results.append(True)
    except Exception as e:
        print(f"  {FAIL} {name}: {e}")
        results.append(False)

print("\n── Phase 2 Verification ──\n")

def test_document_imports():
    import PyPDF2
    import docx
    import pptx
    from backend.documents import extract_text_from_pdf, extract_text_from_docx, extract_text_from_pptx

check("Document Parser Dependencies (PyPDF2, docx, pptx)", test_document_imports)

def test_frontend_categories():
    with open("frontend/src/pages/DashboardPage.tsx", "r", encoding="utf-8") as f:
        content = f.read()
        assert "LEARNING_OUTCOMES" in content
        assert "LECTURE_NOTES" in content

check("Dashboard UI handles Learning Outcomes & Lecture Notes", test_frontend_categories)

# Summary
print(f"\n── Results: {sum(results)}/{len(results)} passed ──\n")
sys.exit(0 if all(results) else 1)
