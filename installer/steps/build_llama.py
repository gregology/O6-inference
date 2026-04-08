"""Build llama.cpp with Vulkan support."""

from pathlib import Path

from ..step import Step

LLAMA_DIR = Path("/srv/llm/src/llama.cpp")
BUILD_DIR = LLAMA_DIR / "build-vulkan"
SERVER_BIN = BUILD_DIR / "bin" / "llama-server"


class BuildLlamaStep(Step):
    name = "build-llama"
    description = "Build llama.cpp (Vulkan, curl disabled)"

    def check(self) -> bool:
        if not SERVER_BIN.exists():
            return False
        # If there are upstream updates, rebuild is needed.
        if LLAMA_DIR.exists():
            self.sh_ok(f"sudo -u llm git -C {LLAMA_DIR} fetch --quiet")
            local = self.sh_output(f"git -C {LLAMA_DIR} rev-parse HEAD")
            remote = self.sh_output(f"git -C {LLAMA_DIR} rev-parse @{{u}}")
            if local and remote and local != remote:
                return False
        return True

    def run(self) -> None:
        if not LLAMA_DIR.exists():
            self.sh_live(
                "sudo -u llm git clone https://github.com/ggml-org/llama.cpp "
                f"{LLAMA_DIR}"
            )
        else:
            self.sh_live(f"sudo -u llm git -C {LLAMA_DIR} pull")

        # Clean previous build
        if BUILD_DIR.exists():
            self.sh(f"rm -rf {BUILD_DIR}")

        nproc = self.sh_output("nproc") or "4"
        self.sh_live(
            f"sudo -u llm bash -lc '"
            f"cmake -S {LLAMA_DIR} -B {BUILD_DIR} -G Ninja "
            f"-DCMAKE_BUILD_TYPE=Release "
            f"-DLLAMA_CURL=OFF "
            f"-DGGML_VULKAN=ON "
            f"&& cmake --build {BUILD_DIR} -j {nproc}'"
        )

        # Restart the service if it's running so it picks up the new binary.
        if self.sh_ok("systemctl is-active --quiet llama-router.service"):
            self.sh("systemctl restart llama-router.service")
            print("   Restarted llama-router.service")
