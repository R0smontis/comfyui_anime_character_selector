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

    def test_bundles_revised_wai_v111_list(self) -> None:
        self.assertEqual(5546, len(selector._CHARACTER_MAP))
        self.assertEqual(5547, len(selector._CHINESE_OPTIONS))
        self.assertEqual(5547, len(selector._ENGLISH_OPTIONS))

    def test_representative_revised_game_mappings(self) -> None:
        expected = {
            "安朵丝（少女前线2：追放）": "andoris (girls' frontline 2)",
            "绯（少女前线2：追放）": "centaureissi (girls' frontline 2)",
            "奇塔（少女前线2：追放）": "cheeta (girls' frontline 2)",
            "寇尔芙（少女前线2：追放）": "colphne (girls' frontline 2)",
            "黛烟（少女前线2：追放）": "daiyan (girls' frontline 2)",
            "杜莎妮（少女前线2：追放）": "dushevnaya (girls' frontline 2)",
            "芙洛伦（少女前线2：追放）": "florence (girls' frontline 2)",
            "闪电（少女前线2：追放）": "groza (girls' frontline 2)",
            "海伦（少女前线2：追放）": "helen (girls' frontline 2)",
            "绛雨（少女前线2：追放）": "jiangyu (girls' frontline 2)",
            "可露凯（少女前线2：追放）": "klukai (girls' frontline 2)",
            "克罗丽科（少女前线2：追放）": "krolik (girls' frontline 2)",
            "科谢尼娅（少女前线2：追放）": "ksenia (girls' frontline 2)",
            "莱娅（少女前线2：追放）": "leva (girls' frontline 2)",
            "刘易斯（少女前线2：追放）": "lewis (girls' frontline 2)",
            "莉塔拉（少女前线2：追放）": "littara (girls' frontline 2)",
            "洛塔（少女前线2：追放）": "lotta (girls' frontline 2)",
            "玛绮朵（少女前线2：追放）": "makiatto (girls' frontline 2)",
            "米什提（少女前线2：追放）": "mechty (girls' frontline 2)",
            "莫辛纳甘（少女前线2：追放）": "mosin-nagant (girls' frontline 2)",
            "纳甘（少女前线2：追放）": "nagant (girls' frontline 2)",
            "纳美西丝（少女前线2：追放）": "nemesis (girls' frontline 2)",
            "妮基塔（少女前线2：追放）": "nikketa (girls' frontline 2)",
            "佩里缇亚（少女前线2：追放）": "peritya (girls' frontline 2)",
            "琼玖（少女前线2：追放）": "qiongjiu (girls' frontline 2)",
            "塞布丽娜（少女前线2：追放）": "sabrina (girls' frontline 2)",
            "夏克里（少女前线2：追放）": "sharkry (girls' frontline 2)",
            "春田（少女前线2：追放）": "springfield (girls' frontline 2)",
            "索米（少女前线2：追放）": "suomi (girls' frontline 2)",
            "托洛洛（少女前线2：追放）": "tololo (girls' frontline 2)",
            "乌尔丽德（少女前线2：追放）": "ullrid (girls' frontline 2)",
            "维克托（少女前线2：追放）": "vector (girls' frontline 2)",
            "维普蕾（少女前线2：追放）": "vepley (girls' frontline 2)",
            "朝晖（少女前线2：追放）": "zhaohui (girls' frontline 2)",
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
            "阿格莱雅（崩坏：星穹铁道）": "aglaea (honkai: star rail)",
            "那刻夏（崩坏：星穹铁道）": "anaxa (honkai: star rail)",
            "遐蝶（崩坏：星穹铁道）": "castorice (honkai: star rail)",
            "赛飞儿（崩坏：星穹铁道）": "cipher (honkai: star rail)",
            "昔涟（崩坏：星穹铁道）": "cyrene (honkai: star rail)",
            "长夜月（崩坏：星穹铁道）": "evernight (honkai: star rail)",
            "风堇（崩坏：星穹铁道）": "hyacine (honkai: star rail)",
            "海瑟音（崩坏：星穹铁道）": "hysilens (honkai: star rail)",
            "万敌（崩坏：星穹铁道）": "mydei (honkai: star rail)",
            "火花（崩坏：星穹铁道）": "sparxie (honkai: star rail)",
            "缇宝（崩坏：星穹铁道）": "tribbie (honkai: star rail)",
            "安卡希雅（尘白禁区）": "acacia (snowbreak)",
            "卜卜（尘白禁区）": "bubu (snowbreak)",
            "猫汐尔（尘白禁区）": "mauxir (snowbreak)",
            "晴（尘白禁区）": "naruse haru (snowbreak)",
            "妮塔（尘白禁区）": "nita (snowbreak)",
            "瑟瑞斯（尘白禁区）": "siris (snowbreak)",
            "肴（尘白禁区）": "yao (snowbreak)",
            "琴诺（尘白禁区）": "cherno kegaard",
            "伊切尔（尘白禁区）": "eatchel gustav",
            "芬妮（尘白禁区）": "fenny golden",
            "里芙（尘白禁区）": "lyfe bestla",
            "恩雅（尘白禁区）": "enya murphy",
            "芙提雅（尘白禁区）": "fritia ignis",
            "凯茜娅（尘白禁区）": "katya klein",
            "茉莉安（尘白禁区）": "marian andreotti",
            "苔丝（尘白禁区）": "tess kotkin",
            "薇蒂雅（尘白禁区）": "vidya shannon",
            "贝尼（黑礁）": "benny (black lagoon)",
            "达奇（黑礁）": "dutch (black lagoon)",
            "法比奥拉（黑礁）": "fabiola iglesias",
            "格蕾特尔（黑礁）": "gretel (black lagoon)",
            "汉塞尔（黑礁）": "hansel (black lagoon)",
            "约兰达（黑礁）": "yolanda (black lagoon)",
            "古河秋生（CLANNAD）": "furukawa akio",
            "古河早苗（CLANNAD）": "furukawa sanae",
            "伊吹风子（CLANNAD）": "ibuki fuuko",
            "宫泽有纪宁（CLANNAD）": "miyazawa yukine",
            "冈崎汐（CLANNAD）": "okazaki ushio",
            "相乐美佐枝（CLANNAD）": "sagara misae",
            "春原芽衣（CLANNAD）": "sunohara mei",
            "春原阳平（CLANNAD）": "sunohara youhei",
            "芳野祐介（CLANNAD）": "yoshino yuusuke",
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
