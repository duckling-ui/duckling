"""
System information utilities for hardware detection and CPU monitoring.
"""

import os
import platform
from typing import Optional

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


def get_cpu_count() -> int:
    """Return number of logical CPUs."""
    if not PSUTIL_AVAILABLE:
        return 0
    try:
        return psutil.cpu_count(logical=True) or 0
    except Exception:
        return 0


def get_cpu_usage(process_specific: bool = True) -> Optional[float]:
    """
    Return current CPU usage as percentage (0-100).
    If process_specific=True, returns Duckling backend process CPU (runs Docling); else system-wide.
    """
    if not PSUTIL_AVAILABLE:
        return None
    try:
        if process_specific:
            proc = psutil.Process(os.getpid())
            return proc.cpu_percent(interval=0.5)
        return psutil.cpu_percent(interval=0.5)
    except Exception:
        return None


def get_hardware_type() -> dict:
    """
    Detect hardware type: CPU, GPU (CUDA), or Apple Silicon (MPS).

    Returns dict with:
      - type: "cpu" | "cuda" | "mps" | "unknown"
      - cpu_count: int
      - gpu_name: str | None
      - gpu_memory_mb: float | None
      - platform: str
    """
    result = {
        "type": "unknown",
        "cpu_count": get_cpu_count(),
        "gpu_name": None,
        "gpu_memory_mb": None,
        "platform": platform.system().lower(),
    }

    # Check for CUDA
    try:
        import torch
        if torch.cuda.is_available():
            result["type"] = "cuda"
            result["gpu_name"] = torch.cuda.get_device_name(0) if torch.cuda.device_count() > 0 else None
            if result["gpu_name"] and torch.cuda.device_count() > 0:
                mem_bytes = torch.cuda.get_device_properties(0).total_memory
                result["gpu_memory_mb"] = round(mem_bytes / (1024 * 1024), 1)
            return result
    except ImportError:
        pass

    # Check for Apple MPS (Metal Performance Shaders)
    try:
        import torch
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            result["type"] = "mps"
            result["gpu_name"] = "Apple Silicon (MPS)"
            return result
    except ImportError:
        pass

    # Fallback: check platform for Apple Silicon
    if platform.system() == "Darwin" and platform.machine() == "arm64":
        result["type"] = "mps"
        result["gpu_name"] = "Apple Silicon"
        return result

    result["type"] = "cpu"
    return result


def sample_cpu_during_conversion(stop_event, process_specific: bool = True) -> list:
    """
    Sample CPU usage in a loop until stop_event is set.
    Uses interval=0.5s so stop_event is checked every half second.
    If process_specific=True, measures Duckling backend process CPU (runs Docling); else system-wide.
    Returns list of CPU percentage values.
    """
    if not PSUTIL_AVAILABLE:
        return []
    samples = []
    try:
        proc = psutil.Process(os.getpid()) if process_specific else None
        while not stop_event.is_set():
            try:
                if proc:
                    val = proc.cpu_percent(interval=0.5)
                else:
                    val = psutil.cpu_percent(interval=0.5)
                samples.append(val)
            except Exception:
                break
    except Exception:
        pass
    return samples
