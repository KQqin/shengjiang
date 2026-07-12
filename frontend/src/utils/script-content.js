/** 与后端 room.js 一致的环节解锁逻辑 */

export function unlockedSections(phaseIndex) {
  const sections = ['public']
  if (phaseIndex >= 3) sections.push('secret')
  if (phaseIndex >= 4) sections.push('clue1')
  if (phaseIndex >= 6) sections.push('clue2')
  if (phaseIndex >= 7) sections.push('vote')
  if (phaseIndex >= 8) sections.push('reveal')
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
  }
}

export function buildPlayerContent(role, phaseIndex, scriptData) {
  const unlocked = unlockedSections(phaseIndex)
  const content = { unlocked }

  if (unlocked.includes('public')) {
    content.public = publicRole(role)
  }
  if (unlocked.includes('secret')) {
    content.secret = {
      relations: role.relations,
      secretTask: role.secretTask,
    }
  }
  if (unlocked.includes('clue1')) {
    content.clue1 = role.privateClues[0]
  }
  if (unlocked.includes('clue2')) {
    content.clue2 = role.privateClues[1]
  }
  if (unlocked.includes('vote')) {
    content.voteOptions = scriptData.voteOptions.map(({ id, text }) => ({ id, text }))
  }
  if (unlocked.includes('reveal')) {
    content.truth = scriptData.truth
  }

  return content
}
