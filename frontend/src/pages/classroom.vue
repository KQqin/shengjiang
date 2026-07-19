<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import {
  courseNames,
  courseContent,
  defaultGame,
  defaultNodes,
  defaultSections,
  parseHeroFromTitle,
} from '../data/course-content.js'
import {
  bindTeachingFullscreenSync,
  markTeachingFullscreen,
  toggleTeachingFullscreen,
  restoreTeachingFullscreen,
} from '../utils/teaching-fullscreen.js'

const courseId = ref('1')
const pageIndex = ref(0)
const modalOpen = ref(false)
const modalTitle = ref('')
const modalScenario = ref('')
const modalClues = ref([])
const modalChoices = ref([])
const modalFeedback = ref('')
const selectedChoice = ref(-1)
const isFullscreen = ref(false)
const pageRoot = ref(null)

const content = computed(() => courseContent[courseId.value] || courseContent[Number(courseId.value)])
const courseTitle = computed(() => courseNames[courseId.value] || courseNames[Number(courseId.value)] || '五四运动与新文化启蒙')
const nodes = computed(() => content.value?.nodes || defaultNodes)
const sections = computed(() => {
  if (content.value?.sections) return content.value.sections
  const hero = parseHeroFromTitle(courseTitle.value)
  return defaultSections.map((sec) => {
    if (sec.type === 'hero') {
      return { ...sec, title: hero.title, highlight: hero.highlight, sub: hero.sub }
    }
    return sec
  })
})

const heroData = computed(() => {
  if (content.value) {
    return {
      title: content.value.heroTitle,
      highlight: content.value.heroHighlight,
      sub: content.value.heroSub,
    }
  }
  return parseHeroFromTitle(courseTitle.value)
})

const totalPages = computed(() => sections.value.length)
const canGoPrev = computed(() => pageIndex.value > 0)
const canGoNext = computed(() => pageIndex.value < totalPages.value - 1)

onLoad((query) => {
  if (query?.course) courseId.value = String(query.course)
})

function isInteractiveTarget(target) {
  if (!target?.closest) return false
  return !!target.closest('button, a, input, textarea, .game-card, .game-grid, .modal, .catalog-item')
}

function goBack() {
  uni.navigateTo({ url: '/pages/index' })
}

function goHost() {
  if (isFullscreen.value) markTeachingFullscreen()
  uni.navigateTo({ url: `/pages/script-host?course=${courseId.value}` })
}

function goRole() {
  if (isFullscreen.value) markTeachingFullscreen()
  uni.navigateTo({ url: `/pages/script-role?course=${courseId.value}` })
}

function goHistoryChoice() {
  if (isFullscreen.value) markTeachingFullscreen()
  uni.navigateTo({ url: `/pages/history-choice?course=${courseId.value}` })
}

function goToCatalogTarget(nodeLabel) {
  const idx = nodes.value.findIndex((n) => n === nodeLabel || n.includes(nodeLabel))
  if (idx >= 0) goToPage(idx)
}

function goToPage(i) {
  const next = Math.max(0, Math.min(i, totalPages.value - 1))
  pageIndex.value = next
}

function prevPage() {
  if (canGoPrev.value) goToPage(pageIndex.value - 1)
}

function nextPage() {
  if (canGoNext.value) goToPage(pageIndex.value + 1)
}

function onStageClick(e) {
  if (modalOpen.value) return
  if (isInteractiveTarget(e.target)) return
  nextPage()
}

function onStageContextMenu(e) {
  if (modalOpen.value) return
  if (isInteractiveTarget(e.target)) return
  e.preventDefault()
  prevPage()
}

function openGame(gameKey) {
  const games = content.value?.games
  const gameData = gameKey === 'default' ? defaultGame : (games?.[gameKey] || defaultGame)
  modalTitle.value = gameData.title
  modalScenario.value = gameData.scenario
  modalClues.value = gameData.clues || []
  modalChoices.value = gameData.choices || []
  modalFeedback.value = ''
  selectedChoice.value = -1
  modalOpen.value = true
}

function selectChoice(index, feedback) {
  selectedChoice.value = index
  modalFeedback.value = feedback
}

function closeModal() {
  modalOpen.value = false
}

function onModalBackdrop(e) {
  if (e.target === e.currentTarget) closeModal()
}

function isGameNode(i) {
  const node = nodes.value[i]
  return node && (node.includes('游戏') || node.includes('⚡'))
}

function usePatriotBg(section) {
  if (!section) return false
  if (section.type === 'hero') return true
  if (section.type !== 'block') return false
  if (section.variant === 'hc-intro' || section.variant === 'hc-rules') return true
  return section.heading === '本课小结'
}

async function toggleFullscreen() {
  if (typeof document === 'undefined') return
  const wasActive = isFullscreen.value
  const active = await toggleTeachingFullscreen()
  isFullscreen.value = active
  if (!wasActive && !active) {
    uni.showToast?.({ title: '当前环境不支持全屏', icon: 'none' })
  }
}

let unbindFullscreen = null

onMounted(() => {
  if (typeof document === 'undefined') return
  restoreTeachingFullscreen().then((active) => {
    isFullscreen.value = active
  })
  unbindFullscreen = bindTeachingFullscreenSync((active) => {
    isFullscreen.value = active
  })
})

onUnmounted(() => {
  unbindFullscreen?.()
})
</script>

<template>
  <view ref="pageRoot" class="page-classroom" :class="{ 'page-classroom--fullscreen': isFullscreen }">
    <view class="topbar">
      <view class="topbar-left">
        <button type="button" class="back" @click="goBack">← 返回首页</button>
        <text class="title">{{ courseTitle }}</text>
      </view>
      <button type="button" class="btn-teach" @click.stop="toggleFullscreen">
        {{ isFullscreen ? '退出全屏' : '全屏上课' }}
      </button>
    </view>

    <view class="body">
      <view class="timeline">
        <view class="timeline-label">课件时间线</view>
        <view
          v-for="(n, i) in nodes"
          :key="'tl-' + i"
          class="tl-node"
          :class="{ active: pageIndex === i, game: isGameNode(i) }"
          @click="goToPage(i)"
        >
          {{ n }}
        </view>
      </view>

      <view class="slide-panel">
        <view class="slide-stage" @click="onStageClick" @contextmenu="onStageContextMenu">
          <view
            v-if="sections[pageIndex]"
            :key="'sec-' + pageIndex"
            class="sec"
            :class="{
              hero: sections[pageIndex].type === 'hero',
              'sec--alt': pageIndex % 2 === 1 && !usePatriotBg(sections[pageIndex]) && sections[pageIndex].type !== 'full-image' && sections[pageIndex].type !== 'catalog' && sections[pageIndex].variant !== 'youth-portraits',
              'sec--game': ['history-choice-game', 'script-murder-game', 'single-game', 'dual-games'].includes(sections[pageIndex].type),
              'sec--game-battle': sections[pageIndex].type === 'history-choice-game',
              'sec--game-script': sections[pageIndex].type === 'script-murder-game',
              'sec--full-image': sections[pageIndex].type === 'full-image',
              'sec--catalog': sections[pageIndex].type === 'catalog',
              'sec--youth-portraits': sections[pageIndex].type === 'block' && sections[pageIndex].variant === 'youth-portraits',
              'sec--patriot-bg': usePatriotBg(sections[pageIndex]),
            }"
          >
            <template v-if="sections[pageIndex].type === 'hero'">
              <view class="hero-h1">
                <text>{{ heroData.title }}</text>
                <text v-if="heroData.highlight" class="hero-highlight">{{ heroData.highlight }}</text>
              </view>
              <view class="hero-p">{{ heroData.sub }}</view>
            </template>

            <view v-else-if="sections[pageIndex].type === 'catalog'" class="catalog-slide">
              <view class="catalog-items">
                <view
                  v-for="(item, ci) in sections[pageIndex].items"
                  :key="'cat-' + ci"
                  :class="['catalog-item', 'catalog-item--' + (ci + 1)]"
                  @click.stop="goToCatalogTarget(item.target)"
                >
                  <view class="catalog-label"><text class="catalog-label-seal">{{ item.seal }}</text>{{ item.label }}</view>
                </view>
              </view>
            </view>

            <view v-else-if="sections[pageIndex].type === 'block'" class="block" :class="'block--' + (sections[pageIndex].variant || 'default')">
              <view v-if="sections[pageIndex].heading" class="block-h2">{{ sections[pageIndex].heading }}</view>
              <view v-if="sections[pageIndex].subheading" class="block-subheading">{{ sections[pageIndex].subheading }}</view>
              <view
                v-for="(p, pi) in sections[pageIndex].paragraphs"
                :key="'p-' + pi"
                class="block-p"
              >
                {{ p }}
              </view>
              <view
                v-for="(q, qi) in sections[pageIndex].questions || []"
                :key="'q-' + qi"
                class="block-question"
              >
                {{ q }}
              </view>
              <view v-if="sections[pageIndex].closing" class="block-p block-closing">{{ sections[pageIndex].closing }}</view>
              <view v-if="sections[pageIndex].roles?.length" class="role-tags">
                <text v-for="(role, ri) in sections[pageIndex].roles" :key="'role-' + ri" class="role-tag">{{ role }}</text>
              </view>
              <view v-if="sections[pageIndex].rules?.length" class="rule-list">
                <view v-for="(rule, ri) in sections[pageIndex].rules" :key="'rule-' + ri" class="rule-item">
                  <text class="rule-icon">{{ rule.icon }}</text>
                  <text class="rule-text">{{ rule.text }}</text>
                </view>
              </view>
              <view v-if="sections[pageIndex].footer" class="block-footer">{{ sections[pageIndex].footer }}</view>
              <view v-if="sections[pageIndex].quote" class="quote">{{ sections[pageIndex].quote }}</view>
            </view>

            <view v-else-if="sections[pageIndex].type === 'full-image'" class="full-image-wrap">
              <image
                class="full-image-slide"
                :src="sections[pageIndex].src"
                :alt="sections[pageIndex].alt || ''"
                mode="aspectFit"
              />
            </view>

            <view v-else-if="sections[pageIndex].type === 'video'" class="block">
              <view v-if="sections[pageIndex].heading" class="block-h2">{{ sections[pageIndex].heading }}</view>
              <view class="video-placeholder">{{ sections[pageIndex].placeholder }}</view>
            </view>

            <view v-else-if="sections[pageIndex].type === 'single-game'" class="game-card">
              <view class="game-card-h3">⚔️ 李大钊的历史抉择</view>
              <view class="game-card-p">课件到此节点，触发内置互动游戏。如果你是 1919 年的李大钊，你会如何选择？</view>
              <button type="button" class="game-btn" @click.stop="openGame('default')">开始互动</button>
            </view>

            <view v-else-if="sections[pageIndex].type === 'history-choice-game'" class="game-card game-card--battle">
              <text class="game-tag">互动游戏 ①</text>
              <view class="game-card-h3">⚔️ 历史抉择</view>
              <button type="button" class="game-btn" @click.stop="goHistoryChoice">开始游戏</button>
            </view>

            <view v-else-if="sections[pageIndex].type === 'script-murder-game'" class="game-card game-card--script">
              <text class="game-tag">互动游戏 ②</text>
              <view class="game-card-h3">🎭 红色剧本杀</view>
              <view class="game-btn-row">
                <button type="button" class="game-btn" @click.stop="goHost">教师大屏</button>
                <button type="button" class="game-btn game-btn--pink" @click.stop="goRole">学生加入</button>
              </view>
            </view>

            <view v-else-if="sections[pageIndex].type === 'dual-games'" class="game-grid">
              <view class="game-card game-card--battle">
                <text class="game-tag">互动游戏 ①</text>
                <view class="game-card-h3">⚔️ 历史抉择</view>
                <button type="button" class="game-btn" @click.stop="goHistoryChoice">教师大屏</button>
              </view>
              <view class="game-card game-card--script">
                <text class="game-tag">互动游戏 ②</text>
                <view class="game-card-h3">🎭 红色剧本杀</view>
                <view class="game-btn-row">
                  <button type="button" class="game-btn" @click.stop="goHost">教师大屏</button>
                  <button type="button" class="game-btn game-btn--pink" @click.stop="goRole">学生加入</button>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view class="modal" :class="{ open: modalOpen }" @click="onModalBackdrop">
      <view class="modal-box" @click.stop>
        <view class="modal-head">
          <view class="modal-head-h4">{{ modalTitle }}</view>
          <button type="button" class="modal-close" @click="closeModal">✕</button>
        </view>
        <view class="modal-body">
          <view class="scenario">{{ modalScenario }}</view>
          <view v-if="modalClues.length" class="clue-list">
            <view v-for="(clue, ci) in modalClues" :key="ci" class="clue-item">{{ clue }}</view>
          </view>
          <button
            v-for="(ch, ci) in modalChoices"
            :key="ci"
            type="button"
            class="choice"
            :class="{ selected: selectedChoice === ci }"
            @click="selectChoice(ci, ch.feedback)"
          >
            {{ ch.text }}
          </button>
          <view class="feedback" :class="{ show: modalFeedback }">{{ modalFeedback }}</view>
        </view>
      </view>
    </view>
  </view>
</template>

<style lang="scss">
@import '../styles/classroom.scss';

.page-classroom {
  .topbar-left {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .body {
    flex: 1;
    min-height: 0;
  }

  .slide-panel {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
  }

  .slide-stage {
    flex: 1;
    min-height: 0;
    position: relative;
    overflow: hidden;
    cursor: default;
  }

  .slide-stage .sec {
    width: 100%;
    height: 100%;
    min-height: 0;
    animation: slide-in 0.28s ease;
  }

  @keyframes slide-in {
    from {
      opacity: 0;
      transform: translateX(18px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }

  .game-card-hint {
    font-size: 14px;
    margin-bottom: 16px;
    color: var(--text-light);
    text-align: left;
  }

  .game-btn-row {
    display: flex;
    gap: 10px;
    justify-content: center;
    flex-wrap: wrap;
  }

  .game-btn--pink {
    background: linear-gradient(180deg, #9B2E24 0%, var(--red-deep) 100%);
    color: #FFFBF5;
  }

  .clue-list {
    margin: 12px 0;
    padding-left: 0;
    list-style: none;
  }

  .clue-item {
    padding: 10px 0;
    margin-bottom: 0;
    background: transparent;
    border-bottom: 1px solid var(--divider-soft);
    border-radius: 0;
    font-size: 15px;
    color: var(--text-muted);
  }

  .video-placeholder {
    text-align: center;
    padding: 40px 0;
    border: none;
    border-top: 1px solid var(--divider-soft);
    border-bottom: 1px solid var(--divider-soft);
    border-radius: 0;
    font-size: 18px;
    color: var(--text-light);
  }

  .block--hc-intro,
  .block--hc-rules {
    max-width: 760px;
  }

  .block-subheading {
    font-family: var(--font-display);
    font-size: 36px;
    font-weight: 400;
    color: var(--title-ink);
    margin-bottom: 20px;
    padding-left: 16px;
    border-left: 6px solid var(--gold);
    letter-spacing: 0.06em;
  }

  .block-question {
    font-size: 18px;
    line-height: 1.95;
    color: var(--text);
    margin-bottom: 0;
    padding: 16px 0 16px 14px;
    border-left: 4px solid var(--red);
    border-bottom: 1px solid var(--divider-soft);
  }

  .block-closing {
    margin-top: 16px;
  }

  .role-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    justify-content: flex-start;
    margin: 20px 0 24px;
    padding-top: 16px;
    border-top: 1px solid var(--divider-soft);
  }

  .role-tag {
    padding: 6px 14px;
    border-radius: 2px;
    font-size: 15px;
    color: #FFFBF5;
    background: var(--red-deep);
    border: 1px solid rgba(110, 20, 14, 0.35);
    margin-right: 0;
    font-weight: 600;
    letter-spacing: 0.06em;
  }

  .rule-list {
    display: flex;
    flex-direction: column;
    gap: 0;
    margin-top: 8px;
  }

  .rule-item {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    padding: 18px 0;
    border-radius: 0;
    background: transparent;
    border: none;
    border-bottom: 1px solid var(--divider-soft);
  }

  .rule-item:last-child {
    border-bottom: none;
  }

  .rule-icon {
    font-size: 22px;
    line-height: 1.4;
    flex-shrink: 0;
  }

  .rule-text {
    font-size: 17px;
    line-height: 1.9;
    color: var(--text-muted);
  }

  .block-footer {
    margin-top: 24px;
    padding-top: 16px;
    border-top: 1px solid var(--divider-soft);
    font-size: 14px;
    color: var(--text-light);
    text-align: left;
  }
}
</style>
