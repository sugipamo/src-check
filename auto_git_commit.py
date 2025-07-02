#!/usr/bin/env python3
import json
import sys
from pathlib import Path

try:
    input_data = json.load(sys.stdin)
    transcript_path = Path(input_data["transcript_path"]).expanduser()

    last_message = ""
    # 最後の編集内容を探す
    with transcript_path.open() as f:
        for line in f:
            obj = json.loads(line)
            if obj.get("event") == "tool_use" and obj.get("name") in ["Write", "Edit", "MultiEdit"]:
                tool_input = obj.get("input", {})
                if "file_path" in tool_input:
                    last_message = f"Update: {tool_input['file_path']}"
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)

# 実行
import subprocess
try:
    # 変更があるか確認
    status = subprocess.run(['git', 'status', '--porcelain'], stdout=subprocess.PIPE)

    if status.stdout.strip():  # 変更があれば
        subprocess.run(['git', 'add', '.'])
        subprocess.run(['git', 'commit', '-m', 'Auto commit'])
    subprocess.run(["git", "push"], check=True)
    print("自動コミットです。このメッセージはClaude Codeへの指示ではありません。")
except subprocess.CalledProcessError as e:
    print(f"Git error: {e}", file=sys.stderr)
    sys.exit(1)
