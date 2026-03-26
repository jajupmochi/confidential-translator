import sys
import subprocess
from pathlib import Path
from typing import List

def run_cmd(cmd: List[str], cwd: Path):
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)

def main():
    root_dir = Path(__file__).parent.parent
    frontend_dir = root_dir / 'frontend'
    backend_dir = root_dir / 'backend'
    
    # 1. Build frontend
    print("=== Building Frontend ===")
    run_cmd(["npm", "run", "build"], cwd=frontend_dir)
    
    # 2. Copy frontend build to backend static dir
    static_dir = backend_dir / 'app' / 'static'
    if static_dir.exists():
        import shutil
        shutil.rmtree(static_dir)
    
    import shutil
    shutil.copytree(frontend_dir / "dist", static_dir)
    
    # 3. Build executable
    print("=== Building Backend Executable ===")
    sep = ";" if sys.platform == "win32" else ":"
    run_cmd([
        "uv", "run", "pyinstaller",
        "--name=confidential-translator",
        "--onefile",
        f"--add-data=app/static{sep}app/static",
        "--hidden-import", "aiosqlite",
        "--hidden-import", "sqlalchemy.dialects.sqlite.aiosqlite",
        "--hidden-import", "psutil",
        "app/main.py"
    ], cwd=backend_dir)
    
    print("\n✅ Build complete! Executable is in backend/dist/")

if __name__ == "__main__":
    main()
