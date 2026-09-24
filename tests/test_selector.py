from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR.parent))

from comfyui_anime_character_selector import NODE_CLASS_MAPPINGS  # noqa: E402
from comfyui_anime_character_selector import anime_character_selector as selector  # noqa: E402

_CJK_RE = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")


def _load_pinyin_index() -> dict[str, dict[str, str]]:
    data_file = PACKAGE_DIR / "web" / "pinyin_data.js"
    raw = data_file.read_text(encoding="utf-8")
    return json.loads(raw[raw.index("{") : raw.rindex("}") + 1])


def _pinyin_entry(name: str, index: dict[str, dict[str, str]]) -> tuple[str, str]:
    entry = index.get(name, {})
    return entry.get("i", ""), entry.get("p", "")


class AnimeCharacterSelectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.node = NODE_CLASS_MAPPINGS["AnimeCharacterSelectorCN"]()

    def test_bundles_revised_wai_v146_list(self) -> None:
        self.assertEqual(5755, len(selector._CHARACTER_MAP))
        self.assertEqual(5756, len(selector._CHINESE_OPTIONS))
        self.assertEqual(5756, len(selector._ENGLISH_OPTIONS))

    def test_pinyin_data_covers_all_cjk_display_names(self) -> None:
        index = _load_pinyin_index()
        cjk_names = [n for n in selector._CHINESE_OPTIONS if _CJK_RE.search(n)]
        missing = [n for n in cjk_names if n not in index]
        self.assertEqual(missing, [], "every CJK display name needs a pinyin entry")
        self.assertGreater(len(index), 5000)
        # Spot-check initials: 凯露 -> kl..., 胡桃 -> ht..., 空崎阳奈 -> kqyn...
        self.assertTrue(index["凯露（公主连结！Re:Dive）"]["i"].startswith("kl"))
        self.assertTrue(index["胡桃（原神）"]["i"].startswith("ht"))
        self.assertTrue(index["空崎阳奈（蔚蓝档案）"]["i"].startswith("kqyn"))
        # Spot-check full pinyin: 胡桃 -> hutaoyuanshen, 凯露 -> kailu..., 空崎阳奈 -> kongqi...
        self.assertTrue(index["胡桃（原神）"]["p"].startswith("hutao"))
        self.assertTrue(index["凯露（公主连结！Re:Dive）"]["p"].startswith("kailu"))
        self.assertTrue(index["空崎阳奈（蔚蓝档案）"]["p"].startswith("kongqi"))
        # Spot-check core pinyin (series suffix stripped) for fuzzy matching
        self.assertEqual(index["胡桃（原神）"]["c"], "hutao")
        self.assertEqual(index["凯露（公主连结！Re:Dive）"]["c"], "kailu")
        self.assertTrue(index["空崎阳奈（蔚蓝档案）"]["c"].startswith("kongqiyangnai"))
        # 爱丽丝·卡塔雷特: full pinyin joins CJK syllables only
        self.assertTrue(index["爱丽丝·卡塔雷特（黄金拼图）"]["p"].startswith("ailisikataleite"))
        self.assertIn("凯露（公主连结！Re:Dive）", index)
        for entry in index.values():
            self.assertTrue(entry["i"].islower())
            self.assertTrue(entry["p"].islower())
            # c 为核心拼音，纯拉丁核心名（如 "12F（明日方舟）"）为空
            self.assertTrue(entry["c"] == "" or entry["c"].islower())

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
            "木之本藤隆（魔卡少女樱）": "kinomoto fujitaka",
            "木之本桃矢（魔卡少女樱）": "kinomoto touya",
            "月城雪兔（魔卡少女樱）": "tsukishiro yukito",
            "艾德（星际牛仔）": "edward wong hau pepelu tivrusky iv",
            "艾丽卡·欧维罗（星际牛仔）": "electra ovilo",
            "朱莉娅（星际牛仔）": "julia (cowboy bebop)",
            "比夏斯（星际牛仔）": "vicious (cowboy bebop)",
            "文森特·渥拉裘（星际牛仔）": "vincent volaju",
            "高须龙儿（龙与虎）": "takasu ryuuji",
            "高须泰子（龙与虎）": "takasu yasuko",
            "虚妹（凉宫春日的忧郁）": "kyon's sister",
            "三味线（凉宫春日的忧郁）": "shamisen (suzumiya haruhi)",
            "谷口（凉宫春日的忧郁）": "taniguchi (suzumiya haruhi)",
            "国木田（凉宫春日的忧郁）": "kunikida (suzumiya haruhi)",
            "阿万音由季（命运石之门）": "amane yuki",
            "天王寺绹（命运石之门）": "tennouji nae",
            "天王寺裕吾（命运石之门）": "tennouji yuugo",
            "椎名篝（命运石之门）": "shiina kagari",
            "巴特（攻壳机动队）": "batou (gits)",
            "户草（攻壳机动队）": "togusa (gits)",
            "荒卷大辅（攻壳机动队）": "aramaki daisuke",
            "石川（攻壳机动队）": "ishikawa (gits)",
            "斋藤（攻壳机动队）": "saitou (gits)",
            "波玛（攻壳机动队）": "boma (gits)",
            "塔奇克马（攻壳机动队）": "tachikoma",
            "富奇科马（攻壳机动队）": "fuchikoma",
            "地场卫（美少女战士）": "chiba mamoru",
            "天王遥（美少女战士）": "ten'ou haruka",
            "海王满（美少女战士）": "kaiou michiru",
            "冥王雪奈（美少女战士）": "meiou setsuna",
            "星野光（美少女战士）": "seiya kou",
            "大气光（美少女战士）": "taiki kou",
            "夜天光（美少女战士）": "yaten kou",
            "早乙女乱马（乱马½）": "saotome ranma",
            "天道靡（乱马½）": "tendou nabiki",
            "天道霞（乱马½）": "tendou kasumi",
            "天道早云（乱马½）": "tendou souun",
            "早乙女玄马（乱马½）": "saotome genma",
            "沐丝（乱马½）": "mousse (ranma 1/2)",
            "裤袜太郎（乱马½）": "pantyhose tarou",
            "九能带刀（乱马½）": "kunou tatewaki",
            "九能小太刀（乱马½）": "kunou kodachi",
            "五寸钉光（乱马½）": "gosunkugi hikaru",
            "阿迪涅（天元突破）": "adiane",
            "达莉·阿代（天元突破）": "darry adai",
            "基米·阿代（天元突破）": "gimmy adai",
            "奇坦·巴奇卡（天元突破）": "kittan bachika",
            "吉永·巴奇卡（天元突破）": "kiyoh bachika",
            "利珑·利特纳（天元突破）": "leeron littner",
            "罗杰侬（天元突破）": "lordgenome",
            "维拉尔（天元突破）": "viral (ttgl)",
            "黎星刻（反叛的鲁路修）": "li xingke",
            "利瓦尔·卡尔德蒙德（反叛的鲁路修）": "rivalz cardemonde",
            "查尔斯·Di·布里塔尼亚（反叛的鲁路修）": "charles zi britannia",
            "修奈泽尔·El·布里塔尼亚（反叛的鲁路修）": "schneizel el britannia",
            "藤堂镜志朗（反叛的鲁路修）": "toudou kyoushirou",
            "篠崎咲世子（反叛的鲁路修）": "shinozaki sayoko",
            "阿列克斯·路易·阿姆斯特朗（钢之炼金术士）": "alex louis armstrong",
            "格拉托尼（钢之炼金术士）": "gluttony (fma)",
            "格利德（钢之炼金术士）": "greed (fma)",
            "马斯·休斯（钢之炼金术士）": "maes hughes",
            "普莱德（钢之炼金术士）": "pride (fma)",
            "斯卡（钢之炼金术士）": "scar (fma)",
            "斯洛斯（钢之炼金术士）": "sloth (fma)",
            "泉·卡迪斯（钢之炼金术士）": "izumi curtis",
            "佐尔夫·J·金布利（钢之炼金术士）": "solf j. kimblee",
            "柊美纪（幸运星）": "hiiragi miki",
            "泉彼方（幸运星）": "izumi kanata",
            "泉总次郎（幸运星）": "izumi soujirou",
            "黑井奈那子（幸运星）": "kuroi nanako",
            "峰岸绫乃（幸运星）": "minegishi ayano",
            "成实唯（幸运星）": "narumi yui",
            "帕特莉西亚·马汀（幸运星）": "patricia martin",
            "白石稔（幸运星）": "shiraishi minoru",
            "田村日和（幸运星）": "tamura hiyori",
            "犬夜叉（犬夜叉）": "inuyasha (character)",
            "弥勒（犬夜叉）": "miroku (inuyasha)",
            "七宝（犬夜叉）": "shippou (inuyasha)",
            "桔梗（犬夜叉）": "kikyou (inuyasha)",
            "铃（犬夜叉）": "rin (inuyasha)",
            "邪见（犬夜叉）": "jaken",
            "神乐（犬夜叉）": "kagura (inuyasha)",
            "琥珀（犬夜叉）": "kohaku (inuyasha)",
            "钢牙（犬夜叉）": "kouga (inuyasha)",
            "云母（犬夜叉）": "kirara (inuyasha)",
            "诸叶（犬夜叉）": "moroha",
            "奈落（犬夜叉）": "naraku (inuyasha)",
            "诸星当（福星小子）": "moroboshi ataru",
            "三宅忍（福星小子）": "miyake shinobu",
            "面堂终太郎（福星小子）": "mendou shuutarou",
            "藤波龙之介（福星小子）": "fujinami ryuunosuke",
            "弁天（福星小子）": "benten (urusei yatsura)",
            "小天（福星小子）": "ten (urusei yatsura)",
            "兰（福星小子）": "ran (urusei yatsura)",
            "阿雪（福星小子）": "oyuki (urusei yatsura)",
            "错乱坊（福星小子）": "cherry (urusei yatsura)",
            "樱花（福星小子）": "sakura (urusei yatsura)",
            "克拉玛（福星小子）": "kurama (urusei yatsura)",
            "眼镜（福星小子）": "megane (urusei yatsura)",
            "波卷（福星小子）": "perm (urusei yatsura)",
            "艾基尔（刀剑神域）": "agil",
            "克莱因（刀剑神域）": "klein (sao)",
            "阿尔戈（刀剑神域）": "argo the rat",
            "须乡伸之（刀剑神域）": "sugou nobuyuki",
            "茅场晶彦（刀剑神域）": "kayaba akihiko",
            "尤吉欧（刀剑神域）": "eugeo",
            "幸（刀剑神域）": "sachi (sao)",
            "西莉卡（刀剑神域）": "silica",
            "吉尔伯特·布干维利亚（紫罗兰永恒花园）": "gilbert bougainvillea",
            "克劳迪娅·霍金斯（紫罗兰永恒花园）": "claudia hodgins",
            "迪特弗里特·布干维利亚（紫罗兰永恒花园）": "dietfried bougainvillea",
            "爱丽丝·卡纳利（紫罗兰永恒花园）": "iris cannary",
            "卡塔莉娜·博德莱尔（紫罗兰永恒花园）": "cattleya baudelaire",
            "露库莉娅·马尔博罗（紫罗兰永恒花园）": "luculia marlborough",
            "艾米·巴特莱特（紫罗兰永恒花园）": "amy bartlett",
            "埃丽卡·布朗（紫罗兰永恒花园）": "erica brown",
            "班尼迪克特·布卢（紫罗兰永恒花园）": "benedict blue",
            "安妮·马格诺利亚（紫罗兰永恒花园）": "ann magnolia",
            "店长（孤独摇滚）": "pa-san",
            "后藤美智代（孤独摇滚）": "gotoh michiyo",
            "乙女樱（莉可丽丝）": "otome sakura",
            "普罗斯佩拉·墨丘利（机动战士高达：水星的魔女）": "prospera mercury",
            "妮卡·七浦（机动战士高达：水星的魔女）": "nika nanaura",
            "黑川茜（我推的孩子）": "kurokawa akane",
            "赞泽（葬送的芙莉莲）": "sense (sousou no frieren)",
            "灰姑娘（胜利女神：NIKKE）": "cinderella (nikke)",
            "贝伊（胜利女神：NIKKE）": "bay (nikke)",
            "艾德（胜利女神：NIKKE）": "ade (nikke)",
            "诺亚尔（胜利女神：NIKKE）": "noir (nikke)",
            "布兰儿（胜利女神：NIKKE）": "blanc (nikke)",
            "爱莲（胜利女神：NIKKE）": "elegg (nikke)",
            "卡罗琳（尘白禁区）": "caroline (snowbreak)",
            "知更鸟（崩坏：星穹铁道）": "robin (honkai: star rail)",
            "灰原哀（名侦探柯南）": "haibara ai",
            "玉叶妃（药屋少女的呢喃）": "gyokuyou (kusuriya no hitorigoto)",
            "若月妮可（WITCH WATCH）": "wakatsuki nico",
            "小舟潮（夏日重现）": "kofune ushio",
            "胡蝶忍（鬼灭之刃）": "kochou shinobu",
            "约尔·福杰（间谍过家家）": "yor briar",
            "玛露希尔（迷宫饭）": "marcille donato",
            "尤贝尔（葬送的芙莉莲）": "ubel (sousou no frieren)",
            "山田杏奈（我心里危险的东西）": "yamada anna",
            "恰斯卡（原神）": "chasca (genshin impact)",
            "艾梅莉埃（原神）": "emilie (genshin impact)",
            "圣园未花（蔚蓝档案）": "mika (blue archive)",
            "早濑优香（蔚蓝档案）": "yuuka (blue archive)",
            "白洲梓（蔚蓝档案）": "azusa (blue archive)",
            "空崎阳奈（蔚蓝档案）": "hina (blue archive)",
            "陆八魔阿露（蔚蓝档案）": "aru (blue archive)",
            "河和静子（蔚蓝档案）": "shizuko (blue archive)",
            "下江小春（蔚蓝档案）": "koharu (blue archive)",
            "春原旬（蔚蓝档案）": "shun (blue archive)",
            "调月莉音（蔚蓝档案）": "rio (blue archive)",
            "玛薇卡（原神）": "mavuika (genshin impact)",
            "希诺宁（原神）": "xilonen (genshin impact)",
            "瓦蕾莎（原神）": "varesa (genshin impact)",
            "朱菜（关于我转生变成史莱姆这档事）": "shuna (tensura)",
            "星锑（重返未来：1999）": "regulus (reverse:1999)",
            "苏芙比（重返未来：1999）": "sotheby",
            "有村麻央（学园偶像大师）": "arimura mao",
            "利维坦（胜利女神：NIKKE）": "leviathan (nikke)",
            "无声铃鹿（赛马娘）": "silence suzuka (umamusume)",
            "东海帝皇（赛马娘）": "tokai teio (umamusume)",
            "月村手毬（学园偶像大师）": "tsukimura temari",
            "结束祈（金牌得主）": "yuitsuka inori",
            "冈崎祈（金牌得主）": "okazaki iruka",
            "三轮霞（咒术回战）": "miwa kasumi",
            "广濑夏子（全修。）": "hirose natsuko",
            "尤尼奥（全修。）": "unio (zenshuu)",
            "贝蒂（Re:从零开始的异世界生活）": "beatrice (re zero)",
            "贝姬·布莱克贝尔（间谍过家家）": "becky blackbell",
            "春乌菈菈（赛马娘）": "haru urara (umamusume)",
            "摩耶重炮（赛马娘）": "mayano top gun (umamusume)",
            "里见光钻（赛马娘）": "satono diamond (umamusume)",
            "鲁道夫象征（赛马娘）": "symboli rudolf (umamusume)",
            "百合园圣亚（蔚蓝档案）": "seia (blue archive)",
            "生盐乃爱（蔚蓝档案）": "noa (blue archive)",
            "尾刃坎纳（蔚蓝档案）": "kanna (blue archive)",
            "橘野乃美（蔚蓝档案）": "nozomi (blue archive)",
            "古关忧（蔚蓝档案）": "ui (blue archive)",
            "飞鸟马时（蔚蓝档案）": "toki (blue archive)",
            "礼服陆八魔阿露（蔚蓝档案）": "aru (dress) (blue archive)",
            "白洲梓（泳装）（蔚蓝档案）": "azusa (swimsuit) (blue archive)",
            "下江小春-泳装（蔚蓝档案）": "koharu (swimsuit) (blue archive)",
            "河和静子（泳装）（蔚蓝档案）": "shizuko (swimsuit) (blue archive)",
            "早濑优香（运动服）（蔚蓝档案）": "yuuka (track) (blue archive)",
            "黑馆羽留奈（蔚蓝档案）": "haruna (blue archive)",
            "黑馆羽留奈（体操服）（蔚蓝档案）": "haruna (track) (blue archive)",
            "樱井美代（蔚蓝档案）": "miyo (blue archive)",
            "空井咲（蔚蓝档案）": "saki (blue archive)",
            "空井咲（泳装）（蔚蓝档案）": "saki (swimsuit) (blue archive)",
            "泷口宵（皎洁迎宵之月）": "takiguchi yoi",
            "可可（尖帽子魔法工房）": "coco (tongari boushi no atelier)",
            "紫苑（关于我转生变成史莱姆这档事）": "shion (tensura)",
            "黄金巨匠（赛马娘）": "orfevre (umamusume)",
            "目白莱恩（赛马娘）": "mejiro ryan (umamusume)",
            "爱慕织姬（赛马娘）": "admire vega (umamusume)",
            "比安卡（战双帕弥什）": "bianca (pgr)",
            "七实（战双帕弥什）": "nanami (pgr)",
            "卡列尼娜（战双帕弥什）": "karenina (pgr)",
            "娜尔梅亚（碧蓝幻想）": "narmaya (granblue fantasy)",
            "德丽莎·阿波卡利斯（崩坏3rd）": "theresa apocalypse",
            "娜尔梅亚·夏日（碧蓝幻想）": "narmaya (summer) (granblue fantasy)",
            "德丽莎·阿波卡利斯（月下眷属）（崩坏3rd）": "theresa apocalypse (luna kindred)",
            "德丽莎·阿波卡利斯（月誓绯爱）（崩坏3rd）": "theresa apocalypse (lunar vow  crimson love)",
            "德丽莎·阿波卡利斯（女武神誓约）（崩坏3rd）": "theresa apocalypse (valkyrie pledge)",
            "沙洛姆（无期迷途）": "shalom (path to nowhere)",
            "罗睺（无期迷途）": "rahu (path to nowhere)",
            "卓娅（无期迷途）": "zoya (path to nowhere)",
            "可可莉克（无期迷途）": "coquelic (path to nowhere)",
            "兰利（无期迷途）": "langley (path to nowhere)",
            "赫卡蒂（无期迷途）": "hecate (path to nowhere)",
            "黛伦（无期迷途）": "deren (path to nowhere)",
            "诺克斯（无期迷途）": "nox (path to nowhere)",
            "白逸（无期迷途）": "bai yi (path to nowhere)",
            "卡利奥斯特罗（碧蓝幻想）": "cagliostro (granblue fantasy)",
            "伊琳娜（无期迷途）": "eirene (path to nowhere)",
            "哈梅尔（无期迷途）": "hamel (path to nowhere)",
            "恩菲尔（无期迷途）": "enfer (path to nowhere)",
            "阿黛拉（无期迷途）": "adela (path to nowhere)",
            "希帕提娅（无期迷途）": "hypatia (path to nowhere)",
            "德雷雅（无期迷途）": "dreya (path to nowhere)",
            "标枪（碧蓝航线）": "javelin (azur lane)",
            "美美（公主连结！Re:Dive）": "mimi (princess connect!)",
            "静流（公主连结！Re:Dive）": "shizuru (princess connect!)",
            "纺希（公主连结！Re:Dive）": "tsumugi (princess connect!)",
            "优衣（公主连结！Re:Dive）": "yui (princess connect!)",
            "阿尔法（战双帕弥什）": "alpha (pgr)",
            "21号（战双帕弥什）": "no. 21 (pgr)",
            "拉弥亚（战双帕弥什）": "lamia (pgr)",
            "罗塞塔（战双帕弥什）": "rosetta (pgr)",
            "邦比娜塔（战双帕弥什）": "bambinata (pgr)",
            "赛琳娜（战双帕弥什）": "selena (pgr)",
            "管理员（明日方舟：终末地）": "endministrator (arknights)",
            "佩丽卡（明日方舟：终末地）": "perlica (arknights)",
            "乱破（崩坏：星穹铁道）": "rappa (honkai: star rail)",
            "椒丘（崩坏：星穹铁道）": "jiaoqiu (honkai: star rail)",
            "忘归人（崩坏：星穹铁道）": "fugue (honkai: star rail)",
            "加拉赫（崩坏：星穹铁道）": "gallagher (honkai: star rail)",
            "欧洛伦（原神）": "ororon (genshin impact)",
            "卡齐娜（原神）": "kachina (genshin impact)",
            "皇冠（胜利女神：NIKKE）": "crown (nikke)",
            "蒂亚（胜利女神：NIKKE）": "tia (nikke)",
            "梅里（胜利女神：NIKKE）": "mary (nikke)",
            "予愿安洁莉娜（明日方舟）": "angelina the mellow wish (arknights)",
            "新约能天使（明日方舟）": "exusiai the new covenant (arknights)",
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
