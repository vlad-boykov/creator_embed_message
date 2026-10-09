import base64
import ctypes
import ctypes.wintypes as wintypes
import json
import os
import sys
from pathlib import Path

from config import DRAFT_PATH, TOKEN_PATH
from .models import DraftState


class _DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]


def _blob(data: bytes) -> _DATA_BLOB:
    buf = ctypes.create_string_buffer(data)
    return _DATA_BLOB(len(data), ctypes.cast(buf, ctypes.POINTER(ctypes.c_byte)))


def protect_windows(data: bytes) -> bytes:
    if sys.platform != "win32":
        raise RuntimeError("Защищённое хранилище токена доступно в Windows.")
    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32
    src = _blob(data)
    dst = _DATA_BLOB()
    if not crypt32.CryptProtectData(ctypes.byref(src), "Rustik Fox token", None, None, None, 0, ctypes.byref(dst)):
        raise ctypes.WinError()
    try:
        return ctypes.string_at(dst.pbData, dst.cbData)
    finally:
        kernel32.LocalFree(dst.pbData)


def unprotect_windows(data: bytes) -> bytes:
    if sys.platform != "win32":
        raise RuntimeError("Защищённое хранилище токена доступно в Windows.")
    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32
    src = _blob(data)
    dst = _DATA_BLOB()
    if not crypt32.CryptUnprotectData(ctypes.byref(src), None, None, None, None, 0, ctypes.byref(dst)):
        raise ctypes.WinError()
    try:
        return ctypes.string_at(dst.pbData, dst.cbData)
    finally:
        kernel32.LocalFree(dst.pbData)


def save_token(token: str) -> None:
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_bytes(protect_windows(token.encode("utf-8")))


def load_token() -> str:
    if not TOKEN_PATH.exists():
        return ""
    try:
        return unprotect_windows(TOKEN_PATH.read_bytes()).decode("utf-8")
    except Exception:
        return ""


def delete_token() -> None:
    try:
        TOKEN_PATH.unlink()
    except FileNotFoundError:
        pass


def save_draft(draft: DraftState) -> None:
    DRAFT_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = DRAFT_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(draft.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, DRAFT_PATH)


def load_draft() -> DraftState:
    if not DRAFT_PATH.exists():
        return DraftState()
    try:
        return DraftState.from_dict(json.loads(DRAFT_PATH.read_text(encoding="utf-8")))
    except Exception:
        return DraftState()
