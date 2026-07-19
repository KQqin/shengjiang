"""从工作区 doc 提取文本，生成 shared/script-data.json。"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXTRACTED = ROOT.parent / "_scripts_extracted.txt"
OUT = ROOT / "shared" / "script-data.json"

ROLE_META = [
    ("chen-huaian", "陈怀安", 4),
    ("su-xiaohe", "苏小禾", 5),
    ("lin-dashan", "林大山", 6),
    ("wen-xiuning", "温秀宁", 7),
    ("zhou-mingyuan", "周明远", 8),
    ("zhao-qishan", "赵启山", 1),
    ("wu-qiulan", "吴秋岚", 2),
    ("ma-weiguo", "马卫国", 3),
    ("jiang-chengye", "江承业", 9),
    ("liu-guilan", "刘桂兰", 10),
    ("huang-xiaogen", "黄小根", 11),
    ("gao-shunping", "高顺平", 12),
]

# 线索规则：
# - 每人 privateClues[0]=一轮、privateClues[1]=二轮；共 12×2=24 条私人线索
# - 二轮另发 publicClues P1–P4（4 条，全员同步可见）
# - 私人线索写「关于他人的信息」，不写持有人自己的秘密
# - 获取不必拘泥旁观者：物品、档案、风闻、字条、登记摘录均可；关系疏远的角色也可持有
# - 红鲱鱼须落在第三方手中（尤其温周私事，不可分给温/周本人）
# - 一轮偏弱/含红鲱鱼；二轮略强，但不集中全部直锤
# - 部分弱线索可替换为带日期的时间线锚点，便于公聊拼时间轴（非每条线索都写日期）
# - 私人线索一律第三人称、客观陈述：只写可见事实/摘录/登记，不写评价、推论、引导语（如「矛头」「宜」「更像」「仅供参考」）
CLUES = {
    "chen-huaian": [
        "【物证·账页残角】秩序册里夹着半页脱落的粮油账残角，第三栏数字被反复擦拭，卷面发毛；边侧批注笔迹与苏小禾相近，旁注来源为账房废纸篓。",
        "【档案·吵嚷记录】站务临时会议摘要：上月盘点后，林大山当众称「账房记错、库房不会少」，与陈怀安争执十余分钟，在场青年多人听见。",
    ],
    "su-xiaohe": [
        "【物证·油渍字条】青年团学习室桌缝发现一张油渍便条，内容为「饼留后门了，别提。」字迹难辨；同期站内议论涉及外勤女办事员与值班小伙私下递物。",
        "【抄本·督办提醒】公开栏督办提醒副本：陈怀安所辖粮油账页擦痕密集，按规定应登记上报，登记簿中未见对应流程记录。",
    ],
    "lin-dashan": [
        "【文书·加急通知】陈怀安签发的加急清点通知全文：「账物不符就是政治问题，三日内复核。」",
        "【转述·问询门外】赵启山问询室门外记录：苏小禾曾称「库房可能有问题」，当时未附实物佐证材料。",
    ],
    "wen-xiuning": [
        "【旁听·采购核对】采购室隔墙所闻，江承业与马卫国核对回执时称：「温这次票据齐，货也对得上。」",
        "【备忘·质询方向】赵启山工作备忘一页，手写拟核问项：「涂改链条」「三人互相指称」。",
    ],
    "zhou-mingyuan": [
        "【草稿·清点差异】上月二十号大盘点，库房学徒遗失的粗布清点草稿：实物比账册登记多出约三尺；旁有林大山批注「账房又记串了」。",
        "【简报·外勤线报】高顺平带回的线报摘要：白区特务近期活动集中在钨矿、军火线；又记上月二十九号曾收敌情线报，站内未见对应预警记录。",
    ],
    "zhao-qishan": [
        "【收档·匿名短笺】进驻前收档多封匿名短笺，分别写陈怀安「管账不严」、林大山「盘点马虎」、苏小禾「新人手生」，均无可核实实物。",
        "【质证·三方笔录】陈怀安、林大山、苏小禾陈述摘抄：分别指称库房马虎、账房记错、库房可能有问题；交叉记录中未附实物佐证。",
    ],
    "wu-qiulan": [
        "【登记·深夜留灯】站务巡查登记：苏小禾名下多次「账房深夜留灯」备案，事由均登记为「加班誊账」。",
        "【物证·橡皮屑】账房窗台扫出一小撮橡皮屑与半枚磨损橡皮，纤维间夹纸灰；二十七日晚 21:40 账房窗外可见灯影下有人反复擦拭账页，身形似苏小禾。",
    ],
    "ma-weiguo": [
        "【勘查·封条记录】库房实地勘验表：林大山负责区封条粘贴不齐、角落积灰未清；门窗锁具完好，未见撬痕与外人闯入痕迹。",
        "【报告·实物核对】抽核实物与采购单对照记录：账页大规模涂改之前，大件物资数量与票据登记基本一致。",
    ],
    "jiang-chengye": [
        "【回执·外勤采购】温秀宁本次外勤采购回执联复印件：票据齐全，件数与卸货记录一致。",
        "【侧记·交接语录】陈怀安交接底册时的口述记录：「十五号撞见涂改，这几本账擦得我心慌」；同期未见其正式登记上报记录。",
    ],
    "liu-guilan": [
        "【风闻·后门碰面】帮工口述：上月二十三号傍晚，温秀宁与周明远在库房后门碰头，递过一个小包；未见包内物品，同期有「私挪公粮」传言。",
        "【目击·库房吵嚷】上月二十号下午，刘桂兰在库房外听见林大山与陈怀安争吵，双方各执一词。",
    ],
    "huang-xiaogen": [
        "【拾得·粗粮饼】库房后门台阶发现两块油纸半包的粗粮饼，仍带余温；旁落一张外勤路程单角，样式与温秀宁归站所用相近。",
        "【勤务·时间杂记】巡查杂记摘录：上月十号午前，陈怀安在账房外单独问话苏小禾；十八号傍晚，林大山按登记领福利粗粮出库，有办事员在场。",
    ],
    "gao-shunping": [
        "【线报·敌情方向】外勤线报摘录：白区特务近期活动目标以钨砂、军火、西药为主。",
        "【记录·岗位纠纷】站内近期纠纷记录摘抄：陈怀安、苏小禾、林大山三方存在互相指称与履职争执的多条记载。",
    ],
}

STATIC = {
    "id": "suqu-account-dispute",
    "title": "苏区账目风波",
    "subtitle": "物资总站的一天",
    "maxPlayers": 12,
    "maxConnections": 13,
    "phases": [
        {
            "id": 0,
            "key": "lobby",
            "name": "入场",
            "displayType": "lobby",
            "durationSec": 180,
            "showTimer": False,
            "hostHint": "等待 12 名学生加入并抽取角色卡",
        },
        {
            "id": 1,
            "key": "script",
            "name": "读剧本",
            "displayType": "script",
            "durationSec": 480,
            "showTimer": True,
            "hostHint": "学生阅读个人剧本与本场任务；可浏览全员简介",
        },
        {
            "id": 2,
            "key": "intro",
            "name": "自我介绍",
            "displayType": "discuss",
            "durationSec": 480,
            "showTimer": False,
            "hostHint": "按 introOrder 顺序线下发言，仅公开人物简介",
        },
        {
            "id": 3,
            "key": "search1",
            "name": "一轮线索",
            "displayType": "search",
            "durationSec": 420,
            "showTimer": True,
            "hostHint": "发放私人线索①，组织学生公聊讨论，可自愿公开",
        },
        {
            "id": 4,
            "key": "search2",
            "name": "二轮线索",
            "displayType": "search",
            "durationSec": 420,
            "showTimer": True,
            "hostHint": "发放私人线索②与公共线索 P1–P4（同步进入公开卡池）",
        },
        {
            "id": 5,
            "key": "vote",
            "name": "讨论投票",
            "displayType": "vote",
            "durationSec": 480,
            "showTimer": False,
            "hostHint": "学生在手机端填写「事件真相」与「核心元凶」，大屏查看汇总",
        },
        {
            "id": 6,
            "key": "reveal",
            "name": "揭晓",
            "displayType": "reveal",
            "durationSec": 300,
            "showTimer": False,
            "hostHint": "展示真相时间线与思政小结",
        },
    ],
    "displayTypes": {
        "lobby": {"label": "入场准备", "icon": "🚪"},
        "script": {"label": "读剧本", "icon": "📜"},
        "search": {"label": "搜证", "icon": "🔍"},
        "discuss": {"label": "讨论", "icon": "💬"},
        "vote": {"label": "投票", "icon": "🗳️"},
        "reveal": {"label": "揭晓", "icon": "✨"},
    },
    "background": (
        "1932年，闽浙赣苏区正处在最艰难的封锁时期。物资总站是苏区物资中转、储备、核算的核心关口，"
        "所有人恪守「账物相符、分毫不差」的铁规。本月月底例行大盘点，多本账本出现涂改，小额粮油、"
        "粗布账实不符，站内流言四起。上级督查组紧急进驻，限时彻查。"
    ),
    "incident": {
        "title": "1932年 · 闽浙赣苏区物资总站",
        "body": "月底大盘点发现账目涂改与小额缺口，督查组进驻彻查。请还原真相，杜绝主观定罪。",
    },
    "publicClues": [
        {
            "id": "P1",
            "title": "上级审计摘要",
            "subtitle": "中央苏区审计处",
            "category": "官方文书",
            "icon": "📑",
            "accent": "#8B3A3A",
            "seal": "审",
            "content": "缺口数额与时段已锁定。站内账物记录存在涂改痕迹；运输环节大批损失记录未见异常。",
        },
        {
            "id": "P2",
            "title": "内部举报信汇总",
            "subtitle": "督查组收档",
            "category": "站内档案",
            "icon": "✉️",
            "accent": "#6B4423",
            "seal": "档",
            "content": "多封举报指向「管理混乱」「互相攻讦」，均未附实物佐证。",
        },
        {
            "id": "P3",
            "title": "库房勘查报告",
            "subtitle": "马卫国 · 实地勘验",
            "category": "勘查记录",
            "icon": "🔍",
            "accent": "#2D5016",
            "seal": "勘",
            "content": "本月一号清晨全站勘查：门窗锁具、围墙、封条完好；无撬痕、无外人潜入、无暴力破坏痕迹。",
        },
        {
            "id": "P4",
            "title": "出入时间表摘要",
            "subtitle": "黄小根 · 值班登记",
            "category": "勤务日志",
            "icon": "📅",
            "accent": "#4A4A6A",
            "seal": "志",
            "content": "缺口关键时段值班登记：相关岗位人员往来均在公开区域，未见单独隐蔽交接记录。",
        },
    ],
    "voteForm": {
        "fields": [
            {
                "key": "truth",
                "label": "事件真相（简短描述）",
                "placeholder": "请用一两句话描述你认为的风波真相",
            },
            {
                "key": "culprit",
                "label": "核心元凶（填人名）",
                "placeholder": "填写核心责任人姓名",
            },
        ],
        "referenceAnswer": {
            "truth": "苏小禾涂改账本引发连锁反应，陈怀安知情未报，三人互泼脏水，无实质性贪污",
            "culprit": "苏小禾",
        },
    },
    "truth": {
        "summary": "无贪污、无特务、无采购舞弊。苏小禾因害怕批评长期涂改账本；陈怀安知悉涂改未上报；林大山小额盘点粗放；温周私下往来被误读；督查与情报环节亦有前置缺位；全员互相甩锅，将小错发酵为站级信任危机。",
        "timeline": [
            "上月10号：陈怀安私密问话苏小禾，苏小禾心生猜忌",
            "上月15号下午：苏小禾涂改粮油账页被陈怀安撞见，仅口头提醒",
            "上月18号傍晚：林大山依规领取福利粗粮，苏小禾目击生疑",
            "上月20号：大盘点陈怀安与林大山争执（刘桂兰拐角目击），粗布差三尺",
            "上月23号傍晚：温秀宁私赠周明远粗粮饼（黄小根远处目击）",
            "上月27号深夜：苏小禾独自涂改粗布错账（吴秋岚21:40窗外目击）",
            "上月29号：高顺平收白区特务线报（未全站预警）",
            "本月1号清晨：马卫国全站勘查，排除暴力潜入",
            "无数小错累积发酵，三人互泼脏水，流言放大",
            "督查与证人线索排除特务破坏、采购舞弊",
        ],
        "moral": "小问题隐瞒会酿成站级信任危机；就事论事、以证说话，比互相泼脏水更重要。",
    },
}

ROLE_FIELDS = {
    "chen-huaian": {
        "gender": "男",
        "title": "总账老会计",
        "tag": "资深财务、严谨古板、恩怨核心",
        "group": "feud",
    },
    "su-xiaohe": {
        "gender": "女",
        "title": "青年记账员",
        "tag": "入职三月、胆小怯懦、风波源头",
        "group": "feud",
    },
    "lin-dashan": {
        "gender": "男",
        "title": "库房主管",
        "tag": "实干急躁、不拘小节、恩怨核心",
        "group": "feud",
    },
    "wen-xiuning": {
        "gender": "女",
        "title": "外勤采购队员",
        "tag": "勇敢细腻、贸易联络",
        "group": "romance",
    },
    "zhou-mingyuan": {
        "gender": "男",
        "title": "库房库管员",
        "tag": "踏实肯干、沉默内敛",
        "group": "romance",
    },
    "zhao-qishan": {
        "gender": "男",
        "title": "督查组长",
        "tag": "上级特派、客观公正",
        "group": "inspector",
    },
    "wu-qiulan": {
        "gender": "女",
        "title": "督查组员",
        "tag": "心思细腻、捕捉矛盾",
        "group": "inspector",
    },
    "ma-weiguo": {
        "gender": "男",
        "title": "督查组员",
        "tag": "作风硬朗、现场勘查",
        "group": "inspector",
    },
    "jiang-chengye": {
        "gender": "男",
        "title": "采购负责人",
        "tag": "贸易主管、原则极强",
        "group": "neutral",
    },
    "liu-guilan": {
        "gender": "女",
        "title": "后勤组长",
        "tag": "温和公允、善于察人",
        "group": "neutral",
    },
    "huang-xiaogen": {
        "gender": "男",
        "title": "后勤干事",
        "tag": "勤快跑腿、目击面广",
        "group": "neutral",
    },
    "gao-shunping": {
        "gender": "男",
        "title": "外勤队员",
        "tag": "情报研判、对敌经验丰富",
        "group": "neutral",
    },
}


def split_paragraphs(text: str) -> list[str]:
    parts = re.split(r"(?<=[。！？])\s*", text.strip())
    paras: list[str] = []
    buf = ""
    for p in parts:
        if not p:
            continue
        buf += p
        if len(buf) >= 120 or p.endswith(("。", "！", "？")):
            paras.append(buf.strip())
            buf = ""
    if buf.strip():
        paras.append(buf.strip())
    return paras


def parse_roles(raw: str) -> dict[str, dict]:
    parsed: dict[str, dict] = {}
    chunks = re.split(r"角色\d+：", raw)
    names = re.findall(r"角色\d+：([^【]+)【人物简介", raw)
    for name, chunk in zip(names, chunks[1:]):
        name = name.split("｜")[0].strip()
        intro_m = re.search(r"【人物简介·全员可见】(.*?)【个人剧本·仅自己可见】", chunk, re.S)
        script_m = re.search(r"【个人剧本·仅自己可见】(.*?)【本场任务】", chunk, re.S)
        task_m = re.search(r"【本场任务】(.*?)(?=角色\d+：|主持人专属|$)", chunk, re.S)
        if not (intro_m and script_m and task_m):
            continue
        tasks = [
            re.sub(r"^\d+[、.]", "", line).strip()
            for line in re.split(r"\d+[、.]", task_m.group(1).strip())
            if line.strip()
        ]
        parsed[name] = {
            "publicIntro": intro_m.group(1).strip(),
            "personalScript": split_paragraphs(script_m.group(1).strip()),
            "secretTasks": tasks,
        }
    return parsed


SU_XIAOHE_MAR15 = (
    "上月十五号下午，你在账房涂改一笔粮油数目，纸面擦得发毛。"
    "陈会计从门口经过，只淡淡说了句「下次仔细点，尽量少涂改」，"
    "你红着脸点头，心里却松了口气——他没有声张，你也便把这件事抛在脑后。"
)


def ensure_timeline_closure(roles: list[dict]) -> None:
    """补全时间线对照表要求、原文未写明的关键互证段落。"""
    for role in roles:
        if role["id"] != "su-xiaohe":
            continue
        script = role["personalScript"]
        joined = "".join(script)
        if "十五号" in joined or "15号" in joined:
            return
        insert_at = next(
            (i for i, p in enumerate(script) if "二十七" in p or "27号" in p),
            len(script),
        )
        script.insert(insert_at, SU_XIAOHE_MAR15)


def apply_script_dedup_patches(roles: list[dict]) -> None:
    """去除个人剧本中已知的语义重复段落（与 script-data.json 手工修订保持一致）。"""
    by_id = {r["id"]: r for r in roles}

    wen = by_id.get("wen-xiuning")
    if wen:
        wen["personalScript"] = [
            p
            for p in wen["personalScript"]
            if "风波爆发后，站内凭空传出你与周明远私相授受" not in p
            and "你九死一生奔走在封锁线，每一次采购流程都合规严谨" not in p
            and "但你深知当下站内人心惶惶、人人自危，私下赠物的小事一旦被刻意放大" not in p
        ]

    su = by_id.get("su-xiaohe")
    if su:
        trimmed: list[str] = []
        for p in su["personalScript"]:
            if p.startswith("风波突发后，你内心又慌又疑"):
                continue
            if p.startswith("你一遍遍复盘自己入职以来的所有工作细节"):
                continue
            if p.startswith("可偶尔念头一闪：万一是自己涂改的时候算错了呢"):
                continue
            if p.startswith("你立刻又否定——不可能，每一笔你都核对过"):
                continue
            if p.startswith("当下站内流言四起、人心惶惶"):
                continue
            if p.startswith("你越复盘越细思极恐"):
                continue
            if p.startswith("陈怀安独掌账务审核大权"):
                continue
            if p.startswith("你内心猜忌重重、全员存疑"):
                continue
            trimmed.append(p)
        bridge = "你强迫自己不要再想涂改的事——越琢磨越像搬石头砸自己的脚。眼下最要紧的是把议论往「更有嫌疑」的方向引，别让人盯死账房。"
        if bridge not in "".join(trimmed):
            for i, p in enumerate(trimmed):
                if "别牵连到自己头上" in p:
                    trimmed.insert(i + 1, bridge)
                    break
        su["personalScript"] = trimmed

    zhao = by_id.get("zhao-qishan")
    if zhao:
        zhao["personalScript"] = [
            p
            for p in zhao["personalScript"]
            if not p.startswith("你到站之初，仅掌握基础案情")
            and not p.startswith("上级并未告知你责任人、问题源头与事件性质")
        ]

    zhou = by_id.get("zhou-mingyuan")
    if zhou:
        zhou["personalScript"] = [
            (
                "风波之下，你更加开不了口辩解，只能默默坚守库房本职、先把手头台账一项项核对清楚。"
                if p.startswith("你性格内敛、不善言辞、不喜争辩，只能默默坚守库房本职")
                else p
            )
            for p in zhou["personalScript"]
        ]

    huang = by_id.get("huang-xiaogen")
    if huang:
        merged = False
        out: list[str] = []
        for p in huang["personalScript"]:
            if p.startswith("你日日巡查、遍历全站各个区域"):
                continue
            if p.startswith("长期值守巡查下来，你可以百分百确定"):
                out.append(
                    "长期值守巡查下来，你走遍全站各区，可以确定：日常工作往来与物资交接都在公开流程内完成，从未目击大额物资偷运或隐秘外流。"
                )
                merged = True
                continue
            out.append(p)
        if not merged:
            for i, p in enumerate(out):
                if "全站每一处区域" in p and i + 1 < len(out):
                    out[i + 1 : i + 1] = [
                        "长期值守巡查下来，你走遍全站各区，可以确定：日常工作往来与物资交接都在公开流程内完成，从未目击大额物资偷运或隐秘外流。"
                    ]
                    break
        huang["personalScript"] = out


def main() -> None:
    raw = EXTRACTED.read_text(encoding="utf-8")
    bg_m = re.search(r"剧本背景【全员公开必读】(.*?)重要玩家规则", raw, re.S)
    if bg_m:
        STATIC["background"] = bg_m.group(1).strip()

    doc_roles = parse_roles(raw)
    roles = []
    for rid, name, intro_order in ROLE_META:
        doc = doc_roles.get(name)
        if not doc:
            raise SystemExit(f"missing doc role: {name}")
        meta = ROLE_FIELDS[rid]
        public_intro = doc["publicIntro"]
        gender = meta["gender"]
        if gender and not public_intro.startswith(f"{gender}，"):
            public_intro = f"{gender}，{public_intro}"
        roles.append(
            {
                "id": rid,
                "name": name,
                "gender": gender,
                "title": meta["title"],
                "tag": meta["tag"],
                "group": meta["group"],
                "introOrder": intro_order,
                "poster": f"assets/suqu-account-dispute/roles/{rid}/poster.png",
                "publicIntro": public_intro,
                "personalScript": doc["personalScript"],
                "secretTasks": doc["secretTasks"],
                "privateClues": CLUES[rid],
            }
        )

    ensure_timeline_closure(roles)
    apply_script_dedup_patches(roles)
    data = {**STATIC, "roles": roles}
    public_n = len(data.get("publicClues", []))
    if len(roles) != 12:
        raise SystemExit(f"expected 12 roles, got {len(roles)}")
    for r in roles:
        pc = r.get("privateClues") or []
        if len(pc) != 2:
            raise SystemExit(f"role {r['name']} must have 2 private clues, got {len(pc)}")
    if public_n != 4:
        raise SystemExit(f"expected 4 public clues, got {public_n}")
    vote_form = data.get("voteForm") or {}
    if len(vote_form.get("fields") or []) != 2:
        raise SystemExit("voteForm must have exactly 2 fields")
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {OUT} ({len(roles)} roles, {len(roles)*2} private + {public_n} public clues)")


if __name__ == "__main__":
    main()
