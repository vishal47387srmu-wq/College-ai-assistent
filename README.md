# College AI Assistant

A small Python assistant for college students. It supports local attendance and timetable commands, with optional Gemini answers for general questions.

## Run

Use Python 3.10+:

```powershell
python assistant.py
```

The existing `.env` file is read automatically. Set `GEMINI_API_KEY` there to enable general AI questions. Keep that file private and never commit it.

## Commands

- `attendance 40 32`
- `mark attendance 2026-10-15 Maths present`
- `schedule Monday`
- `help`
- `quit`

## Test

```powershell
python -m unittest -v
```
