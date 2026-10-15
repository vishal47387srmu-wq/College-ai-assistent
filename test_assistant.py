import unittest
from unittest.mock import patch

from assistant import CollegeAssistant


class CollegeAssistantTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assistant = CollegeAssistant()

    def test_attendance_command(self) -> None:
        self.assertIn("80.0%", self.assistant.reply("attendance 40 32"))
        self.assertIn("Safe", self.assistant.reply("attendance 40 32"))

    def test_zero_attendance_is_reported(self) -> None:
        self.assertIn("cannot be zero", self.assistant.reply("attendance 0 0"))

    def test_schedule_command(self) -> None:
        self.assertIn("Monday", self.assistant.reply("schedule Monday"))

    def test_unknown_question_has_offline_fallback(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            self.assertIn("GEMINI_API_KEY", self.assistant.reply("How do I apply for a scholarship?"))


if __name__ == "__main__":
    unittest.main()
