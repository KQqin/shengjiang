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
CLUES = {
    "chen-huaian": [
        "【物证·账页残角】秩序册里夹着半页脱落的粮油账残角，第三栏数字被反复擦拭，卷面发毛；批注笔迹似苏小禾，像从账房废纸篓翻出。",
        "【档案·吵嚷记录】站务临时会议摘要：上月盘点后林大山当众嚷「账房记错、库房不会少」，与你争执十余分钟，全站青年都听见了。",
    ],
    "su-xiaohe": [
        "【风闻·油渍字条】青年团学习室桌缝发现一张油渍便条：「饼留后门了，别提。」字迹难辨，站内却已议论「像外勤女办事员与值班小伙私下递物」——与你无关，却极易引火烧身。",
        "【抄本·督办提醒】公开栏督办提醒副本：陈怀安所辖粮油账页擦痕密集，按规定应登记上报，却未见对应流程记录——矛头指向账房骨干。",
    ],
    "lin-dashan": [
        "【文书·加急通知】陈怀安签发加急清点通知，措辞严厉：「账物不符就是政治问题，三日内复核」——扑面而来的压力，像把库房推上风口。",
        "【转述·问询门外】赵启山问询室门外听来：苏小禾曾称「库房可能有问题」，当时并无实物佐证，更像急于把压力甩出账房。",
    ],
    "wen-xiuning": [
        "【旁听·采购核对】路过采购室，听见江承业与马卫国核对回执：「温这次票据齐，货也对得上」——至少说明你这趟外勤本身未见异常。",
        "【备忘·质询方向】赵启山工作备忘一页：拟重点核问「涂改链条」「三人互相指称」——没点你名，外勤信誉却被卷进漩涡。",
    ],
    "zhou-mingyuan": [
        "【草稿·清点差异】库房学徒遗失的粗布清点草稿：实物比账册多出约三尺，旁有林大山批注「账房又记串了」——矛头直指账房。",
        "【简报·外勤线报】高顺平带回的线报摘要：白区特务近期活动集中在钨矿、军火线，粮油小额目标风险偏低——仅供参考。",
    ],
    "zhao-qishan": [
        "【收档·匿名短笺】进驻前收到多封匿名短笺，分别影射陈怀安「管账不严」、林大山「盘点马虎」、苏小禾「新人手生」——均无可核实物。",
        "【质证·三方笔录】陈怀安、林大山、苏小禾核心说法互指（库房马虎 / 账房记错 / 库房可能有问题），交叉比对后均无实物实锤。",
    ],
    "wu-qiulan": [
        "【登记·深夜留灯】站务巡查登记：苏小禾名下多次「账房深夜留灯」备案，事由皆写「加班誊账」——起初像肯干，细想却蹊跷。",
        "【物证·橡皮屑】账房窗台扫出一小撮橡皮屑与半枚磨损橡皮，纤维间夹纸灰；同晚二十七日 21:40 窗外曾见灯影下有人反复擦拭账页，身形似苏小禾。",
    ],
    "ma-weiguo": [
        "【勘查·封条马虎】库房实地勘验表：林大山负责区封条粘贴不齐、角落积灰未清——管理偏粗；但门窗锁具完好，无撬痕、无外人潜入。",
        "【报告·实物吻合】抽核实物与采购单：账页大规模涂改之前，大件物资与票据基本吻合；缺口主要体现在账面记录链，而非库房短少。",
    ],
    "jiang-chengye": [
        "【回执·外勤采购】温秀宁本次外勤采购回执联复印件：票据齐全、件数与卸货记录一致——可暂排除「采购途中大批短少」。",
        "【侧记·老会计叹息】陈怀安交接底册时叹道「这几本账擦得我心慌」，似对涂改痕迹早有察觉，却未见其按制度正式登记上报。",
    ],
    "liu-guilan": [
        "【风闻·后门传闻】扫街时听帮工嘀咕：上月二十三傍晚，见温秀宁与周明远在库房后门碰头，递了个小包——没人看清里面，已传成「私挪公粮」。",
        "【目击·库房吵嚷】你亲见林大山与陈怀安在库房激烈争吵，各执一词、互不相让；争吵只能证明矛盾深，证明不了谁偷了物资。",
    ],
    "huang-xiaogen": [
        "【拾得·粗粮饼】库房后门台阶发现两块油纸半包的粗粮饼，仍带余温；旁落一张外勤路程单角，样式像温秀宁归站时随身之物——说不清谁交谁收。",
        "【日志·出入总表】你整理的缺口关键时段出入总表：无人私下串通转移物资；大额交接均在公开区域，无隐蔽搬运记录。",
    ],
    "gao-shunping": [
        "【线报·敌情方向】外勤线报：白区特务惯以钨砂、军火、西药为目标，针对小额粮油布匹下手的可能性偏低——不能单独定案，但可缩小方向。",
        "【研判·站内症结】综合站内情况：陈怀安、苏小禾、林大山之间履职疏漏与互相攻讦，比「外部破坏」更符合本案特征——宜优先核查账务链条。",
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
            "showTimer": True,
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
            "showTimer": True,
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
        "粗布账实不符，站内流言四起。上级督查组紧急进驻，限时彻查。\n\n"
        "重要规则：本场为无凶案、非明凶、全员盲视角思政剧本。无反派、无恶意贪腐、无刻意破坏。"
        "请积极参与搜证与公聊推理，共同复盘风波根源。"
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
            "content": "缺口数额与时段已锁定；问题集中在站内账物记录与涂改痕迹，而非运输环节大批损失。",
        },
        {
            "id": "P2",
            "title": "内部举报信汇总",
            "subtitle": "督查组收档",
            "category": "站内档案",
            "icon": "✉️",
            "accent": "#6B4423",
            "seal": "档",
            "content": "多封举报指向「管理混乱」「互相攻讦」，但均无实物实锤，疑似流言放大所致。",
        },
        {
            "id": "P3",
            "title": "库房勘查报告",
            "subtitle": "马卫国 · 实地勘验",
            "category": "勘查记录",
            "icon": "🔍",
            "accent": "#2D5016",
            "seal": "勘",
            "content": "门窗锁具、围墙、封条完好；无撬痕、无外人潜入、无暴力破坏痕迹。",
        },
        {
            "id": "P4",
            "title": "出入时间表摘要",
            "subtitle": "黄小根 · 值班登记",
            "category": "勤务日志",
            "icon": "📅",
            "accent": "#4A4A6A",
            "seal": "志",
            "content": "缺口关键时段无人私下串通转移物资；相关同志往来均在公开区域，无隐蔽交接。",
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
        "summary": "无贪污、无特务、无采购舞弊。苏小禾因害怕批评涂改账本；陈怀安知悉涂改未上报；林大山小额盘点粗放；温周私下往来被误读；全员互相甩锅，将小错发酵为站级信任危机。",
        "timeline": [
            "苏小禾多次涂改账页（以为只是小错）",
            "库房盘点对不上，陈怀安、林大山、苏小禾互相指责",
            "苏小禾向督查作无实据猜测",
            "温秀宁、周明远私赠粗粮被流言误读",
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


def main() -> None:
    raw = EXTRACTED.read_text(encoding="utf-8")
    bg_m = re.search(r"剧本背景【全员公开必读】(.*?)重要玩家规则", raw, re.S)
    if bg_m:
        STATIC["background"] = bg_m.group(1).strip() + "\n\n" + re.search(
            r"重要玩家规则：(.*?)角色1", raw, re.S
        ).group(1).strip()

    doc_roles = parse_roles(raw)
    roles = []
    for rid, name, intro_order in ROLE_META:
        doc = doc_roles.get(name)
        if not doc:
            raise SystemExit(f"missing doc role: {name}")
        meta = ROLE_FIELDS[rid]
        roles.append(
            {
                "id": rid,
                "name": name,
                "gender": meta["gender"],
                "title": meta["title"],
                "tag": meta["tag"],
                "group": meta["group"],
                "introOrder": intro_order,
                "poster": f"assets/suqu-account-dispute/roles/{rid}/poster.png",
                "publicIntro": doc["publicIntro"],
                "personalScript": doc["personalScript"],
                "secretTasks": doc["secretTasks"],
                "privateClues": CLUES[rid],
            }
        )

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
