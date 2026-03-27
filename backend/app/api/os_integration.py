"""OS integration for native file dialogs and folder opening.

Cross-platform approach using native OS file dialog commands:
- Linux: kdialog (KDE) → zenity (GNOME/GTK) → tkinter (fallback)
- macOS: osascript (native Cocoa dialog)
- Windows: PowerShell (native Windows dialog)
"""
import os
import subprocess
import sys
import logging
import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/system", tags=["OS Integration"])


class FilePathRequest(BaseModel):
    file_path: str


# ─── Platform-specific dialog helpers ───────────────────────────────────────


def _pick_file_linux(title: str = "Select File") -> str | None:
    """Try native Linux file pickers in priority order."""
    # 1. Try kdialog (KDE native)
    try:
        res = subprocess.run(
            ["kdialog", "--getopenfilename", os.path.expanduser("~"), "*"],
            capture_output=True, text=True, timeout=120,
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
        return None  # user cancelled
    except FileNotFoundError:
        pass

    # 2. Try zenity (GNOME/GTK native)
    try:
        res = subprocess.run(
            ["zenity", "--file-selection", f"--title={title}"],
            capture_output=True, text=True, timeout=120,
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
        return None
    except FileNotFoundError:
        pass

    # 3. Fallback to tkinter
    return _pick_file_tkinter(title)


def _save_file_linux(default_name: str, title: str = "Save File") -> str | None:
    """Try native Linux save dialogs in priority order."""
    home = os.path.expanduser("~")
    default_path = os.path.join(home, default_name)

    # 1. Try kdialog (KDE native — properly supports --default)
    try:
        res = subprocess.run(
            ["kdialog", "--getsavefilename", default_path, "*"],
            capture_output=True, text=True, timeout=120,
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
        return None
    except FileNotFoundError:
        pass

    # 2. Try zenity (GNOME/GTK native)
    try:
        res = subprocess.run(
            [
                "zenity", "--file-selection", "--save",
                "--confirm-overwrite",
                f"--filename={default_path}",
                f"--title={title}",
            ],
            capture_output=True, text=True, timeout=120,
        )
        logger.debug(f"Zenity save: rc={res.returncode}, out='{res.stdout.strip()}'")
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
        return None
    except FileNotFoundError:
        pass

    # 3. Fallback to tkinter
    return _save_file_tkinter(default_name, title)


def _pick_file_macos(title: str = "Select File") -> str | None:
    """macOS native file picker via osascript."""
    script = f'''
    set theFile to choose file with prompt "{title}"
    return POSIX path of theFile
    '''
    try:
        res = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=120,
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
        return None
    except Exception:
        return _pick_file_tkinter(title)


def _save_file_macos(default_name: str, title: str = "Save File") -> str | None:
    """macOS native save dialog via osascript."""
    script = f'''
    set theFile to choose file name with prompt "{title}" default name "{default_name}"
    return POSIX path of theFile
    '''
    try:
        res = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=120,
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
        return None
    except Exception:
        return _save_file_tkinter(default_name, title)


def _pick_file_windows(title: str = "Select File") -> str | None:
    """Windows native file picker via PowerShell."""
    ps_script = f'''
    Add-Type -AssemblyName System.Windows.Forms
    $dialog = New-Object System.Windows.Forms.OpenFileDialog
    $dialog.Title = "{title}"
    $dialog.InitialDirectory = [Environment]::GetFolderPath("UserProfile")
    $result = $dialog.ShowDialog()
    if ($result -eq [System.Windows.Forms.DialogResult]::OK) {{
        Write-Output $dialog.FileName
    }}
    '''
    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            capture_output=True, text=True, timeout=120,
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
        return None
    except Exception:
        return _pick_file_tkinter(title)


def _save_file_windows(default_name: str, title: str = "Save File") -> str | None:
    """Windows native save dialog via PowerShell."""
    ext = os.path.splitext(default_name)[1].lstrip('.') if '.' in default_name else 'txt'
    ps_script = f'''
    Add-Type -AssemblyName System.Windows.Forms
    $dialog = New-Object System.Windows.Forms.SaveFileDialog
    $dialog.Title = "{title}"
    $dialog.FileName = "{default_name}"
    $dialog.InitialDirectory = [Environment]::GetFolderPath("UserProfile")
    $dialog.Filter = "{ext.upper()} files (*.{ext})|*.{ext}|All files (*.*)|*.*"
    $dialog.DefaultExt = "{ext}"
    $result = $dialog.ShowDialog()
    if ($result -eq [System.Windows.Forms.DialogResult]::OK) {{
        Write-Output $dialog.FileName
    }}
    '''
    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            capture_output=True, text=True, timeout=120,
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
        return None
    except Exception:
        return _save_file_tkinter(default_name, title)


# ─── Tkinter fallback (last resort) ────────────────────────────────────────

def _pick_file_tkinter(title: str = "Select File") -> str | None:
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.attributes('-topmost', True)
    root.withdraw()
    root.update()
    path = filedialog.askopenfilename(title=title)
    root.destroy()
    return path if path else None


def _save_file_tkinter(default_name: str, title: str = "Save File") -> str | None:
    import tkinter as tk
    from tkinter import filedialog
    ext = os.path.splitext(default_name)[1] if '.' in default_name else ''
    root = tk.Tk()
    root.attributes('-topmost', True)
    root.withdraw()
    root.update()
    filetypes = []
    if ext:
        filetypes.append((f"{ext.upper().lstrip('.')} files", f"*{ext}"))
    filetypes.append(("All files", "*.*"))
    path = filedialog.asksaveasfilename(
        title=title,
        initialfile=default_name,
        initialdir=os.path.expanduser("~"),
        defaultextension=ext,
        filetypes=filetypes,
    )
    root.destroy()
    return path if path else None


# ─── Unified dispatcher ────────────────────────────────────────────────────

def pick_file(title: str = "Select File") -> str | None:
    if sys.platform == "darwin":
        return _pick_file_macos(title)
    elif sys.platform == "win32":
        return _pick_file_windows(title)
    else:
        return _pick_file_linux(title)


def save_file(default_name: str, title: str = "Save File") -> str | None:
    if sys.platform == "darwin":
        return _save_file_macos(default_name, title)
    elif sys.platform == "win32":
        return _save_file_windows(default_name, title)
    else:
        return _save_file_linux(default_name, title)


# ─── API Routes ─────────────────────────────────────────────────────────────


@router.get("/pick-file")
async def pick_native_file():
    """Open a native OS file picker and return the selected path."""
    try:
        file_path = pick_file(title="Select Document for Translation")
        if file_path:
            return {"file_path": file_path, "file_name": os.path.basename(file_path)}
        return {"file_path": None, "file_name": None}
    except Exception as e:
        logger.error(f"Native file picker failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to open native picker: {e}")


@router.get("/save-file")
async def save_native_file(default_name: str = "translated_document"):
    """Open a native OS save dialog and return the selected path."""
    try:
        logger.debug(f"Save dialog requested with default_name={default_name}")
        file_path = save_file(
            default_name=default_name,
            title="Save Translated File",
        )
        logger.debug(f"Save dialog result: file_path={file_path}")
        return {"file_path": file_path}
    except Exception as e:
        logger.error(f"Native save dialog failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to open save picker: {e}")


@router.post("/open-file")
async def open_native_file(request: FilePathRequest):
    """Open a file with the default OS application."""
    if not os.path.exists(request.file_path):
        raise HTTPException(status_code=404, detail="Location no longer exists.")

    try:
        if sys.platform == "win32":
            os.startfile(request.file_path)
        elif sys.platform == "darwin":
            subprocess.run(["open", request.file_path], check=True)
        else:
            subprocess.run(["xdg-open", request.file_path], check=True)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to open location: {e}")


@router.post("/open-folder")
async def open_native_folder(request: FilePathRequest):
    """Open the parent folder of a file, highlighting the file if supported."""
    if not os.path.exists(request.file_path):
        folder_path = os.path.dirname(request.file_path)
        if not os.path.exists(folder_path):
            raise HTTPException(status_code=404, detail="Folder no longer exists.")
    else:
        folder_path = os.path.dirname(request.file_path)

    try:
        if sys.platform == "win32":
            subprocess.run(["explorer", "/select,", request.file_path])
        elif sys.platform == "darwin":
            subprocess.run(["open", "-R", request.file_path], check=True)
        else:  # linux
            subprocess.run(["xdg-open", folder_path], check=True)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to open folder: {e}")
