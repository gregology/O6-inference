"""Download models from Hugging Face, optionally prune removed ones."""

from pathlib import Path
import shutil

from ..step import Step

HF_BIN = "/srv/llm/venv/bin/hf"
HF_HOME = "/srv/llm/cache/huggingface"
MODELS_DIR = Path("/srv/llm/models")


class ModelsStep(Step):
    name = "models"
    description = "Download models from Hugging Face"

    def check(self) -> bool:
        # Always run — we need to diff desired vs installed.
        return False

    def run(self) -> None:
        desired_dirs = {m.dir or m.id for m in self.config.models}
        installed_dirs = {
            p.name for p in MODELS_DIR.iterdir() if p.is_dir()
        } if MODELS_DIR.exists() else set()

        to_download = []
        for model in self.config.models:
            model_dir = Path(model.local_dir)
            if not model_dir.exists() or not any(model_dir.rglob("*.gguf")):
                to_download.append(model)

        to_remove = installed_dirs - desired_dirs

        if not to_download and not to_remove:
            print("   All models up to date")
            return

        # Download new/missing models
        for model in to_download:
            print(f"   Downloading {model.id} from {model.repo} ...")
            model_dir = Path(model.local_dir)
            model_dir.mkdir(parents=True, exist_ok=True)

            if model.file:
                cmd = (
                    f"sudo -u llm env HF_HOME={HF_HOME} {HF_BIN} download "
                    f"{model.repo} {model.file} "
                    f"--local-dir {model.local_dir}"
                )
            elif model.include:
                cmd = (
                    f"sudo -u llm env HF_HOME={HF_HOME} {HF_BIN} download "
                    f"{model.repo} "
                    f"--include '{model.include}' "
                    f"--local-dir {model.local_dir}"
                )
            else:
                raise ValueError(f"Model {model.id}: must specify 'file' or 'include'")

            self.sh_live(cmd)

        # Prune removed models
        if to_remove:
            if self.config.prune:
                for model_id in sorted(to_remove):
                    path = MODELS_DIR / model_id
                    print(f"   Pruning {model_id} ({path}) ...")
                    shutil.rmtree(path)
            else:
                print(f"   Orphaned models (pass --prune to remove): {', '.join(sorted(to_remove))}")
