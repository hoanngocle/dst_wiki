from dataclasses import dataclass
from typing import Dict


SCHEMA_VERSION = 1
SUPPORTED_NAMESPACES: Dict[int, str] = {
    0: "Main",
    6: "File",
    14: "Category",
}


@dataclass(frozen=True)
class CrawlSummary:
    pages: int
    images: int
    links: int
    failures: int
    pending_pages: int = 0
    pending_images: int = 0

    @property
    def exit_code(self) -> int:
        return 1 if self.failures else 0
