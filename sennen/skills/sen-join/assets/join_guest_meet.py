#!/usr/bin/env python3
"""Send a meeting-bot request through the 20minds meeting-bot SSE API."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import urlparse

_DEFAULT_GREETING = "Hello everyone, I'm 20minds Bot."
_INPUT_NOT_SET = object()  # sentinel: --input was not provided by the user

import requests


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send a prompt to the 20minds meeting-bot endpoint for a Google Meet URL."
    )
    parser.add_argument("meet_url", help="Google Meet URL to target.")
    parser.add_argument(
        "--input",
        default=_INPUT_NOT_SET,
        help="Prompt or message to send to the meeting bot.",
    )
    parser.add_argument(
        "--api-key-env",
        default="TWENTYMINDS_API_KEY",
        help="Environment variable name that stores the API key.",
    )
    parser.add_argument(
        "--wait-seconds",
        type=int,
        default=45,
        help="Maximum number of seconds to wait for meeting-bot events before failing.",
    )
    parser.add_argument(
        "--until-incoming-chat",
        action="store_true",
        help="Exit successfully after the first participant chat message is received.",
    )
    parser.add_argument(
        "--listen-only",
        action="store_true",
        help="Do not send an initial message; only attach to the meeting stream and wait for incoming chat.",
    )
    parser.add_argument(
        "--figure",
        help="Optional path to a static image figure to upload to the meeting bot.",
    )
    parser.add_argument(
        "--stop-figures",
        action="store_true",
        help="Stop figure/video output and return the bot to text-only mode.",
    )
    parser.add_argument(
        "--leave-call",
        action="store_true",
        help="Tell the meeting bot to leave the call.",
    )
    return parser.parse_args()


def validate_meet_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != "meet.google.com":
        raise ValueError(f"Expected a Google Meet URL, got: {url}")
    if not parsed.path.strip("/"):
        raise ValueError(f"Expected a Google Meet URL, got: {url}")
    return url


def load_api_key(env_name: str) -> str | None:
    api_key = os.environ.get(env_name)
    if api_key:
        return api_key

    env_path = Path.cwd() / ".env"
    if not env_path.exists():
        return None

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key != env_name:
            continue
        value = value.strip().strip('"').strip("'")
        if value:
            os.environ.setdefault(env_name, value)
            return value
    return None


def _parse_sse_data(lines: list[str]) -> dict | list | str | None:
    raw = "\n".join(lines).strip()
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return raw


def _response_id_from_payload(payload: object) -> str | None:
    if not isinstance(payload, dict):
        return None
    response = payload.get("response")
    if isinstance(response, dict):
        value = response.get("id") or response.get("response_id")
        if value:
            return str(value)
    value = payload.get("response_id") or payload.get("id")
    if value:
        return str(value)
    return None


def _output_text_from_payload(payload: object) -> str | None:
    if not isinstance(payload, dict):
        return None
    response = payload.get("response")
    if not isinstance(response, dict):
        return None
    output = response.get("output")
    if not isinstance(output, list):
        return None
    parts: list[str] = []
    for item in output:
        if not isinstance(item, dict):
            continue
        content = item.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            text = block.get("text")
            if isinstance(text, str) and text:
                parts.append(text)
    if parts:
        return "".join(parts)
    return None


def _output_item_metadata(payload: object) -> dict | None:
    if not isinstance(payload, dict):
        return None
    item = payload.get("item")
    if not isinstance(item, dict):
        return None
    metadata = item.get("metadata")
    if not isinstance(metadata, dict):
        return None
    return metadata


def _is_participant_chat_item(payload: object) -> bool:
    metadata = _output_item_metadata(payload)
    if not isinstance(metadata, dict):
        return False
    return str(metadata.get("meeting_event_type") or "") == "chat.message.received"


def _meeting_event_id_from_payload(payload: object) -> str | None:
    metadata = _output_item_metadata(payload)
    if not isinstance(metadata, dict):
        return None
    value = metadata.get("meeting_event_id")
    if value:
        return str(value)
    return None


def _meeting_state_path() -> Path:
    return Path(tempfile.gettempdir()) / "20minds_meeting_bot_seen_events.json"


def _meeting_state_key(meet_url: str) -> str:
    return str(meet_url or "").strip()


def _load_seen_event_ids(meet_url: str) -> set[str]:
    path = _meeting_state_path()
    if not path.exists():
        return set()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return set()
    values = payload.get(_meeting_state_key(meet_url))
    if not isinstance(values, list):
        return set()
    return {str(value) for value in values if str(value).strip()}


def _save_seen_event_ids(meet_url: str, seen_event_ids: set[str]) -> None:
    path = _meeting_state_path()
    payload: dict[str, list[str]] = {}
    if path.exists():
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                payload = {str(k): [str(v) for v in vals] for k, vals in raw.items() if isinstance(vals, list)}
        except Exception:
            payload = {}
    key = _meeting_state_key(meet_url)
    payload[key] = sorted(seen_event_ids)[-500:]
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _send_once(api_key: str, meet_url: str, text: str) -> int:
    response = requests.post(
        "https://api.20minds.ai/v1/meeting-bot/responses",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        json={
            "input": text,
            "stream": False,
            "meeting_url": meet_url,
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    delivery_status = str(((payload.get("metadata") or {}).get("delivery_status")) or "unknown")
    print(f"[sent:{delivery_status}] {text}")
    return 0


def _send_figure_once(api_key: str, meet_url: str, figure_path: str) -> int:
    path = Path(figure_path).expanduser()
    if not path.exists() or not path.is_file():
        raise SystemExit(f"Figure file not found: {figure_path}")
    raw = path.read_bytes()
    if not raw:
        raise SystemExit(f"Figure file is empty: {figure_path}")
    content_type, _ = mimetypes.guess_type(path.name)
    response = requests.post(
        "https://api.20minds.ai/v1/meeting-bot/figures",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        json={
            "meeting_url": meet_url,
            "figure_b64": base64.b64encode(raw).decode("ascii"),
            "content_type": content_type or "application/octet-stream",
            "filename": path.name,
        },
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    delivery_status = str(payload.get("delivery_status") or "unknown")
    print(f"[figure:{delivery_status}] {path.name}")
    return 0


def _stop_figures_once(api_key: str, meet_url: str) -> int:
    response = requests.delete(
        "https://api.20minds.ai/v1/meeting-bot/figures",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        json={
            "meeting_url": meet_url,
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    delivery_status = str(payload.get("delivery_status") or "unknown")
    print(f"[figure:{delivery_status}] stop")
    return 0


def _leave_call_once(api_key: str, meet_url: str) -> int:
    response = requests.post(
        "https://api.20minds.ai/v1/meeting-bot/responses",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        json={
            "meeting_url": meet_url,
            "stream": False,
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    response_id = str(payload.get("id") or payload.get("response_id") or "")
    if not response_id:
        raise SystemExit("Meeting-bot leave request did not return a response id.")
    delete_response = requests.delete(
        f"https://api.20minds.ai/v1/meeting-bot/responses/{response_id}",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        },
        timeout=30,
    )
    delete_response.raise_for_status()
    delivery_status = "left"
    print(f"[leave:{delivery_status}] {meet_url}")
    return 0


def _should_send_input(args: argparse.Namespace) -> bool:
    if args.listen_only:
        return False
    # When doing a figure/stop/leave action, only send input if the user explicitly provided it.
    if (args.figure or args.stop_figures or args.leave_call) and args.input is _INPUT_NOT_SET:
        return False
    return bool(args.input if args.input is not _INPUT_NOT_SET else _DEFAULT_GREETING)


def main() -> None:
    args = parse_args()

    try:
        meet_url = validate_meet_url(args.meet_url)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2) from exc

    api_key = load_api_key(args.api_key_env)
    if not api_key:
        print(
            f"Missing API key. Set {args.api_key_env} in the environment or in a .env file before running this command.",
            file=sys.stderr,
        )
        raise SystemExit(2)

    if not args.listen_only:
        if _should_send_input(args):
            _send_once(api_key, meet_url, args.input if args.input is not _INPUT_NOT_SET else _DEFAULT_GREETING)
        if args.figure:
            _send_figure_once(api_key, meet_url, args.figure)
        if args.stop_figures:
            _stop_figures_once(api_key, meet_url)
        if args.leave_call:
            _leave_call_once(api_key, meet_url)
        if not _should_send_input(args) and not args.figure and not args.stop_figures and not args.leave_call:
            raise SystemExit("Either --input, --figure, --stop-figures, --leave-call, or --listen-only is required.")
        raise SystemExit(0)

    response_id: str | None = None
    saw_text_delta = False
    saw_participant_chat = False
    saw_created = False
    saw_completed = False
    printed_output = False
    seen_event_ids = _load_seen_event_ids(meet_url)
    active_participant_event_id: str | None = None
    deadline = time.time() + max(1, int(args.wait_seconds or 45))
    while time.time() < deadline and not saw_completed and not (args.until_incoming_chat and saw_participant_chat):
        current_response_id: str | None = None
        response = requests.post(
            "https://api.20minds.ai/v1/meeting-bot/responses",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
            },
            json={
                "input": "" if args.listen_only else args.input,
                "stream": True,
                "meeting_url": meet_url,
            },
            stream=True,
            timeout=(30, max(60, int(args.wait_seconds or 45) + 30)),
        )
        response.raise_for_status()

        event_name: str | None = None
        data_lines: list[str] = []
        for raw_line in response.iter_lines(decode_unicode=True):
            if time.time() > deadline:
                break

            line = raw_line or ""
            if not line:
                if not event_name:
                    continue
                payload = _parse_sse_data(data_lines)
                event_type = event_name
                event_name = None
                data_lines = []
            elif line.startswith("event:"):
                event_name = line.split(":", 1)[1].strip()
                continue
            elif line.startswith("data:"):
                data_lines.append(line.split(":", 1)[1].lstrip())
                continue
            else:
                continue

            if event_type == "response.created":
                saw_created = True
                current_response_id = _response_id_from_payload(payload) or current_response_id
                if current_response_id:
                    response_id = current_response_id
            elif event_type == "response.output_item.added":
                if _is_participant_chat_item(payload):
                    event_id = _meeting_event_id_from_payload(payload)
                    if event_id and event_id in seen_event_ids:
                        active_participant_event_id = "__skip__"
                    else:
                        active_participant_event_id = event_id or "__new__"
                        if event_id:
                            seen_event_ids.add(event_id)
                            _save_seen_event_ids(meet_url, seen_event_ids)
                else:
                    active_participant_event_id = None
            elif event_type == "response.output_text.delta":
                delta = ""
                if isinstance(payload, dict):
                    delta = str(payload.get("delta") or "")
                if delta:
                    if active_participant_event_id == "__skip__":
                        continue
                    if active_participant_event_id and active_participant_event_id != "__skip__":
                        print(delta, end="", flush=True)
                        saw_text_delta = True
                        printed_output = True
                        saw_participant_chat = True
                        break
                    print(delta, end="", flush=True)
                    saw_text_delta = True
                    printed_output = True
            elif event_type == "response.completed":
                saw_completed = True
                current_response_id = _response_id_from_payload(payload) or current_response_id
                if current_response_id:
                    response_id = current_response_id
                if not saw_text_delta:
                    output_text = _output_text_from_payload(payload)
                    if output_text:
                        print(output_text)
                        printed_output = True
                    else:
                        print(json.dumps(payload, indent=2))
                        printed_output = True
            elif event_type == "response.failed":
                print(json.dumps(payload, indent=2), file=sys.stderr)
            deadline = time.time() + max(1, int(args.wait_seconds or 45))
        if saw_text_delta:
            print()
        if saw_completed or saw_text_delta or (args.until_incoming_chat and saw_participant_chat) or time.time() >= deadline:
            break
        time.sleep(2)

    if not (saw_created or saw_text_delta or saw_completed):
        print(
            f"Meeting-bot request emitted no recognizable response events within {args.wait_seconds} seconds.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    if saw_text_delta and not saw_completed:
        return

    if not saw_completed:
        print("Meeting-bot request did not complete.", file=sys.stderr)
        raise SystemExit(1)

    if not printed_output:
        print(
            "Meeting-bot request completed but returned no text.",
            file=sys.stderr,
        )
        raise SystemExit(1)


if __name__ == "__main__":
    main()
