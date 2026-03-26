import logging
import shutil
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
import subprocess
import socket
import os

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class OllamaService:
    """Async client wrapper for the Ollama REST API."""

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or settings.ollama_base_url
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url, 
                timeout=300.0,
                trust_env=False
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def is_connected(self) -> bool:
        """Check if Ollama server is reachable."""
        try:
            client = await self._get_client()
            response = await client.get("/api/tags", timeout=5.0)
            return response.status_code == 200
        except (httpx.ConnectError, httpx.TimeoutException, httpx.ReadError):
            return False

    def is_port_in_use(self, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', port)) == 0

    def start_server(self):
        """Attempt to start ollama serve in the background if it's not running."""
        if not self.is_port_in_use(11434):  # todo: it may not be the default port
            try:
                env = os.environ.copy()
                if settings.ollama_models_path:
                    env["OLLAMA_MODELS"] = settings.ollama_models_path
                    logger.info(f"Setting OLLAMA_MODELS to: {settings.ollama_models_path}")
                
                subprocess.Popen(
                    ["ollama", "serve"], 
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL,
                    env=env
                )
                logger.info("Started Ollama server automatically in the background.")
                return True
            except FileNotFoundError:
                logger.warning("Ollama not found in PATH. Please ensure it is installed.")
                return False
        return True

    def stop_server(self):
        """Automatically kill any running ollama serve process."""
        try:
            import psutil
        except ImportError:
            logger.warning("psutil not found, skipping ollama termination.")
            return False
        
        killed = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Check for ollama process
                if proc.info['name'] == 'ollama' or 'ollama' in (proc.info['name'] or ''):
                    cmdline = " ".join(proc.info['cmdline'] or [])
                    if "serve" in cmdline:
                        logger.info(f"Killing Ollama server (PID: {proc.info['pid']})...")
                        proc.terminate()
                        try:
                            proc.wait(timeout=3)
                        except psutil.TimeoutExpired:
                            proc.kill()
                        killed = True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return killed

    def is_installed(self) -> bool:
        """Check if Ollama binary is installed in the system."""
        return shutil.which("ollama") is not None

    async def install_ollama(self):
        """Install Ollama using the official script. Yields progress updates."""
        import os
        import subprocess

        yield {"status": "starting", "message": "Downloading installation script...", "percent": 10.0}

        try:
            # For simplicity and security, we tell the user to run the curl command
            # but here we try to automate it for Ubuntu as requested.
            # We'll use a temporary script file.
            script_url = "https://ollama.com/install.sh"
            script_path = "/tmp/ollama_install.sh"

            # Download script
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(script_url)
                response.raise_for_status()
                with open(script_path, "wb") as f:
                    f.write(response.content)
            
            os.chmod(script_path, 0o755)
            yield {"status": "downloaded", "message": "Script downloaded. Starting installation...", "percent": 30.0}

            # Run script with sudo if possible, or just run it.
            # NOTE: In a real app, you'd need the user's password for sudo.
            # Since we are in a terminal/standalone, we might already have permissions or it might fail.
            # We'll use pkexec for a GUI password prompt on Linux (Ubuntu).
            
            cmd = ["sh", script_path]
            # Try to use pkexec for GUI sudo prompt if available
            if shutil.which("pkexec"):
                cmd = ["pkexec", "sh", script_path]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            yield {"status": "installing", "message": "Installing Ollama (this may require your password)...", "percent": 50.0}
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                yield {"status": "success", "message": "Ollama installed successfully!", "percent": 100.0}
            else:
                error_msg = stderr.decode().strip() or stdout.decode().strip()
                yield {"status": "error", "message": f"Installation failed: {error_msg}", "percent": 0.0}

        except Exception as e:
            logger.error(f"Installation error: {e}")
            yield {"status": "error", "message": str(e), "percent": 0.0}
        finally:
            if os.path.exists(script_path):
                os.remove(script_path)

    async def list_models(self) -> list[dict]:
        """List all locally available models."""
        try:
            client = await self._get_client()
            response = await client.get("/api/tags")
            response.raise_for_status()
            data = response.json()
            return data.get("models", [])
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []

    @staticmethod
    def is_thinking_model(model: str) -> bool:
        """Check if a model is a 'thinking' model that supports /no_think."""
        thinking_patterns = ["qwen3", "qwq", "deepseek-r1"]
        # todo: this should not be hardcoded, but rather fetched from the model's metadata
        model_lower = model.lower()
        return any(p in model_lower for p in thinking_patterns)

    async def generate(
        self,
        model: str,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        thinking: bool | None = None,
    ) -> dict:
        """Generate text using Ollama API. Returns the full response dict.

        Args:
            thinking: If None, auto-detect based on model name and settings.
                      If False, disable thinking for thinking-capable models.
        """
        client = await self._get_client()

        # Auto-detect thinking preference
        if thinking is None:
            thinking = settings.thinking_enabled

        # Build options
        options: dict = {
            "num_predict": settings.max_generation_tokens,
        }

        if self.is_thinking_model(model) and not thinking:
            # Non-thinking mode for Qwen 3.5 etc.
            options.update({
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 20,
                "presence_penalty": 1.5,
            })
        else:
            options["temperature"] = temperature

        payload: dict = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": options,
        }
        if system:
            payload["system"] = system

        response = await client.post("/api/generate", json=payload)
        
        if response.status_code == 404:
            from fastapi import HTTPException
            err_msg = response.json().get("error", response.text)
            if "not found" in err_msg.lower() or "try pulling it first" in err_msg.lower():
                raise HTTPException(status_code=404, detail="model_not_found")

        response.raise_for_status()
        return response.json()

    async def generate_stream(
        self,
        model: str,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        thinking: bool | str | None  = None,
    ):
        """Stream generation tokens from Ollama. Yields parsed JSON chunks.

        Each chunk contains: {"response": "token", "done": false/true, ...}
        For thinking models, tokens inside <think> blocks are tagged.
        """
        import json as json_module

        client = await self._get_client()

        if thinking is None:
            logger.debug(f"Thinking is None, using default: {settings.thinking_enabled}.")
            thinking = settings.thinking_enabled

        options: dict = {
            "num_predict": settings.max_generation_tokens,
        }

        if self.is_thinking_model(model) and not thinking:
            options.update({
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 20,
                "presence_penalty": 1.5,
            })

            logger.debug(f"Using thinking model \"{model}\", thinking disabled.")
        else:
            options["temperature"] = temperature

        payload: dict = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "options": options,
        }
        if system:
            payload["system"] = system
        if thinking is False:
            payload["think"] = False

        logger.debug(f"Payload: {payload}") # fixme

        async with client.stream("POST", "/api/generate", json=payload) as response:
            if response.status_code == 404:
                await response.aread()
                try:
                    err_msg = response.json().get("error", response.text)
                except Exception:
                    err_msg = response.text
                if "not found" in err_msg.lower() or "try pulling it first" in err_msg.lower():
                    yield {"error_type": "model_not_found", "message": err_msg, "model": model}
                else:
                    yield {"error_type": "http_error", "message": f"HTTP 404: {err_msg}"}
                return
            elif response.status_code != 200:
                await response.aread()
                yield {"error_type": "http_error", "message": f"HTTP {response.status_code}: {response.text}"}
                return

            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.strip():
                    yield json_module.loads(line)

    async def pull_model(self, name: str):
        """Pull a model from Ollama registry. Yields progress updates."""
        client = await self._get_client()
        async with client.stream(
            "POST", "/api/pull", json={"name": name, "stream": True}
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.strip():
                    import json

                    yield json.loads(line)

    async def delete_model(self, name: str) -> bool:
        """Delete a local model."""
        try:
            client = await self._get_client()
            response = await client.delete("/api/delete", json={"name": name})
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to delete model {name}: {e}")
            return False

    async def get_model_info(self, name: str) -> dict | None:
        """Get detailed info about a specific model."""
        try:
            client = await self._get_client()
            response = await client.post("/api/show", json={"name": name})
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

    def get_system_specs(self) -> dict:
        """Get system hardware specs for model recommendation."""
        import os

        gpu_vram_mb = 0
        ram_mb = 0

        # Get RAM
        try:
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        ram_mb = int(line.split()[1]) // 1024
                        break
        except Exception:
            pass

        # Get GPU VRAM via nvidia-smi
        try:
            import subprocess

            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                gpu_vram_mb = int(result.stdout.strip().split("\n")[0])
        except Exception:
            pass

        return {
            "ram_mb": ram_mb,
            "gpu_vram_mb": gpu_vram_mb,
            "cpu_count": os.cpu_count() or 1,
        }

    def recommend_model(self) -> dict:
        """Recommend best model based on system specs."""
        specs = self.get_system_specs()
        vram = specs["gpu_vram_mb"]
        ram = specs["ram_mb"]

        if vram >= 12000 or ram >= 32000:
            return {
                "recommended_model": "qwen3.5:9b",
                "reason": f"Your system has {vram}MB VRAM and {ram}MB RAM. "
                "The 9B model provides superior translation quality.",
                "gpu_vram_mb": vram,
                "ram_mb": ram,
                "alternatives": ["qwen3.5:4b", "qwen3.5:2b", "qwen2.5:7b"],
            }
        elif vram >= 4000 or ram >= 8000:
            return {
                "recommended_model": "qwen3.5:4b",
                "reason": f"Your system has {vram}MB VRAM and {ram}MB RAM. "
                "The 4B model offers a perfect balance of quality and speed.",
                "gpu_vram_mb": vram,
                "ram_mb": ram,
                "alternatives": ["qwen3.5:2b", "qwen2.5:3b"],
            }
        else:
            return {
                "recommended_model": "qwen3.5:2b",
                "reason": f"Your system has {vram}MB VRAM and {ram}MB RAM. "
                "The 2B model is extremely fast and lightweight.",
                "gpu_vram_mb": vram,
                "ram_mb": ram,
                "alternatives": [],
            }


# Singleton instance
ollama_service = OllamaService()
