"""Install and enable the llama-router systemd service."""

from pathlib import Path

from ..step import Step

SERVICE_PATH = Path("/etc/systemd/system/llama-router.service")
SERVER_BIN = "/srv/llm/src/llama.cpp/build-vulkan/bin/llama-server"
MODELS_INI = "/srv/llm/etc/models.ini"


def render_unit(host: str, port: int) -> str:
    return f"""\
[Unit]
Description=llama.cpp router (multi-model, Vulkan)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=llm
Group=llm
WorkingDirectory=/srv/llm
Environment=HOME=/srv/llm
Environment=HF_HOME=/srv/llm/cache/huggingface

ExecStart={SERVER_BIN} \\
  --host {host} --port {port} \\
  --models-preset {MODELS_INI} \\
  --models-max 1 \\
  --parallel 1 \\
  --timeout 1800

Restart=on-failure
RestartSec=2
LimitNOFILE=1048576

StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""


class SystemdStep(Step):
    name = "systemd"
    description = "Install and enable llama-router service"

    def check(self) -> bool:
        if not SERVICE_PATH.exists():
            return False
        # Check if the unit content matches what we'd generate.
        expected = render_unit(self.config.host, self.config.port)
        return SERVICE_PATH.read_text() == expected

    def run(self) -> None:
        content = render_unit(self.config.host, self.config.port)
        SERVICE_PATH.write_text(content)
        self.sh("systemctl daemon-reload")
        self.sh("systemctl enable --now llama-router.service")
        print("   Service enabled and started")
        print("   Logs: journalctl -u llama-router.service -f")
