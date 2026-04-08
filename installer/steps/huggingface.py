"""Set up the Hugging Face CLI in a venv."""

from pathlib import Path

from ..step import Step

VENV = Path("/srv/llm/venv")
HF_BIN = VENV / "bin" / "hf"


class HuggingFaceStep(Step):
    name = "huggingface"
    description = "Set up Hugging Face CLI"

    def check(self) -> bool:
        # Always run — pip install --upgrade is a no-op if already current.
        return False

    def run(self) -> None:
        if not VENV.exists():
            self.sh(f"sudo -u llm python3 -m venv {VENV}")
        self.sh(f"sudo -u llm {VENV}/bin/pip install --upgrade pip 'huggingface_hub[cli]'")
