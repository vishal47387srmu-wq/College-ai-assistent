"""College AI Assistant.

Run with ``python assistant.py`` for an interactive assistant.  The assistant
handles common college tasks locally and can use Gemini for general questions
when ``GEMINI_API_KEY`` is configured in ``.env`` or the environment.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from tools import analyze_timetable, calculate_attendance_percentage, mark_attendance


def load_dotenv(path: Path = Path(".env")) -> None:
    """Load simple KEY=VALUE entries without requiring python-dotenv."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"\''))


@dataclass
class CollegeAssistant:
    """Conversation coordinator for local college tools and Gemini."""

    timetable: str = ""
    history: list[tuple[str, str]] = field(default_factory=list)
    _model: object | None = field(default=None, init=False, repr=False)

    def reply(self, message: str) -> str:
        """Return a helpful response for a user message."""
        clean = message.strip()
        if not clean:
            return "Please enter a question."

        local_response = self._local_command(clean)
        if local_response is None:
            local_response = self._ask_gemini(clean)
        self.history.append((clean, local_response))
        return local_response

    def _local_command(self, message: str) -> str | None:
        lowered = message.lower()
        if lowered in {"help", "/help"}:
            return (
                "I can help with attendance, timetable lookups, and general college questions.\n"
                "Examples: 'attendance 40 32', 'mark attendance 2026-10-15 Maths present', "
                "'schedule Monday'."
            )
        if lowered in {"quit", "exit", "/quit"}:
            return "Goodbye!"

        attendance = re.search(r"attendance\s+(\d+)\s+(\d+)", lowered)
        if attendance:
            total, attended = map(int, attendance.groups())
            result = calculate_attendance_percentage(total, attended)
            if "error" in result:
                return result["error"]
            return (
                f"Attendance: {result['attendance_percentage']}% ({result['status']}). "
                "The target is 75%."
            )

        marked = re.search(
            r"mark attendance\s+(\S+)\s+(.+?)\s+(present|absent)$", lowered
        )
        if marked:
            date, subject, status = marked.groups()
            result = mark_attendance(date, subject.title(), status)
            return result["message"]

        if lowered.startswith(("schedule ", "timetable ")):
            day = message.split(maxsplit=1)[1]
            result = analyze_timetable(day, self.timetable)
            return f"{result['day']}: {result['schedule']}"
        return None

    def _ask_gemini(self, message: str) -> str:
        """Ask Gemini when available, with a useful offline fallback."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return (
                "I can answer attendance and timetable commands locally. Add a "
                "GEMINI_API_KEY to .env to enable general AI questions."
            )
        try:
            if self._model is None:
                from google import genai

                self._model = genai.Client(api_key=api_key)
            prompt = (
                "You are a concise, friendly college assistant. Give practical, "
                "accurate answers and say when information may vary by college.\n\n"
                f"Student question: {message}"
            )
            response = self._model.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )
            return response.text or "I could not generate a response. Please try again."
        except Exception:
            return "The AI service is unavailable right now. Local college tools are still working."


def main() -> None:
    load_dotenv()
    assistant = CollegeAssistant()
    print("College AI Assistant — type 'help' for examples, or 'quit' to exit.")
    while True:
        try:
            message = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if message.strip().lower() in {"quit", "exit", "/quit"}:
            print("Assistant: Goodbye!")
            break
        print(f"Assistant: {assistant.reply(message)}")


if __name__ == "__main__":
    main()
