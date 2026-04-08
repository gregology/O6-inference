"""Install system packages."""

from ..step import Step

PACKAGES = [
    # Build tools
    "git", "cmake", "ninja-build", "build-essential", "pkg-config",
    # Python
    "python3", "python3-pip", "python3-venv",
    # Utilities
    "curl", "ca-certificates", "jq", "xz-utils",
    # Math / threading
    "libopenblas-dev", "libomp-dev",
    # Vulkan
    "libvulkan1", "libvulkan-dev", "vulkan-tools",
    "mesa-vulkan-drivers", "glslc",
    # Build dep (not linked, but needed for cmake find)
    "libcurl4-openssl-dev",
]


class PackagesStep(Step):
    name = "packages"
    description = "Install system packages"

    def check(self) -> bool:
        # Check a representative subset — if these are present, apt ran.
        probes = ["cmake", "ninja-build", "libvulkan-dev", "glslc"]
        for pkg in probes:
            if not self.sh_ok(f"dpkg -s {pkg} 2>/dev/null"):
                return False
        return True

    def run(self) -> None:
        self.sh("apt-get update")
        self.sh(f"apt-get install -y {' '.join(PACKAGES)}")
