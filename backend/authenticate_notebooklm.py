import asyncio
from notebooklm import NotebookLMClient

async def authenticate():
    print("Starting authentication flow for NotebookLM...")
    print("A browser window should appear. Please log in to your Google Account.")
    try:
        # Initializing from_storage will trigger the browser login if no session is saved.
        async with await NotebookLMClient.from_storage() as client:
            print("Successfully authenticated and obtained session!")
    except Exception as e:
        print(f"Error during authentication: {e}")

if __name__ == "__main__":
    asyncio.run(authenticate())
