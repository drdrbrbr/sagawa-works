#!/usr/bin/env python3
"""
Claude Code の会話履歴を Obsidian 用 Markdown に変換するスクリプト
使い方: python3 export-chat.py <session-id> [output-dir]
"""

import json
import sys
import os
from datetime import datetime, timezone

HISTORY_DIR = os.path.expanduser("~/.claude/projects/-Users-t-sagawa")
DEFAULT_OUTPUT = os.path.expanduser(
    "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Vault2026/Claude"
)

def load_session(session_id):
    path = os.path.join(HISTORY_DIR, f"{session_id}.jsonl")
    if not os.path.exists(path):
        print(f"セッションが見つかりません: {path}")
        sys.exit(1)
    messages = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                messages.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return messages

def extract_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "\n".join(parts)
    return ""

SKIP_PATTERNS = ["<local-command-caveat>", "<local-command-stdout>", "<command-name>", "<bash-input>", "<system-reminder>", "<task-notification>", "Unknown skill:"]

def convert_to_markdown(messages):
    lines = []
    date_str = datetime.now().strftime("%Y-%m-%d")

    lines.append(f"---\ntags:\n  - claude\ndate: {date_str}\n---\n")

    for msg in messages:
        role = msg.get("role") or (msg.get("message") or {}).get("role")
        content_raw = msg.get("content") or (msg.get("message") or {}).get("content", "")
        text = extract_text(content_raw).strip()

        if not text or not role:
            continue
        if any(p in text for p in SKIP_PATTERNS):
            continue
        if role not in ("user", "assistant"):
            continue

        label = "**You**" if role == "user" else "**Claude**"
        lines.append(f"{label}\n{text}\n")

    return "\n".join(lines)

def latest_session():
    files = [f for f in os.listdir(HISTORY_DIR) if f.endswith(".jsonl")]
    if not files:
        print("セッションが見つかりません")
        sys.exit(1)
    latest = max(files, key=lambda f: os.path.getmtime(os.path.join(HISTORY_DIR, f)))
    return latest.replace(".jsonl", "")

def main():
    session_id = sys.argv[1] if len(sys.argv) > 1 else latest_session()
    output_dir = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT

    os.makedirs(output_dir, exist_ok=True)

    messages = load_session(session_id)
    markdown = convert_to_markdown(messages)

    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date_str}-claude-{session_id[:8]}.md"
    output_path = os.path.join(output_dir, filename)

    with open(output_path, "w") as f:
        f.write(markdown)

    print(f"書き出し完了: {output_path}")

if __name__ == "__main__":
    main()
