"""ComfyUI 二次元角色选择器。"""

from .anime_character_selector import AnimeCharacterSelectorCN, AnimeCharacterSelectorEN

NODE_CLASS_MAPPINGS = {
    "AnimeCharacterSelectorCN": AnimeCharacterSelectorCN,
    "AnimeCharacterSelectorEN": AnimeCharacterSelectorEN,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AnimeCharacterSelectorCN": "二次元角色选择器（中文）",
    "AnimeCharacterSelectorEN": "二次元角色选择器（英文标签）",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
