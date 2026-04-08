"""Install newer Vulkan-Headers (Bookworm's are too old for ggml-vulkan)."""

from pathlib import Path

from ..step import Step

VULKAN_HEADER_TAG = "v1.4.339"
HEADER_PATH = Path("/usr/local/include/vulkan/vulkan_core.h")


class VulkanHeadersStep(Step):
    name = "vulkan-headers"
    description = "Install Vulkan-Headers " + VULKAN_HEADER_TAG

    def check(self) -> bool:
        if not HEADER_PATH.exists():
            return False
        # Check the installed version matches what we expect.
        content = HEADER_PATH.read_text()
        # v1.4.339 → VK_HEADER_VERSION 339
        version_num = VULKAN_HEADER_TAG.rsplit(".", 1)[-1]
        return f"VK_HEADER_VERSION {version_num}" in content

    def run(self) -> None:
        self.sh("rm -rf /tmp/Vulkan-Headers")
        self.sh(
            f"git clone --depth 1 --branch {VULKAN_HEADER_TAG} "
            "https://github.com/KhronosGroup/Vulkan-Headers.git /tmp/Vulkan-Headers"
        )
        self.sh(
            "cmake -S /tmp/Vulkan-Headers -B /tmp/Vulkan-Headers/build "
            "-G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local"
        )
        self.sh("cmake --build /tmp/Vulkan-Headers/build")
        self.sh("cmake --install /tmp/Vulkan-Headers/build")
        self.sh("rm -rf /tmp/Vulkan-Headers")
