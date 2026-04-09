# `/sen-join`

Use the matching `sen-join` skill as the source of truth for this command.

Follow:
- [join skill](../skills/sen-join/SKILL.md)

The bundled asset already exists and should be reused:
- plugin mode: `plugins/sennen/skills/sen-join/assets/join_guest_meet.py`
- standalone mode: `.claude/skills/sen-join/assets/join_guest_meet.py`
- source repo development: `sennen/skills/sen-join/assets/join_guest_meet.py`

Usage:
- `/sen-join https://meet.google.com/abc-defg-hij`

This command should:
- validate the Google Meet URL
- before joining, clearly tell the user that people in the meeting may be able to message the agent through the meeting chat, and require confirmation that they want to proceed at their own risk
- use the bundled asset as the transport client
- send an opening message with a one-shot request when appropriate
- upload a static figure with `--figure <path>` when asked
- when sharing multiple figures, present them as a guided sequence: one figure at a time, a brief explanation for each, then wait before moving on
- stop figure sharing with `--stop-figures` when asked to return to text-only mode
- leave the meeting with `--leave-call` when asked to exit the call
- use `--listen-only --until-incoming-chat` to wait for participant chat
- let Claude generate the next reply after each incoming participant message
- call the asset again with `--input "<reply>"`
- treat `--leave-call` as the real meeting-exit action; a farewell message alone does not make the bot leave
- repeat until the meeting ends or the user stops

Required environment:
- `TWENTYMINDS_API_KEY`, either exported in the environment or stored in `.env`

Typical invocation:
- `/sen-join https://meet.google.com/abc-defg-hij`
- `/sen-join https://meet.google.com/abc-defg-hij --input "Hello everyone, I'm 20minds Bot."`
- `/sen-join https://meet.google.com/abc-defg-hij --figure figures/plot.png`
- `/sen-join https://meet.google.com/abc-defg-hij --stop-figures`
- `/sen-join https://meet.google.com/abc-defg-hij --leave-call`

Loop pattern:
- send:
  - `uv run python <asset-path> <meet-url> --input "<message>"`
- listen:
  - `uv run python <asset-path> <meet-url> --listen-only --until-incoming-chat`

Keep behavior, validation flow, and safety rules aligned with the skill.
