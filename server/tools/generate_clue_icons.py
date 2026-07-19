"""生成 24 条私人线索 SVG 小图标。"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "frontend" / "src" / "static" / "clues"

# headline -> (filename, svg inner content without wrapper)
ICONS: dict[str, tuple[str, str]] = {
    "物证·账页残角": (
        "account-scrap",
        """
  <rect x="14" y="16" width="36" height="32" rx="2" fill="#F5E6C8" stroke="#8B6914" stroke-width="1.5"/>
  <path d="M18 22h28M18 28h22M18 34h18" stroke="#C4A574" stroke-width="1.2" stroke-linecap="round"/>
  <path d="M38 20l6 6-8 8-6-6z" fill="#E8D5B5" stroke="#8B6914" stroke-width="1"/>
  <circle cx="42" cy="38" r="4" fill="#E84855" opacity="0.85"/>
""",
    ),
    "档案·吵嚷记录": (
        "meeting-record",
        """
  <rect x="16" y="12" width="32" height="40" rx="2" fill="#F0E4CC" stroke="#7A5C3A" stroke-width="1.5"/>
  <path d="M22 20h20M22 26h16M22 32h18" stroke="#A08060" stroke-width="1.2" stroke-linecap="round"/>
  <path d="M40 38l8 8-4 2-2-4z" fill="#8B4513"/>
  <circle cx="46" cy="18" r="7" fill="#E84855" opacity="0.9"/>
  <text x="46" y="21" text-anchor="middle" fill="#fff" font-size="9" font-weight="700">!</text>
""",
    ),
    "物证·油渍字条": (
        "greasy-note",
        """
  <rect x="18" y="18" width="28" height="28" rx="3" fill="#FFF8E7" stroke="#C4A060" stroke-width="1.5" transform="rotate(-8 32 32)"/>
  <path d="M24 28h16M24 33h12" stroke="#8B7355" stroke-width="1.2" stroke-linecap="round"/>
  <ellipse cx="38" cy="38" rx="8" ry="5" fill="#D4A017" opacity="0.45"/>
""",
    ),
    "抄本·督办提醒": (
        "supervise-copy",
        """
  <rect x="15" y="14" width="34" height="36" rx="2" fill="#FFF5E6" stroke="#8B3A3A" stroke-width="1.5"/>
  <rect x="20" y="20" width="24" height="3" rx="1" fill="#C62828"/>
  <path d="M20 28h22M20 34h18M20 40h14" stroke="#A08060" stroke-width="1.2" stroke-linecap="round"/>
  <circle cx="44" cy="42" r="8" fill="#E84855" opacity="0.25"/>
  <text x="44" y="45" text-anchor="middle" fill="#C62828" font-size="8" font-weight="700">督</text>
""",
    ),
    "文书·加急通知": (
        "urgent-notice",
        """
  <rect x="16" y="12" width="32" height="40" rx="2" fill="#FFF0F0" stroke="#C62828" stroke-width="2"/>
  <rect x="22" y="18" width="20" height="4" rx="1" fill="#E84855"/>
  <path d="M22 28h20M22 34h16M22 40h12" stroke="#B07070" stroke-width="1.2" stroke-linecap="round"/>
  <path d="M42 10l6 4v6l-6 4-6-4v-6z" fill="#DE2910"/>
  <text x="42" y="18" text-anchor="middle" fill="#FFD54F" font-size="7" font-weight="700">急</text>
""",
    ),
    "转述·问询门外": (
        "door-hearsay",
        """
  <rect x="28" y="14" width="16" height="36" rx="1" fill="#D4C4A8" stroke="#7A5C3A" stroke-width="1.5"/>
  <circle cx="40" cy="32" r="2" fill="#8B6914"/>
  <path d="M14 24c4-6 10-8 14-8" stroke="#6B8E23" stroke-width="2" stroke-linecap="round" fill="none"/>
  <path d="M12 28c2 0 4 2 6 4" stroke="#6B8E23" stroke-width="1.5" stroke-linecap="round" fill="none"/>
  <ellipse cx="18" cy="32" rx="6" ry="8" fill="#F5E6C8" stroke="#8B6914" stroke-width="1"/>
""",
    ),
    "旁听·采购核对": (
        "purchase-check",
        """
  <rect x="14" y="18" width="36" height="28" rx="2" fill="#F5F0E6" stroke="#6B4423" stroke-width="1.5"/>
  <path d="M20 26h24M20 32h20M20 38h16" stroke="#A08060" stroke-width="1.2" stroke-linecap="round"/>
  <path d="M38 22l8 4v12l-8 4-8-4V26z" fill="#2D5016" opacity="0.85"/>
  <path d="M40 30l2 2 4-4" stroke="#fff" stroke-width="1.5" stroke-linecap="round" fill="none"/>
""",
    ),
    "备忘·质询方向": (
        "memo-inquiry",
        """
  <rect x="18" y="14" width="28" height="36" rx="2" fill="#FFF8E7" stroke="#8B6914" stroke-width="1.5"/>
  <path d="M24 22h16M24 28h14M24 34h12" stroke="#B09070" stroke-width="1.2" stroke-linecap="round"/>
  <path d="M42 38l8 8" stroke="#4A4A6A" stroke-width="2" stroke-linecap="round"/>
  <path d="M48 38l2 6-4 2z" fill="#E84855"/>
""",
    ),
    "草稿·清点差异": (
        "inventory-draft",
        """
  <rect x="16" y="16" width="32" height="32" rx="2" fill="#F0EAD6" stroke="#8B7355" stroke-width="1.5" transform="rotate(6 32 32)"/>
  <path d="M22 24h20M22 30h16" stroke="#A09070" stroke-width="1.2" stroke-linecap="round"/>
  <text x="26" y="40" fill="#C62828" font-size="10" font-weight="700">+3</text>
  <rect x="38" y="34" width="12" height="8" rx="1" fill="#D2B48C" stroke="#8B6914" stroke-width="1"/>
""",
    ),
    "简报·外勤线报": (
        "field-report",
        """
  <rect x="14" y="18" width="36" height="28" rx="2" fill="#E8F0E8" stroke="#2D5016" stroke-width="1.5"/>
  <path d="M20 26h24M20 32h18" stroke="#558B2F" stroke-width="1.2" stroke-linecap="round"/>
  <circle cx="44" cy="38" r="10" fill="#F5E6C8" stroke="#8B6914" stroke-width="1"/>
  <path d="M40 38h8M44 34v8" stroke="#C62828" stroke-width="1.5" stroke-linecap="round"/>
""",
    ),
    "收档·匿名短笺": (
        "anonymous-notes",
        """
  <rect x="12" y="20" width="18" height="24" rx="2" fill="#FFF5E6" stroke="#8B6914" stroke-width="1.2" transform="rotate(-10 21 32)"/>
  <rect x="24" y="16" width="18" height="24" rx="2" fill="#FFF8E7" stroke="#8B6914" stroke-width="1.2"/>
  <rect x="34" y="22" width="18" height="24" rx="2" fill="#F5F0E6" stroke="#8B6914" stroke-width="1.2" transform="rotate(8 43 34)"/>
  <text x="33" y="30" text-anchor="middle" fill="#888" font-size="10">?</text>
""",
    ),
    "质证·三方笔录": (
        "three-statements",
        """
  <rect x="10" y="22" width="14" height="20" rx="1" fill="#F5E6C8" stroke="#8B6914" stroke-width="1"/>
  <rect x="25" y="18" width="14" height="24" rx="1" fill="#FFF0F0" stroke="#C62828" stroke-width="1"/>
  <rect x="40" y="22" width="14" height="20" rx="1" fill="#E8F0E8" stroke="#2D5016" stroke-width="1"/>
  <path d="M17 28h0M32 26h0M47 28h0" stroke="#888" stroke-width="2" stroke-linecap="round"/>
""",
    ),
    "登记·深夜留灯": (
        "night-lamp-log",
        """
  <rect x="16" y="16" width="32" height="32" rx="2" fill="#FFF8E7" stroke="#8B6914" stroke-width="1.5"/>
  <path d="M22 24h20M22 30h16M22 36h12" stroke="#B09070" stroke-width="1.2" stroke-linecap="round"/>
  <path d="M46 14v10" stroke="#B8860B" stroke-width="2" stroke-linecap="round"/>
  <circle cx="46" cy="28" r="6" fill="#FFD54F" opacity="0.9"/>
  <circle cx="46" cy="28" r="3" fill="#FFF8E1"/>
""",
    ),
    "物证·橡皮屑": (
        "eraser-crumb",
        """
  <rect x="20" y="20" width="24" height="14" rx="3" fill="#FF8FAB" stroke="#C62828" stroke-width="1"/>
  <circle cx="24" cy="40" r="2" fill="#D4C4A8"/>
  <circle cx="30" cy="42" r="1.5" fill="#C4B498"/>
  <circle cx="36" cy="39" r="2" fill="#E8D5B5"/>
  <circle cx="42" cy="43" r="1.5" fill="#D4C4A8"/>
  <path d="M18 38c6-2 10-2 16 0" stroke="#A08060" stroke-width="1" stroke-linecap="round" fill="none"/>
""",
    ),
    "勘查·封条记录": (
        "seal-inspection",
        """
  <rect x="14" y="20" width="36" height="28" rx="2" fill="#E8E0D0" stroke="#6B4423" stroke-width="1.5"/>
  <rect x="18" y="24" width="28" height="4" fill="#C62828" opacity="0.8"/>
  <text x="32" y="27" text-anchor="middle" fill="#fff" font-size="5" font-weight="700">封</text>
  <path d="M22 34h20M22 40h14" stroke="#8B7355" stroke-width="1.2" stroke-linecap="round"/>
  <path d="M42 14l4 4-6 6-4-4z" fill="#2D5016" opacity="0.7"/>
""",
    ),
    "报告·实物核对": (
        "goods-report",
        """
  <rect x="14" y="22" width="20" height="24" rx="1" fill="#F5E6C8" stroke="#8B6914" stroke-width="1"/>
  <rect x="30" y="18" width="20" height="28" rx="2" fill="#FFF8E7" stroke="#6B4423" stroke-width="1.5"/>
  <path d="M34 26h12M34 32h10M34 38h8" stroke="#A08060" stroke-width="1.2" stroke-linecap="round"/>
  <rect x="16" y="26" width="12" height="10" rx="1" fill="#D2B48C"/>
""",
    ),
    "回执·外勤采购": (
        "purchase-receipt",
        """
  <rect x="16" y="14" width="32" height="36" rx="2" fill="#F0FFF0" stroke="#2D5016" stroke-width="1.5"/>
  <path d="M22 22h20M22 28h16" stroke="#558B2F" stroke-width="1.2" stroke-linecap="round"/>
  <rect x="22" y="34" width="20" height="10" rx="1" fill="#E84855" opacity="0.2" stroke="#C62828" stroke-width="1"/>
  <text x="32" y="41" text-anchor="middle" fill="#2D5016" font-size="7" font-weight="700">回执</text>
""",
    ),
    "侧记·交接语录": (
        "handover-quote",
        """
  <rect x="14" y="16" width="36" height="32" rx="2" fill="#FFF5E6" stroke="#8B6914" stroke-width="1.5"/>
  <path d="M20 26h24M20 32h18" stroke="#A08060" stroke-width="1.2" stroke-linecap="round"/>
  <ellipse cx="32" cy="42" rx="14" ry="6" fill="#F5E6C8" stroke="#8B6914" stroke-width="1"/>
  <text x="32" y="44" text-anchor="middle" fill="#6B4423" font-size="6">……</text>
""",
    ),
    "风闻·后门碰面": (
        "backdoor-rumor",
        """
  <rect x="26" y="14" width="20" height="36" rx="1" fill="#8B7355" stroke="#4A3728" stroke-width="1.5"/>
  <circle cx="42" cy="32" r="2" fill="#D4C4A8"/>
  <circle cx="18" cy="28" r="5" fill="#F5E6C8" stroke="#8B6914" stroke-width="1"/>
  <circle cx="46" cy="26" r="5" fill="#FFE8D6" stroke="#8B6914" stroke-width="1"/>
  <path d="M22 28h6" stroke="#888" stroke-width="1" stroke-dasharray="2 2"/>
""",
    ),
    "目击·库房吵嚷": (
        "warehouse-argument",
        """
  <rect x="12" y="18" width="40" height="28" rx="2" fill="#E8E0D0" stroke="#6B4423" stroke-width="1.5"/>
  <circle cx="24" cy="32" r="6" fill="#F5E6C8" stroke="#8B6914" stroke-width="1"/>
  <circle cx="40" cy="32" r="6" fill="#FFE0E0" stroke="#C62828" stroke-width="1"/>
  <path d="M30 28l4 4-4 4" stroke="#E84855" stroke-width="1.5" stroke-linecap="round" fill="none"/>
""",
    ),
    "拾得·粗粮饼": (
        "grain-cake",
        """
  <ellipse cx="32" cy="36" rx="16" ry="10" fill="#D2B48C" stroke="#8B6914" stroke-width="1.5"/>
  <path d="M20 34c4-4 8-6 12-6s8 2 12 6" stroke="#C4A060" stroke-width="1" fill="none"/>
  <rect x="22" y="18" width="20" height="12" rx="2" fill="#FFF8E7" stroke="#C4A060" stroke-width="1" transform="rotate(-15 32 24)"/>
""",
    ),
    "勤务·时间杂记": (
        "patrol-journal",
        """
  <rect x="16" y="14" width="32" height="36" rx="2" fill="#FFF8E7" stroke="#8B6914" stroke-width="1.5"/>
  <path d="M22 22h20M22 28h16M22 34h12" stroke="#B09070" stroke-width="1.2" stroke-linecap="round"/>
  <circle cx="44" cy="42" r="10" fill="#F5E6C8" stroke="#8B6914" stroke-width="1.5"/>
  <path d="M44 36v6l4 2" stroke="#6B4423" stroke-width="1.5" stroke-linecap="round"/>
  <circle cx="44" cy="36" r="1.5" fill="#6B4423"/>
""",
    ),
    "线报·敌情方向": (
        "intel-report",
        """
  <rect x="14" y="20" width="36" height="24" rx="2" fill="#E8EEF8" stroke="#4A4A6A" stroke-width="1.5"/>
  <path d="M20 28h24M20 34h16" stroke="#6A7A9A" stroke-width="1.2" stroke-linecap="round"/>
  <path d="M42 16l6 8-6 8-6-8z" fill="#C62828" opacity="0.85"/>
  <circle cx="42" cy="24" r="2" fill="#FFD54F"/>
""",
    ),
    "记录·岗位纠纷": (
        "dispute-log",
        """
  <rect x="14" y="16" width="36" height="32" rx="2" fill="#FFF0F0" stroke="#C62828" stroke-width="1.5"/>
  <path d="M20 24h24M20 30h20M20 36h16" stroke="#B07070" stroke-width="1.2" stroke-linecap="round"/>
  <path d="M38 22l8-4v8z" fill="#E84855"/>
  <path d="M46 22l-8 4v8z" fill="#2D5016" opacity="0.7"/>
""",
    ),
}

WRAPPER = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none">
  <rect width="64" height="64" rx="8" fill="#F2ECE0"/>
{body}</svg>
"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    lines = ["// Auto-generated clue icon map", "export const CLUE_ICON_MAP = {"]
    for headline, (slug, body) in ICONS.items():
        path = OUT / f"{slug}.svg"
        path.write_text(WRAPPER.format(body=body), encoding="utf-8")
        lines.append(f"  '{headline}': '/static/clues/{slug}.svg',")
    lines.append("}")
    lines.append("")
    lines.append("export function parseClueHeadlineKey(content = '') {")
    lines.append("  const m = String(content).match(/^【([^】]+)】/)")
    lines.append("  return m ? m[1] : ''")
    lines.append("}")
    lines.append("")
    lines.append("export function getClueIconUrl(content = '') {")
    lines.append("  const key = parseClueHeadlineKey(content)")
    lines.append("  return key ? CLUE_ICON_MAP[key] || '' : ''")
    lines.append("}")
    js_path = ROOT / "frontend" / "src" / "utils" / "clue-icons.js"
    js_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {len(ICONS)} icons -> {OUT}")
    print(f"wrote {js_path}")


if __name__ == "__main__":
    main()
