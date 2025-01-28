from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Prompt:
    """
    Stores string values for core, flux, and memories, and provides
    a function to build a concatenated prompt from these values.
    """

    core: str
    flux: str
    memories: str

    def build_prompt(self) -> str:
        """
        Returns a concatenated string in the format:
        f"{self.core} {self.flux} you remember {self.memories}"

        :return: str
        """
        return f"{self.core} {self.flux} you remember {self.memories}"
