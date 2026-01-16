from dataclasses import dataclass


@dataclass(frozen=True)
class VaultRegistry:
    safety_vault: str
    growth_vault: str
