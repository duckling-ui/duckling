"""Server-level configuration loader for Duckling."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict


DEFAULT_SERVER_CONFIG: Dict[str, Any] = {
    "api_key": "",
    "cors_origins": ["http://localhost:3000", "http://localhost:5173"],
    "engine": {
        "kind": "local",
        "rq_redis_url": "redis://redis:6379/0",
        "rq_queue_name": "convert",
        "rq_results_ttl": 14400,
    },
    "ray": {
        "address": "",
    },
    "logging": {
        "level": "INFO",
        "format": "text",
    },
    "connectors": {
        "allowed_source_types": [],
        "allowed_target_types": [],
        "allow_external_plugins": False,
    },
    "enable_remote_services": False,
    "allow_custom_vlm_config": False,
}


def _deep_merge(base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _load_config_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    suffix = path.suffix.lower()
    if suffix not in {".json", ".yaml", ".yml"}:
        raise ValueError(f"Unsupported config file type: {suffix}")
    text = path.read_text(encoding="utf-8")
    if suffix == ".json":
        return json.loads(text)
    # Keep YAML optional to avoid hard dependency.
    try:
        import yaml  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("YAML config requires PyYAML") from exc
    return yaml.safe_load(text) or {}


def get_server_config(project_root: Path) -> Dict[str, Any]:
    cfg = dict(DEFAULT_SERVER_CONFIG)
    cfg_file = os.getenv("DUCKLING_CONFIG_FILE", "").strip()
    if cfg_file:
        cfg = _deep_merge(cfg, _load_config_file(Path(cfg_file)))

    env_cfg = {
        "api_key": os.getenv("DUCKLING_API_KEY", cfg.get("api_key", "")),
        "engine": {
            "kind": os.getenv("DUCKLING_ENGINE_KIND", cfg["engine"]["kind"]),
            "rq_redis_url": os.getenv("DUCKLING_RQ_REDIS_URL", cfg["engine"]["rq_redis_url"]),
            "rq_queue_name": os.getenv("DUCKLING_RQ_QUEUE_NAME", cfg["engine"]["rq_queue_name"]),
            "rq_results_ttl": int(os.getenv("DUCKLING_RQ_RESULTS_TTL", str(cfg["engine"]["rq_results_ttl"]))),
        },
        "ray": {
            "address": os.getenv("DUCKLING_RAY_ADDRESS", cfg["ray"]["address"]),
        },
        "logging": {
            "level": os.getenv("DUCKLING_LOG_LEVEL", cfg["logging"]["level"]),
            "format": os.getenv("DUCKLING_LOG_FORMAT", cfg["logging"]["format"]),
        },
        "enable_remote_services": os.getenv("DUCKLING_ENABLE_REMOTE_SERVICES", str(cfg["enable_remote_services"])).lower() == "true",
        "allow_custom_vlm_config": os.getenv("DUCKLING_ALLOW_CUSTOM_VLM_CONFIG", str(cfg["allow_custom_vlm_config"])).lower() == "true",
    }
    cfg = _deep_merge(cfg, env_cfg)
    cfg["project_root"] = str(project_root)
    return cfg

