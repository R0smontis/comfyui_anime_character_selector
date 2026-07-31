"""Standalone WAI Illustrious character selectors.

Derived from mirabarukaso/ComfyUI_Mira's WAI character selector under the MIT
License. The bundled list keeps the upstream WAI Illustrious v1.6 roster and
applies verified additions and Chinese-name corrections for Arknights,
Arknights: Endfield, Wuthering Waves, and Zenless Zone Zero. Version 1.1.0
also imports canonical Arknights operator tags from the public AnimaDex
catalogue when matched to the bilingual operator roster. Version 1.2.0 adds
31 mainland-China Blue Archive base-character tags with exact model-tag
evidence. Version 1.3.0 adds 11 NIKKE base-character tags verified against
Chinese character pages and exact model-tag evidence. Version 1.4.0 adds
8 Genshin Impact base-character tags and one NIKKE base-character tag,
verified against BWiki roster pages and exact positive-count model tags.
Version 1.5.0 adds 14 classic-anime character tags across Evangelion,
Cowboy Bebop, Steins;Gate, and K-ON, verified against Chinese reference
pages and exact positive-count model tags.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

_CATEGORY = "二次元角色选择器"
_RANDOM = "random"
_DATA_FILE = Path(__file__).with_name("data") / "wai_characters.csv"


def _load_characters() -> tuple[dict[str, str], tuple[str, ...], tuple[str, ...]]:
    character_map: dict[str, str] = {}
    english_tags: set[str] = set()

    with _DATA_FILE.open("r", encoding="utf-8-sig", newline="") as handle:
        for line_number, row in enumerate(csv.reader(handle), start=1):
            if len(row) != 2:
                raise ValueError(f"Invalid character row {line_number}: expected 2 columns")

            chinese_name, english_tag = (value.strip() for value in row)
            if not chinese_name or not english_tag:
                raise ValueError(f"Invalid character row {line_number}: empty name or tag")
            if chinese_name in character_map:
                raise ValueError(f"Duplicate Chinese character name: {chinese_name}")
            if english_tag in english_tags:
                raise ValueError(f"Duplicate English character tag: {english_tag}")

            character_map[chinese_name] = english_tag
            english_tags.add(english_tag)

    chinese_options = (_RANDOM, *character_map.keys())
    english_options = (_RANDOM, *character_map.values())
    return character_map, chinese_options, english_options


_CHARACTER_MAP, _CHINESE_OPTIONS, _ENGLISH_OPTIONS = _load_characters()


def _select(options: tuple[str, ...], selected: str, seed: int) -> str:
    if selected != _RANDOM:
        return selected
    characters = options[1:]
    return characters[seed % len(characters)]


def _format_prompt(
    tag: str,
    display_name: str,
    character_weight: float,
    insert_before_character: bool,
    custom_prompt: str,
) -> tuple[str, str]:
    escaped_tag = tag.replace("(", r"\(").replace(")", r"\)")
    weighted_tag = escaped_tag
    if not math.isclose(character_weight, 1.0):
        weighted_tag = f"({escaped_tag}:{character_weight:.2f})"
    if not weighted_tag.endswith(","):
        weighted_tag += ","

    custom_prompt = custom_prompt.strip()
    if custom_prompt and not custom_prompt.endswith(","):
        custom_prompt += ","

    prompt_parts = (custom_prompt, weighted_tag) if insert_before_character else (weighted_tag, custom_prompt)
    prompt = " ".join(part for part in prompt_parts if part)
    info = f"Character: {display_name} [{weighted_tag}]\nCustom Prompt: {custom_prompt}"
    return prompt, info


def _input_types(options: tuple[str, ...]) -> dict:
    return {
        "required": {
            "character": (options,),
            "random_action_seed": (
                "INT",
                {
                    "default": 1024,
                    "min": 0,
                    "max": 0xFFFFFFFFFFFFFFFF,
                    "display": "input",
                },
            ),
            "character_weight": (
                "FLOAT",
                {"default": 1.0, "min": 0.1, "max": 2.0, "step": 0.05},
            ),
            "insert_before_character": ("BOOLEAN", {"default": False}),
        },
        "optional": {
            "custom_prompt": (
                "STRING",
                {"display": "input", "multiline": True},
            ),
        },
    }


class AnimeCharacterSelectorCN:
    """Select a WAI character by its Simplified Chinese display name."""

    @classmethod
    def INPUT_TYPES(cls) -> dict:
        return _input_types(_CHINESE_OPTIONS)

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "info")
    FUNCTION = "select_character"
    CATEGORY = _CATEGORY

    def select_character(
        self,
        character: str,
        random_action_seed: int,
        character_weight: float,
        insert_before_character: bool,
        custom_prompt: str = "",
    ) -> tuple[str, str]:
        selected_name = _select(_CHINESE_OPTIONS, character, random_action_seed)
        return _format_prompt(
            _CHARACTER_MAP[selected_name],
            selected_name,
            character_weight,
            insert_before_character,
            custom_prompt,
        )


class AnimeCharacterSelectorEN:
    """Select a WAI character directly by its English model tag."""

    @classmethod
    def INPUT_TYPES(cls) -> dict:
        return _input_types(_ENGLISH_OPTIONS)

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "info")
    FUNCTION = "select_character"
    CATEGORY = _CATEGORY

    def select_character(
        self,
        character: str,
        random_action_seed: int,
        character_weight: float,
        insert_before_character: bool,
        custom_prompt: str = "",
    ) -> tuple[str, str]:
        selected_tag = _select(_ENGLISH_OPTIONS, character, random_action_seed)
        return _format_prompt(
            selected_tag,
            selected_tag,
            character_weight,
            insert_before_character,
            custom_prompt,
        )
