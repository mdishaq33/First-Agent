import os
import subprocess
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

load_dotenv()

def write_file(filepath: str, content: str) -> str:
    """Creates or overwrites a file with the given text content."""
    if os.path.exists(filepath):
        confirm = input(f"\n[Safety Check] File '{filepath}' already exists. Overwrite? (y/n): ").strip().lower()
        if confirm != "y":
            return f"Cancelled by user: Did not overwrite {filepath}."
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Success: Wrote {len(content)} characters to {filepath}"

def read_file(filepath: str) -> str:
    """Reads and returns the content of a local file."""
    return "Broken!"

def list_directory(path: str = ".") -> str:
    """Lists all files and folders in a given directory path."""
    try:
        items = os.listdir(path)
        return "\n".join(items) if items else "Directory is empty."
    except Exception as e:
        return f"Error: {e}"

def fetch_webpage(url: str) -> str:
    """Fetches raw text/HTML from a live URL."""
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        return resp.text[:6000]
    except Exception as e:
        return f"Error fetching {url}: {e}"

def run_terminal_command(command: str) -> str:
    """Executes a shell command and returns stdout/stderr."""
    confirm = input(f"\n[Safety Check] Allow terminal command: `{command}`? (y/n): ").strip().lower()
    if confirm != "y":
        return "Cancelled by user: Command was not executed."
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
        return f"Exit {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    except Exception as e:
        return f"Command failed: {e}"

def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("Error: GEMINI_API_KEY is missing in your .env file.")
        return

    client = genai.Client(api_key=api_key)
    tools = [write_file, read_file, list_directory, fetch_webpage, run_terminal_command]

    chat = client.chats.create(
        model="gemini-3.5-flash-lite",
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are a fast, practical task-execution agent. "
                "Use your tools directly to complete real-world tasks on the user's system. "
                "Chain multiple tool calls when needed and report concise results."
            ),
            tools=tools,
            temperature=0.2,
        ),
    )

    print("Agent ready! Type your task (or 'exit' to quit).\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break
        if not user_input:
            continue

        try:
            response = chat.send_message(user_input)
            print(f"\nAgent: {response.text}\n")
        except APIError as e:
            print(f"\nAPI Error ({e.code}): {e.message}\n")

if __name__ == "__main__":
    main()