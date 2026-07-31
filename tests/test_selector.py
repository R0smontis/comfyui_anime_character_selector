from __future__ import annotations

import sys
import unittest
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR.parent))

from comfyui_anime_character_selector import NODE_CLASS_MAPPINGS  # noqa: E402
from comfyui_anime_character_selector import anime_character_selector as selector  # noqa: E402


class AnimeCharacterSelectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.node = NODE_CLASS_MAPPINGS["AnimeCharacterSelectorCN"]()

    def test_bundles_revised_wai_v16_list(self) -> None:
        self.assertEqual(5470, len(selector._CHARACTER_MAP))
        self.assertEqual(5471, len(selector._CHINESE_OPTIONS))
        self.assertEqual(5471, len(selector._ENGLISH_OPTIONS))

    def test_representative_revised_game_mappings(self) -> None:
        expected = {
            "塞西尔·柯尔米（反叛的鲁路修）": "cecile croomy",
            "吉诺·温伯格（反叛的鲁路修）": "gino weinberg",
            "春川风希（莉可丽丝）": "harukawa fuki",
            "杰里米亚·哥特瓦尔德（反叛的鲁路修）": "jeremiah gottwald",
            "金格·布拉德雷（钢之炼金术士）": "king bradley",
            "兰芳（钢之炼金术士）": "lan fan",
            "姚麟（钢之炼金术士）": "ling yao",
            "真岛（莉可丽丝）": "majima (lycoris recoil)",
            "张梅（钢之炼金术士）": "may chang",
            "米卡（莉可丽丝）": "mika (lycoris recoil)",
            "中原瑞希（莉可丽丝）": "nakahara mizuki",
            "妮娜·爱因斯坦（反叛的鲁路修）": "nina einstein",
            "罗洛·兰佩洛基（反叛的鲁路修）": "rolo lamperouge",
            "黍（明日方舟）": "shu (arknights)",
            "阿（明日方舟）": "aak (arknights)",
            "堇（蔚蓝档案）": "sumire (blue archive)",
            "长发公主（胜利女神：NIKKE）": "rapunzel (nikke)",
            "诺伊斯（胜利女神：NIKKE）": "noise (nikke)",
            "佩丽卡（明日方舟终末地）": "perlica (arknights endfield)",
            "爱弥斯（鸣潮）": "aemeath (wuthering waves)",
            "达妮娅（鸣潮）": "denia (wuthering waves)",
            "铃（绝区零）": "belle (zenless zone zero)",
            "安克（胜利女神：NIKKE）": "anchor (nikke)",
            "桑多涅（原神）": "sandrone (genshin impact)",
            "茜特菈莉（原神）": "citlali (genshin impact)",
            "梦见月瑞希（原神）": "yumemizuki mizuki",
            "赤木律子（新世纪福音战士）": "akagi ritsuko",
            "菲·瓦伦丁（星际牛仔）": "faye valentine",
            "桥田至（命运石之门）": "hashida itaru",
            "真锅和（轻音少女）": "manabe nodoka",
        }
        for chinese_name, tag in expected.items():
            with self.subTest(chinese_name=chinese_name):
                prompt, info = self.node.select_character(
                    chinese_name, 0, 1.0, False, "masterpiece"
                )
                self.assertIn(tag, prompt.replace("\\", ""))
                self.assertIn(chinese_name, info)

    def test_random_selection_is_seed_deterministic(self) -> None:
        first = self.node.select_character("random", 77, 1.0, False, "")
        second = self.node.select_character("random", 77, 1.0, False, "")
        self.assertEqual(first, second)
        self.assertNotIn("Character: random", first[1])

    def test_weight_and_prompt_order(self) -> None:
        prompt, _ = self.node.select_character(
            "黍（明日方舟）", 0, 1.25, True, "solo"
        )
        self.assertTrue(prompt.startswith("solo, "))
        self.assertIn(":1.25)", prompt)


if __name__ == "__main__":
    unittest.main()
