# BUG-001: Memory Consolidation Type Error

## Summary

Memory consolidation fails when LLM returns JSON with non-string values for `history_entry` or `memory_update`.

## Error Log

```
[2026-02-14 22:50:29] [ERROR] Memory consolidation failed: data must be str, not dict
```

## Environment

- **Version**: nanobot v0.1.3.post7 (upstream main)
- **Platform**: Windows 11
- **Python**: 3.11.9
- **Trigger**: Automatic memory consolidation after message threshold

## Steps to Reproduce

**Scenario**: After a long conversation with the agent, the automatic memory consolidation is triggered.

**Steps**:

1. **Start conversation**: Run `nanobot agent` or send messages via any channel (Telegram, Feishu, etc.)
2. **Accumulate messages**: Chat normally, send approximately **50-60 messages** (can be Q&A, file operations, etc.)
3. **Trigger consolidation**: Send the 51st+ message, or use the `/new` command to manually trigger consolidation
4. **Observe result**: Check terminal logs or log files, you may see:
   ```
   [ERROR] Memory consolidation failed: data must be str, not dict
   ```

**Note**: Bug trigger has some randomness depending on LLM response format. The error occurs when the LLM returns `history_entry` or `memory_update` as JSON objects instead of strings. If not triggered on first try, the `/new` command can be used to retry consolidation.

## Root Cause Analysis

### Code Location
`nanobot/agent/loop.py:402-406`

```python
if entry := result.get("history_entry"):
    memory.append_history(entry)  # Expects str, but may receive dict
if update := result.get("memory_update"):
    if update != current_memory:
        memory.write_long_term(update)  # Expects str, but may receive dict
```

### Problem

The prompt explicitly asks LLM to return JSON ("Respond with ONLY valid JSON"), and the code uses `json.loads()` to parse the response. However, the issue is that **LLM may return JSON objects as values instead of strings**:

```json
// Expected (strings as values)
{
  "history_entry": "[2026-02-14 22:50] User asked about...",
  "memory_update": "- Host: HARRYBOOK-T14P"
}

// Actual (objects as values) - causes the bug
{
  "history_entry": {"timestamp": "2026-02-14", "summary": "User asked..."},
  "memory_update": {"facts": ["Host: HARRYBOOK-T14P"]}
}
```

The `MemoryStore.append_history()` and `MemoryStore.write_long_term()` methods expect string arguments:

```python
# nanobot/agent/memory.py:21-26
def write_long_term(self, content: str) -> None:
    self.memory_file.write_text(content, encoding="utf-8")

def append_history(self, entry: str) -> None:
    with open(self.history_file, "a", encoding="utf-8") as f:
        f.write(entry.rstrip() + "\n\n")
```

However, the LLM may return JSON where values are objects instead of strings:

```json
{
  "history_entry": {"timestamp": "2026-02-14 22:50", "summary": "..."},
  "memory_update": {"facts": ["fact1", "fact2"]}
}
```

Instead of expected:

```json
{
  "history_entry": "[2026-02-14 22:50] User asked about...",
  "memory_update": "- Host: HARRYBOOK-T14P\n- Name: Nado"
}
```

## Impact

- Memory consolidation fails silently (only logged as error)
- Old messages are not archived to HISTORY.md
- Long-term memory is not updated
- Session grows indefinitely without consolidation

## Proposed Fix

### Recommended Approach: Prompt + Defense

Combine both prompt optimization and code-level type checking for maximum robustness.

#### 1. Prompt Optimization

Update the prompt to explicitly instruct LLM to return string values:

```python
prompt = f"""You are a memory consolidation agent. Process this conversation and return a JSON object with exactly two keys:

1. "history_entry": A paragraph (2-5 sentences) summarizing the key events/decisions/topics. Start with a timestamp like [YYYY-MM-DD HH:MM].

2. "memory_update": The updated long-term memory content. Add any new facts: user location, preferences, personal info, habits, project context, technical decisions, tools/services used. If nothing new, return the existing content unchanged.

**IMPORTANT**: Both values MUST be strings, not objects or arrays.

Example:
{{
  "history_entry": "[2026-02-14 22:50] User asked about...",
  "memory_update": "- Host: HARRYBOOK-T14P\\n- Name: Nado"
}}

## Current Long-term Memory
{current_memory or "(empty)"}

## Conversation to Process
{conversation}

Respond with ONLY valid JSON, no markdown fences."""
```

#### 2. Code-Level Defense

Add type checking in `nanobot/agent/loop.py` to handle cases where LLM still returns non-string values:

```python
if entry := result.get("history_entry"):
    # Defensive: ensure entry is a string
    if not isinstance(entry, str):
        entry = json.dumps(entry, ensure_ascii=False)
    memory.append_history(entry)
if update := result.get("memory_update"):
    # Defensive: ensure update is a string
    if not isinstance(update, str):
        update = json.dumps(update, ensure_ascii=False)
    if update != current_memory:
        memory.write_long_term(update)
```

**Why `json.dumps()` instead of `str()`?**

| Method | Output Example | Issue |
|--------|---------------|-------|
| `str({"key": "value"})` | `"{'key': 'value'}"` | Uses single quotes (Python repr), not valid JSON, harder to read |
| `json.dumps({"key": "value"})` | `'{"key": "value"}'` | Valid JSON format, consistent with LLM output, better readability |

Using `str()` would store Python dict representation in markdown files, which is inconsistent and harder to parse if needed later.

### Why Keep Both Solutions?

**Prompt optimization alone is sufficient for most cases**, but code-level defense is recommended for:

1. **Robustness**: Different LLM models interpret prompts differently. Some local models may be more "creative" with JSON output.
2. **Future-proofing**: If users switch to different LLM providers, the prompt may not work as effectively.
3. **Graceful degradation**: Code defense ensures the system continues to function (even with suboptimal formatting) rather than crashing with `TypeError`.

**Recommended strategy**: Start with prompt optimization only. If error reports persist, add the code-level type checking as a safety net.

## Status

- [x] Identified
- [x] Analyzed
- [ ] Fixed (proposed)
- [ ] Tested
- [ ] PR submitted to upstream

## References

- Related: Memory system v2 (upstream v0.1.3.post7)
- Files: `nanobot/agent/loop.py`, `nanobot/agent/memory.py`
