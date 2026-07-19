// Auto-generated clue icon map
export const CLUE_ICON_MAP = {
  '物证·账页残角': '/static/clues/account-scrap.svg',
  '档案·吵嚷记录': '/static/clues/meeting-record.svg',
  '物证·油渍字条': '/static/clues/greasy-note.svg',
  '抄本·督办提醒': '/static/clues/supervise-copy.svg',
  '文书·加急通知': '/static/clues/urgent-notice.svg',
  '转述·问询门外': '/static/clues/door-hearsay.svg',
  '旁听·采购核对': '/static/clues/purchase-check.svg',
  '备忘·质询方向': '/static/clues/memo-inquiry.svg',
  '草稿·清点差异': '/static/clues/inventory-draft.svg',
  '简报·外勤线报': '/static/clues/field-report.svg',
  '收档·匿名短笺': '/static/clues/anonymous-notes.svg',
  '质证·三方笔录': '/static/clues/three-statements.svg',
  '登记·深夜留灯': '/static/clues/night-lamp-log.svg',
  '物证·橡皮屑': '/static/clues/eraser-crumb.svg',
  '勘查·封条记录': '/static/clues/seal-inspection.svg',
  '报告·实物核对': '/static/clues/goods-report.svg',
  '回执·外勤采购': '/static/clues/purchase-receipt.svg',
  '侧记·交接语录': '/static/clues/handover-quote.svg',
  '风闻·后门碰面': '/static/clues/backdoor-rumor.svg',
  '目击·库房吵嚷': '/static/clues/warehouse-argument.svg',
  '拾得·粗粮饼': '/static/clues/grain-cake.svg',
  '勤务·时间杂记': '/static/clues/patrol-journal.svg',
  '线报·敌情方向': '/static/clues/intel-report.svg',
  '记录·岗位纠纷': '/static/clues/dispute-log.svg',
}

export function parseClueHeadlineKey(content = '') {
  const m = String(content).match(/^【([^】]+)】/)
  return m ? m[1] : ''
}

export function getClueIconUrl(content = '') {
  const key = parseClueHeadlineKey(content)
  return key ? CLUE_ICON_MAP[key] || '' : ''
}
