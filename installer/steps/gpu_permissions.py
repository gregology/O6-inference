"""Ensure the llm user can access GPU render nodes."""

from ..step import Step


class GpuPermissionsStep(Step):
    name = "gpu-permissions"
    description = "Grant llm user access to GPU render nodes"

    def check(self) -> bool:
        if not self.hw.render_nodes:
            return True  # No render nodes — nothing to do.
        groups = self.sh_output("id -nG llm")
        return self.hw.render_group in groups.split()

    def run(self) -> None:
        if not self.hw.render_nodes:
            print("   (no render nodes found, skipping)")
            return
        group = self.hw.render_group
        self.sh(f"usermod -aG {group} llm")
        print(f"   Added llm to group '{group}'")
        print("   NOTE: a reboot is required for group membership to take effect")
