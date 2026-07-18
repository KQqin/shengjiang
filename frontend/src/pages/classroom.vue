<script setup>
import { ref, computed, onMounted, onUnmounted, getCurrentInstance } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import {
  courseNames,
  courseContent,
  defaultGame,
  defaultNodes,
  defaultSections,
  parseHeroFromTitle,
} from '../data/course-content.js'

const courseId = ref('1')
const activeIndex = ref(0)
const modalOpen = ref(false)
const modalTitle = ref('')
const modalScenario = ref('')
const modalClues = ref([])
const modalChoices = ref([])
const modalFeedback = ref('')
const selectedChoice = ref(-1)

const instance = getCurrentInstance()
let scrollEl = null

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

onLoad((query) => {
  if (query?.course) courseId.value = String(query.course)
})

onMounted(() => {
  // #ifdef H5
  scrollEl = document.querySelector('.page-classroom .scroll')
  scrollEl?.addEventListener('scroll', handleScroll, { passive: true })
  // #endif
})

onUnmounted(() => {
  // #ifdef H5
  scrollEl?.removeEventListener('scroll', handleScroll)
  // #endif
})

function goBack() {
  uni.navigateTo({ url: '/pages/index' })
}

function goHost() {
  uni.navigateTo({ url: `/pages/script-host?course=${courseId.value}` })
}

function goRole() {
  uni.navigateTo({ url: `/pages/script-role?course=${courseId.value}` })
}

function goHistoryChoice() {
  uni.navigateTo({ url: `/pages/history-choice?course=${courseId.value}` })
}

function scrollToSection(i) {
  activeIndex.value = i
  // #ifdef H5
  const target = document.getElementById(`sec-${i}`)
  target?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  // #endif
  // #ifndef H5
  const query = uni.createSelectorQuery().in(instance)
  query.select(`#sec-${i}`).boundingClientRect()
  query.select('.scroll').scrollOffset()
  query.exec((res) => {
    const rect = res?.[0]
    const scroll = res?.[1]
    if (!rect || !scroll) return
    uni.pageScrollTo({ scrollTop: scroll.scrollTop + rect.top - 80, duration: 300 })
  })
  // #endif
}

function handleScroll() {
  const container = scrollEl || document.querySelector('.page-classroom .scroll')
  if (!container) return
  const threshold = container.clientHeight * 0.5
  const secs = container.querySelectorAll('[data-i]')
  let active = 0
  secs.forEach((sec, i) => {
    const top = sec.getBoundingClientRect().top - container.getBoundingClientRect().top
    if (top < threshold) active = i
  })
  activeIndex.value = active
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
</script>

<template>
  <view class="page-classroom">
    <view class="topbar">
      <view class="topbar-left">
        <button type="button" class="back" @click="goBack">← 返回首页</button>
        <text class="title">{{ courseTitle }}</text>
      </view>
    </view>

    <view class="body">
      <view class="timeline">
        <view class="timeline-label">课件时间线</view>
        <view
          v-for="(n, i) in nodes"
          :key="'tl-' + i"
          class="tl-node"
          :class="{ active: activeIndex === i, game: isGameNode(i) }"
          @click="scrollToSection(i)"
        >
          {{ n }}
        </view>
      </view>

      <view class="scroll">
        <view
          v-for="(sec, i) in sections"
          :key="'sec-' + i"
          :id="'sec-' + i"
          class="sec"
          :class="{ hero: sec.type === 'hero' }"
          :data-i="i"
        >
          <template v-if="sec.type === 'hero'">
            <view class="hero-h1">
              <text>{{ heroData.title }}</text>
              <text v-if="heroData.highlight" class="hero-highlight">{{ heroData.highlight }}</text>
            </view>
            <view class="hero-p">{{ heroData.sub }}</view>
          </template>

          <view v-else-if="sec.type === 'block'" class="block">
            <view class="block-h2">{{ sec.heading }}</view>
            <view
              v-for="(p, pi) in sec.paragraphs"
              :key="pi"
              class="block-p"
            >
              {{ p }}
            </view>
            <view v-if="sec.quote" class="quote">{{ sec.quote }}</view>
          </view>

          <view v-else-if="sec.type === 'video'" class="block">
            <view class="block-h2">{{ sec.heading }}</view>
            <view class="video-placeholder">{{ sec.placeholder }}</view>
          </view>

          <view v-else-if="sec.type === 'single-game'" class="game-card">
            <view class="game-card-h3">⚔️ 李大钊的历史抉择</view>
            <view class="game-card-p">课件到此节点，触发内置互动游戏。如果你是 1919 年的李大钊，你会如何选择？</view>
            <button type="button" class="game-btn" @click="openGame('default')">开始互动</button>
          </view>

          <view v-else-if="sec.type === 'dual-games'" class="game-grid">
            <view class="game-card game-card--battle">
              <text class="game-tag">互动游戏 ①</text>
              <view class="game-card-h3">⚔️ 历史抉择生成器</view>
              <view class="game-card-p">青春守初心 廉洁担使命 · 教师大屏投屏，带领全班体验刘启耀、张其德、毛泽民、何叔衡四条抉择线。</view>
              <button type="button" class="game-btn" @click="goHistoryChoice">教师大屏</button>
            </view>
            <view class="game-card game-card--script">
              <text class="game-tag">互动游戏 ②</text>
              <view class="game-card-h3">🎭 红色剧本杀</view>
              <view class="game-card-p">《苏区账目风波》· 13 人联机（1 教师 + 12 学生），读剧本、线索搜证、投票汇总。</view>
              <view class="game-card-hint">请先启动后端：server 目录 → python main.py</view>
              <view class="game-btn-row">
                <button type="button" class="game-btn" @click="goHost">教师大屏</button>
                <button type="button" class="game-btn game-btn--pink" @click="goRole">学生加入</button>
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

  .scroll {
    flex: 1;
    min-height: 0;
    height: auto;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
  }

  .game-card-hint {
    font-size: 12px;
    opacity: 0.7;
    margin-bottom: 16px;
    color: rgba(255, 255, 255, 0.65);
    text-align: center;
  }

  .game-btn-row {
    display: flex;
    gap: 10px;
    justify-content: center;
    flex-wrap: wrap;
  }

  .game-btn--pink {
    background: #ff8fab;
    color: #1a1a1a;
  }

  .clue-list {
    margin: 12px 0;
    padding-left: 0;
    list-style: none;
  }

  .clue-item {
    padding: 8px 12px;
    margin-bottom: 6px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 6px;
    font-size: 13px;
    color: rgba(255, 255, 255, 0.8);
  }

  .video-placeholder {
    opacity: 0.5;
    text-align: center;
    padding: 40px;
    border: 1px dashed rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    font-size: 16px;
    color: rgba(255, 255, 255, 0.75);
  }
}
</style>
