/** 与后端 player_content.py 一致的环节解锁逻辑（6+1 环节） */

export function unlockedSections(phaseIndex) {
  const sections = ['public']
  if (phaseIndex >= 1) sections.push('script', 'secret', 'allRoles', 'background')
  if (phaseIndex >= 3) sections.push('clue1')
  if (phaseIndex >= 4) sections.push('clue2')
  if (phaseIndex >= 5) sections.push('vote')
  if (phaseIndex >= 6) sections.push('reveal')
  return sections
}

export function publicRole(role) {
  return {
    id: role.id,
    name: role.name,
    gender: role.gender,
    title: role.title,
    tag: role.tag,
    publicIntro: role.publicIntro,
    poster: role.poster,
  }
}

export function buildAllRoles(scriptData) {
  return (scriptData?.roles || [])
    .map((r) => ({
      id: r.id,
      name: r.name,
      title: r.title,
      publicIntro: r.publicIntro,
      introOrder: r.introOrder,
    }))
    .sort((a, b) => a.introOrder - b.introOrder)
}

export function buildPlayerContent(role, phaseIndex, scriptData) {
  const unlocked = unlockedSections(phaseIndex)
  const content = { unlocked }

  if (unlocked.includes('public')) {
    content.public = publicRole(role)
  }
  if (unlocked.includes('background')) {
    content.background = scriptData.background || ''
  }
  if (unlocked.includes('script')) {
    content.personalScript = role.personalScript || []
  }
  if (unlocked.includes('secret')) {
    content.secretTasks = role.secretTasks || []
  }
  if (unlocked.includes('allRoles')) {
    content.allRoles = buildAllRoles(scriptData)
  }
  if (unlocked.includes('clue1')) {
    content.clue1 = role.privateClues?.[0] || ''
  }
  if (unlocked.includes('clue2')) {
    content.clue2 = role.privateClues?.[1] || ''
  }
  if (unlocked.includes('vote')) {
    content.voteForm = scriptData.voteForm || { fields: [] }
  }
  if (unlocked.includes('reveal')) {
    content.truth = scriptData.truth
  }

  return content
}
