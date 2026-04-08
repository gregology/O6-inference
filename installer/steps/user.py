"""Create the llm system user and directory layout."""

from pathlib import Path

from ..step import Step

LLM_HOME = Path("/srv/llm")
DIRS = ["src", "models", "etc", "cache/huggingface", "logs"]


class UserStep(Step):
    name = "user"
    description = "Create llm user and directory layout"

    def check(self) -> bool:
        return self.sh_ok("id llm") and all(
            (LLM_HOME / d).is_dir() for d in DIRS
        )

    def run(self) -> None:
        self.sh(
            "useradd --system --home /srv/llm --create-home "
            "--shell /usr/sbin/nologin llm || true"
        )
        for d in DIRS:
            (LLM_HOME / d).mkdir(parents=True, exist_ok=True)
        self.sh("chown -R llm:llm /srv/llm")
