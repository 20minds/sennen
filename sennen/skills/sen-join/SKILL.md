---
name: sen-join
description: Join a Google Meet URL in guest mode and relay chat through a Claude-controlled loop.
---

# Sennen `/sen-join`

Use this skill when the user explicitly wants to join a Google Meet with the 20minds meeting-bot endpoint and have Claude drive the conversation turn by turn.

## Read First

- the Meet URL provided by the user
- whether the repo is uv-managed
- whether the `openai` package is installed in the current environment
- whether `TWENTYMINDS_API_KEY` is set in the environment or in a repo `.env` file
- which exact Python interpreter will execute the asset

## Required Input

- a Google Meet URL such as `https://meet.google.com/abc-defg-hij`

## Risk Warning

Before joining, explicitly tell the user that once the bot is in the meeting:

- anyone in the meeting may be able to send messages to the agent through the meeting chat
- the agent may read those messages and respond to them
- they should only proceed if they are comfortable with that exposure
- participation is at their own risk

Do not join the meeting until the user clearly confirms they want to proceed with that risk.

Preferred wording:

`Joining this meeting will let people in the call send messages directly to the agent through the meeting chat. The agent may read and respond to those messages. Only continue if you're comfortable with that and want to proceed at your own risk.`

## Asset

Use the bundled asset script as the canonical implementation:

- [join_guest_meet.py](assets/join_guest_meet.py)

The asset already exists in this skill directory at `assets/join_guest_meet.py`, relative to this `SKILL.md`.
Before writing any new script or searching outside the skill, check that local path first.
Prefer invoking that asset rather than rewriting the client logic inline.

## Workflow

1. Validate that the provided argument is a Google Meet URL.
2. Give the risk warning in clear, natural language and require explicit confirmation that the user wants to proceed at their own risk.
3. Pick one execution environment and use it consistently for every SDK step in that run.
   - If the repo uses `uv`, the default is `uv run python`.
   - Otherwise use the same `python3` interpreter for import checks and asset execution.
4. Ensure the `openai` package is installed before execution.
   - If the repo uses `uv`, install it with `uv add openai` if missing, then check with `uv run python -c "import openai"`.
   - Otherwise check with `python3 -c "import openai"`.
5. Ensure `TWENTYMINDS_API_KEY` is available either:
   - in the environment that will run the asset, or
   - in a `.env` file in the repo working directory.
6. Reuse the bundled asset script rather than generating a new client.
7. Run the asset with the Meet URL and optional `--input` text.
8. Use a Claude-controlled loop rather than a self-reasoning Python worker:
   - first call the asset with the Meet URL and the opening message
   - then call the asset with `--listen-only --until-incoming-chat` to wait for the next participant message
   - when a participant message arrives, Claude should read it, generate the reply itself, and invoke the asset again with `--input "<reply>"`
   - after sending that reply, invoke the asset again with `--listen-only --until-incoming-chat`
   - repeat until the meeting ends or the user stops
   - if presenting multiple figures, handle them as a paced walkthrough:
     - share one figure at a time
     - give a concise explanation of what the current figure shows and why it matters
     - then pause and wait for the user's cue, question, or acknowledgement before moving to the next figure
     - do not rapidly push several figures in a row without checking whether the user wants to continue
9. The expected behavior of the asset is:
   - validate the Meet URL
   - send `input` text with a one-shot non-streaming request when not in `--listen-only` mode
   - upload `--figure` image files to the meeting-bot figure endpoint when provided
   - support common static figure formats such as `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, and `.webp`
   - stop figure sharing with `--stop-figures` when the meeting asks to return to text-only mode
   - leave the meeting with `--leave-call` when the user asks to exit the call
   - print a concise send confirmation like `[sent:sent] ...` or `[sent:queued] ...`
   - print a concise figure confirmation like `[figure:sent] chart.png`
   - print `[figure:stopped] stop` when figure sharing is turned off
   - print `[leave:left] <meet-url>` when the leave-call request is accepted
   - use streaming only in `--listen-only` mode
   - return successfully after incoming participant chat when `--until-incoming-chat` is set
   - do not auto-delete listener responses for cleanup, because response deletion is used to leave the meeting

## Preferred Command Sequence

1. validate the Meet URL
2. if the repo uses `uv`, use `uv run python` for every step below; do not switch to plain `python3`
3. if the repo uses `uv` and `openai` is missing, install it with `uv add openai`
4. if the repo uses `uv`, check `openai` with `uv run python -c "import openai"`
5. verify `TWENTYMINDS_API_KEY` is present either in the environment or in `.env`
6. if the repo uses `uv`, run the asset with:
   - initial join/send:
     - `uv run python assets/join_guest_meet.py <google-meet-url> --input "<message>"`
   - share a figure:
     - `uv run python assets/join_guest_meet.py <google-meet-url> --figure path/to/chart.png`
   - stop sharing figures:
     - `uv run python assets/join_guest_meet.py <google-meet-url> --stop-figures`
   - leave the meeting:
     - `uv run python assets/join_guest_meet.py <google-meet-url> --leave-call`
   - wait for the next participant message:
     - `uv run python assets/join_guest_meet.py <google-meet-url> --listen-only --until-incoming-chat`
   - send Claude's reply:
     - `uv run python assets/join_guest_meet.py <google-meet-url> --input "<claude reply>"`
7. if the repo does not use `uv`, use the equivalent `python3` commands instead, but still keep to one interpreter consistently

## Operating Notes

- In uv-managed repos, do not use bare `python3` for SDK import checks or asset execution.
- In uv-managed repos, prefer `uv add openai` over trying to run the asset first and failing on `ModuleNotFoundError`.
- A successful `uv add openai` does not make `python3 -c "import openai"` valid unless that same system interpreter also has `openai` installed.
- Prefer concise meeting-bot inputs rather than shell-oriented text.
- If the environment variable is missing, also check `.env` in the repo root before failing.
- Do not require the user to manually `source .env` if the key is already present there.
- The asset should stream response events live rather than waiting only for a final buffered response.
- The asset is transport only. Claude is responsible for generating replies.
- In `--listen-only --until-incoming-chat` mode, a participant message arriving is a success condition.
- When walking through multiple figures, present them one at a time, explain each briefly in natural language, and wait before advancing to the next figure.

## Example Launch

If the repo uses `uv`, a typical launch looks like:

```bash
uv run python assets/join_guest_meet.py "https://meet.google.com/abc-defg-hij" \
  --input "Hello everyone, I'm 20minds Bot."

uv run python assets/join_guest_meet.py "https://meet.google.com/abc-defg-hij" \
  --figure figures/plot.png

uv run python assets/join_guest_meet.py "https://meet.google.com/abc-defg-hij" \
  --stop-figures

uv run python assets/join_guest_meet.py "https://meet.google.com/abc-defg-hij" \
  --leave-call

uv run python assets/join_guest_meet.py "https://meet.google.com/abc-defg-hij" \
  --listen-only --until-incoming-chat
```

## Validation Output

When validating a real run, the useful expected stdout is:

- streaming text from the meeting-bot endpoint as deltas arrive
- participant chat lines like `Dirk Neumann: hello bot` when listening

An empty stdout stream is not enough to claim the bot joined, sent a message, or heard a participant.

If required configuration is missing, expect a clear failure such as:

- `Missing API key. Set TWENTYMINDS_API_KEY in the environment or in a .env file before running this command.`

## Rules

- Use the bundled asset as the transport client for this command.
- Do not reintroduce local browser automation in this asset.
- Do not add transcript processing, uploads, or meeting summaries in this command.
- Before joining, clearly explain that people in the call may be able to message the agent through the meeting chat, and require explicit confirmation from the user that they want to proceed at their own risk.
- Fail clearly if the input is not a Google Meet URL.
- Fail clearly if `openai` is missing or `TWENTYMINDS_API_KEY` is unavailable from both the environment and `.env`.
- When the repo uses `uv`, install missing SDK dependencies with `uv add openai`.
- When the repo uses `uv`, do not mix `uv` installs with plain `python3` execution checks.
- Stream the response output live.
- For meeting-bot, deleting a response is treated as a leave-call action rather than harmless cleanup.
- Claude, not the asset, should decide what to say next.
- When sharing multiple figures, Claude should treat it like a guided walkthrough rather than a batch dump: one figure, one short explanation, then wait.
- Only run this command when the user explicitly asked to join a meeting.
