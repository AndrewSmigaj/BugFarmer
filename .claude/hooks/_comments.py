"""Shared by the two doc-drift checks: did a change touch only comments?

A source file whose code is identical before and after, once comments (and Python docstrings) are removed,
can't have made its doc stale, so neither check counts it (added 2026-09-27, after a sweep that reworded
comments in nine source files was blocked for thirteen docs it could not have affected).

Conservative by design: identical text, other file types, and anything that won't tokenise or parse all
count as a real change. Go is compared token by token (literals kept verbatim, line breaks kept because Go
inserts semicolons at them); Python by its syntax tree, which never contains comments.

Tests: $CLAUDE_DIFF_CONTENT names a JSON file {path: {"old": text, "new": text}} that stands in for the
real versions of those paths.
"""
import ast
import json
import os
import subprocess

CODE_SUFFIXES = (".go", ".py")


def _git(args, cwd=None):
    r = subprocess.run(["git"] + args, capture_output=True, timeout=15, cwd=cwd)
    return r.stdout.decode("utf-8") if r.returncode == 0 else None


def _fixture(path):
    fixture = os.environ.get("CLAUDE_DIFF_CONTENT")
    if fixture is None:
        return None
    with open(fixture, encoding="utf-8") as f:
        entry = json.load(f).get(path) or {}
    return entry.get("old"), entry.get("new")


def staged_versions(path):
    """(HEAD, index) text of a repo-relative path; None for a side that doesn't exist."""
    fx = _fixture(path)
    if fx is not None:
        return fx
    return _git(["show", "HEAD:" + path]), _git(["show", ":" + path])


def worktree_versions(path):
    """(HEAD, working tree) text of a path (absolute or repo-relative); None for a missing side."""
    fx = _fixture(path)
    if fx is not None:
        return fx
    root = (_git(["rev-parse", "--show-toplevel"]) or "").strip()
    if not root:
        return None, None
    rel = os.path.relpath(path, root) if os.path.isabs(path) else path
    if rel.startswith(".."):
        return None, None
    try:
        with open(os.path.join(root, rel), encoding="utf-8") as f:
            new = f.read()
    except OSError:
        new = None
    return _git(["show", "HEAD:" + rel.replace(os.sep, "/")], cwd=root), new


def _go_literal_end(src, i):
    """Index just past the string or rune literal that starts at src[i]."""
    quote = src[i]
    if quote == "`":
        j = src.find("`", i + 1)
        if j < 0:
            raise ValueError("unterminated raw string")
        return j + 1
    j = i + 1
    while j < len(src):
        ch = src[j]
        if ch == "\\":
            j += 2
            continue
        if ch == quote:
            return j + 1
        if ch == "\n":
            raise ValueError("newline in a literal")
        j += 1
    raise ValueError("unterminated literal")


def _go_code(src):
    """Go source as tokens, comments removed. A block comment that spans lines counts as a line break,
    as it does for Go's semicolon insertion."""
    toks, word, i, n = [], [], 0, len(src)

    def flush():
        if word:
            toks.append("".join(word))
            word.clear()

    while i < n:
        c = src[i]
        if src.startswith("//", i):
            j = src.find("\n", i)
            i = n if j < 0 else j
        elif src.startswith("/*", i):
            j = src.find("*/", i + 2)
            if j < 0:
                raise ValueError("unterminated comment")
            flush()
            if "\n" in src[i:j]:
                toks.append("\n")
            i = j + 2
        elif c in "\"'`":
            flush()
            j = _go_literal_end(src, i)
            toks.append(src[i:j])
            i = j
        elif c == "\n":
            flush()
            toks.append("\n")
            i += 1
        elif c in " \t\r\f\v":
            flush()
            i += 1
        else:
            word.append(c)
            i += 1
    flush()
    out = []
    for t in toks:
        if t == "\n" and (not out or out[-1] == "\n"):
            continue
        out.append(t)
    while out and out[-1] == "\n":
        out.pop()
    return out


def _py_code(src):
    """Python source as its syntax tree without docstrings."""
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = node.body
            if (body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                node.body = body[1:]
    return ast.dump(tree, include_attributes=False)


def comments_only(path, old, new):
    """True only when the text changed but the code did not. Anything uncertain returns False."""
    if old is None or new is None or old == new:
        return False
    try:
        if path.endswith(".go"):
            return _go_code(old) == _go_code(new)
        if path.endswith(".py"):
            return _py_code(old) == _py_code(new)
    except (ValueError, SyntaxError):
        return False
    return False
