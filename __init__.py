"""ComfyUI 二次元角色选择器。"""

# 注册 web 目录（拼音首字母搜索扩展所在），由 ComfyUI 自动挂载并加载
WEB_DIRECTORY = "web"

from .anime_character_selector import AnimeCharacterSelectorCN, AnimeCharacterSelectorEN

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
