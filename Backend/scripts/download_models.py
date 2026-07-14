"""Download Qwen and embedding models into Backend/artifacts/models/."""

from __future__ import annotations

import argparse
from pathlib import Path

from huggingface_hub import snapshot_download

BACKEND_ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = BACKEND_ROOT / "artifacts" / "models"

MODELS = {
    "qwen2.5-1.5b-instruct": "Qwen/Qwen2.5-1.5B-Instruct",
    "bge-base-en-v1.5": "BAAI/bge-base-en-v1.5",
}


def download_model(local_name: str, repo_id: str, models_dir: Path) -> Path:
    target = models_dir / local_name
    if target.exists() and (target / "config.json").exists():
        print(f"[skip] {local_name} already present at {target}")
        return target

    print(f"[download] {repo_id} -> {target}")
    snapshot_download(
        repo_id=repo_id,
        local_dir=str(target),
        local_dir_use_symlinks=False,
    )
    print(f"[done] {local_name}")
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Download local Qwen + embedding models")
    parser.add_argument(
        "--models-dir",
        type=Path,
        default=MODELS_DIR,
        help="Directory to store downloaded models",
    )
    args = parser.parse_args()
    args.models_dir.mkdir(parents=True, exist_ok=True)

    for local_name, repo_id in MODELS.items():
        download_model(local_name, repo_id, args.models_dir)

    print(f"All models ready under {args.models_dir}")


if __name__ == "__main__":
    main()
