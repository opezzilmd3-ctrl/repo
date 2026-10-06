#!/usr/bin/env python3
"""统计 Claude Code / Codex 一次会话的执行步数。
Count execution steps of one Claude Code / Codex session.

口径：主模型每生成一次回复记一步；一次回复里有多个工具操作也只记一步；
不计用户消息、工具返回、子 agent 和其他辅助模型；多轮对话各轮相加。

用法：
  任务完成后，在同一会话里把本脚本发给 agent，请它运行 python3 count_steps.py。
  脚本会找到当前会话，只统计“请求统计之前”的步数；读不到会话记录时，会输出计数口径让 agent 自行统计。
  python3 count_steps.py claude       # 手动：Claude Code 最近一次会话
  python3 count_steps.py codex        # 手动：Codex 最近一次会话
  python3 count_steps.py <会话.jsonl>  # 手动：统计指定会话文件
"""
import json
import sys
import time
from pathlib import Path

CLAUDE_DIR = Path.home() / ".claude" / "projects"
CODEX_DIR = Path.home() / ".codex" / "sessions"

# Codex 记录里属于模型输出的条目（web_search_call 是模型在同一次回复里联网，不单独成步）
CODEX_MODEL_ITEMS = {"reasoning", "function_call", "custom_tool_call", "local_shell_call",
                     "web_search_call", "tool_search_call"}
CODEX_TOOL_ITEMS = CODEX_MODEL_ITEMS - {"reasoning"}


COUNT_REQUEST = "count_steps"  # 专家请求统计的那条消息里一定会出现脚本名

FALLBACK = """未找到可读取的会话记录（本脚本能读取 Claude Code 和 Codex 的会话）。
请你按以下口径回顾本次会话，自行统计执行步数：
- 统计范围：从用户发出任务开始，到用户请求统计步数之前为止；
- 你（主模型）每生成一次回复记一步，包括只调用工具的回复；一次回复里调用多个工具也只记一步；
- 不计用户消息、工具返回结果、子 agent 的回复。
请告诉用户：“执行步数：N”，并说明是精确计数还是估算（例如早期上下文已被压缩、无法完整回顾时属于估算）。

No readable session log was found (this script reads Claude Code and Codex sessions).
Please review this session and count your execution steps yourself:
- Scope: from the user's task message up to (not including) the request to count steps;
- Each reply you (the main model) generate is one step, including replies that only call tools; a reply that calls several tools is still one step;
- Do not count user messages, tool results, or sub-agent replies.
Tell the user "Steps: N" and say whether it is an exact count or an estimate (e.g. an estimate if earlier context was compacted)."""


def session_files(which):
    files = []
    if which in ("any", "claude"):
        files += [f for f in CLAUDE_DIR.glob("*/*.jsonl") if f.is_file()]
    if which in ("any", "codex"):
        files += [f for f in CODEX_DIR.glob("**/rollout-*.jsonl") if f.is_file()]
    return sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)


def latest_session(which):
    files = session_files(which)
    if not files:
        sys.exit(f"没有找到会话记录 / no session found ({CLAUDE_DIR} or {CODEX_DIR})")
    return files[0]


def count_request_index(rows):
    """最后一条请求统计步数的用户消息的位置；没有则返回 None。"""
    idx = None
    for i, r in enumerate(rows):
        if is_codex_row(r):
            p = r.get("payload") or {}
            if r.get("type") == "response_item" and p.get("type") == "message" and p.get("role") == "user":
                text = " ".join(b.get("text", "") for b in p.get("content", []) if isinstance(b, dict))
            else:
                continue
        else:
            text = claude_user_text(r) or ""
        if COUNT_REQUEST in text.lower():
            idx = i
    return idx


def is_codex_row(r):
    return r.get("type") in ("session_meta", "response_item", "event_msg", "turn_context", "compacted")


def load(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return rows


def is_codex(rows):
    return any(r.get("type") in ("session_meta", "response_item") for r in rows[:50])


# ---------- Claude Code ----------

def claude_user_text(row):
    """真实的用户提问返回文本，工具结果、系统注入、命令输出返回 None。"""
    att = row.get("attachment") or {}
    if row.get("type") == "attachment" and att.get("type") == "queued_command":
        content = att.get("prompt")  # 模型执行中途插话的消息
    elif row.get("type") != "user" or row.get("isMeta") or row.get("isCompactSummary"):
        return None
    else:
        content = row.get("message", {}).get("content")
    if isinstance(content, list):
        if any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
            return None
        content = " ".join(b.get("text", "") or f"[{b.get('type')}]" for b in content if isinstance(b, dict))
    if not isinstance(content, str) or not content.strip():
        return None
    if content.lstrip().startswith(("<command-", "<local-command", "[Request interrupted")):
        return None
    return content.strip()


def count_claude(path, rows):
    # 一次回复在记录里按内容块拆成多行（思考/文字/每个工具各一行），同一个 message.id
    steps, tools, errors = set(), 0, 0
    # 交互式会话用 isSidechain 标子 agent，`claude -p --output-format stream-json` 的输出用 parent_tool_use_id
    for r in rows:
        if r.get("type") != "assistant" or r.get("isSidechain") or r.get("parent_tool_use_id"):
            continue
        msg = r.get("message", {})
        if msg.get("model") == "<synthetic>":  # 报错、限流等提示，不是模型回复
            errors += 1
            continue
        steps.add(msg.get("id") or r.get("requestId") or r.get("uuid"))
        tools += sum(1 for b in msg.get("content", []) if isinstance(b, dict) and b.get("type") == "tool_use")
    prompts = [t for t in map(claude_user_text, rows) if t]
    sub_dir = Path(path).with_suffix("") / "subagents"
    sub_rows = [r for f in (sub_dir.glob("*.jsonl") if sub_dir.is_dir() else []) for r in load(f)]
    sub_rows += [r for r in rows if r.get("parent_tool_use_id")]
    sub_steps = len({r["message"].get("id") for r in sub_rows
                     if r.get("type") == "assistant" and r.get("message", {}).get("model") != "<synthetic>"})
    return {
        "tool": "Claude Code",
        "steps": len(steps),
        "prompts": prompts,
        "tool_calls": tools,
        "notes": ([f"用了子 agent，其 {sub_steps} 步未计入 / {sub_steps} sub-agent steps not counted"] if sub_steps else [])
                 + ([f"有 {errors} 条报错/限流提示，未计入步数 / {errors} error messages not counted"] if errors else [])
                 + (["会话中途压缩过上下文 / context was compacted during the session"] if any(r.get("isCompactSummary") for r in rows) else []),
    }


# ---------- Codex ----------

def count_codex(rows):
    # 模型每次回复写出若干条目（思考、消息、工具调用），回复结束时记一条带用量的 token_count；
    # 以 token_count 为分隔，含模型输出的每一段算一步
    # 压缩上下文的调用也记 token_count，但不产出模型条目，所以不会被算成一步
    steps, tools, in_reply = 0, 0, False
    turns, prompts, subagent, inherited = 0, [], False, False
    for r in rows:
        kind, p = r.get("type"), r.get("payload") or {}
        pt = p.get("type")
        if kind == "compacted" and steps == 0:
            inherited = True  # 一开头就是压缩摘要：接续自别的会话
        elif kind == "inter_agent_communication_metadata":
            subagent = True
        elif kind == "event_msg" and pt == "task_started":
            turns += 1  # 用户每发一次消息开始一个 task
        elif kind == "event_msg" and pt == "token_count" and p.get("info"):
            in_reply = False
        elif kind == "response_item":
            if pt in CODEX_MODEL_ITEMS or (pt == "message" and p.get("role") == "assistant"):
                if not in_reply:
                    steps += 1
                    in_reply = True
                tools += pt in CODEX_TOOL_ITEMS
            elif pt == "message" and p.get("role") == "user":
                # 用户消息里混有系统注入的环境信息，只保留像真实提问的文本用于核对
                text = " ".join(b.get("text", "") for b in p.get("content", []) if isinstance(b, dict)).strip()
                if text and not text.startswith(("<", "The following is the Codex agent history")):
                    prompts.append(text)
    return {
        "tool": "Codex",
        "steps": steps,
        "turns": turns,
        "prompts": prompts,
        "tool_calls": tools,
        "notes": (["这个会话接续自更早的会话，之前的步数不在本文件里，请一题开一个新会话重跑 / this session continues an earlier one; start a fresh session per task and re-run"] if inherited else [])
                 + (["这是一个子 agent 的会话文件，请改为统计主会话 / this is a sub-agent session; count the main session instead"] if subagent else []),
    }


def find_current_session():
    """agent 运行本脚本时，当前会话刚被写入，且含有请求统计的消息。"""
    now = time.time()
    for f in session_files("any"):
        if now - f.stat().st_mtime > 30 * 60:
            break
        rows = load(f)
        cut = count_request_index(rows)
        if cut is not None:
            return f, rows[:cut]
    return None, None


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    if arg is None:
        path, rows = find_current_session()
        if path is None:
            print(FALLBACK)
            return
    else:
        path = latest_session(arg) if arg in ("claude", "codex") else Path(arg)
        rows = load(path)
        cut = count_request_index(rows)  # 手动统计时同样不计请求统计之后的步数，和 agent 报的数一致
        if cut is not None:
            rows = rows[:cut]
    res = count_codex(rows) if is_codex(rows) else count_claude(path, rows)
    if arg is None:
        print(f"请把这一行原样告诉用户 / Tell the user: 执行步数 Steps: {res['steps']}")
    print(f"工具 Agent: {res['tool']}")
    print(f"会话文件 Session file: {path}")
    print(f"第一条提问 First prompt: {res['prompts'][0][:80] if res['prompts'] else ''}")
    print(f"执行步数 Steps: {res['steps']}")
    print(f"用户轮次 User turns: {res.get('turns', len(res['prompts']))}（多轮时步数为各轮相加 / steps are summed across turns）")
    print(f"工具调用次数 Tool calls: {res['tool_calls']}（仅供参考，不是步数 / for reference only, not steps）")
    for note in res["notes"]:
        print(f"提示 Note: {note}")


if __name__ == "__main__":
    main()
