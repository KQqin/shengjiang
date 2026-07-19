<script setup>
import { ref, computed, onMounted } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import { historyChoiceGame } from '../data/history-choice-data.js'
import { getSharedUrl } from '@/utils/config'
import { restoreTeachingFullscreen } from '@/utils/teaching-fullscreen.js'

const courseId = ref('11')
const screen = ref('select') // select | play | ending | history
const selectedCharId = ref('')
const round = ref(1)
const phase = ref('story') // story | options | deduction
const r1Key = ref('')
const r2Key = ref('')
const r3Key = ref('')
const marks = ref([])
const lastOption = ref(null)
const showAnnounce = ref(false)
const showRewind = ref(false)
const savedRuns = ref([])
const historyIndex = ref(0)
const pickingOptionKey = ref('')
const optionLocked = ref(false)

const OPTION_PICK_DELAY = 680

const STORAGE_KEY = 'history-choice-runs'
const SEAL_NUMS = ['壹', '贰', '叁', '肆']

function charSeal(index) {
  return SEAL_NUMS[index] || String(index + 1)
}

function assetUrl(path) {
  if (!path) return ''
  return getSharedUrl(path.replace(/^shared\//, ''))
}

const character = computed(() =>
  historyChoiceGame.characters.find((c) => c.id === selectedCharId.value),
)

const progressText = computed(() => `第 ${round.value} 题 / 共 3 题`)
const progressPercent = computed(() => Math.round((round.value / 3) * 100))

const currentBlock = computed(() => {
  if (!character.value) return null
  if (round.value === 1) return character.value.round1
  if (round.value === 2) return character.value.round2[r1Key.value] || null
  const nodeId = character.value.round2[r1Key.value]?.options?.find((o) => o.key === r2Key.value)?.node
  return character.value.round3[nodeId] || null
})

const currentStory = computed(() => currentBlock.value?.story || '')

const currentSceneImage = computed(() => assetUrl(currentBlock.value?.sceneImage))

const currentOptions = computed(() => {
  if (!character.value || phase.value !== 'options') return []
  return currentBlock.value?.options || []
})

const deductionText = computed(() => lastOption.value?.deduction || '')
const deductionImage = computed(() => assetUrl(lastOption.value?.deductionImage))

const playHeroImage = computed(() => {
  if (phase.value === 'deduction') {
    return deductionImage.value || currentSceneImage.value
  }
  return currentSceneImage.value
})

const checkpoints = computed(() => {
  const list = [{ id: 'r1-story', label: '第1轮 · 剧情', round: 1, phase: 'story' }]
  if (r1Key.value) {
    list.push({ id: 'r1-done', label: `第1轮 · 已选 ${r1Key.value}`, round: 1, phase: 'done' })
    list.push({ id: 'r2-story', label: '第2轮 · 剧情', round: 2, phase: 'story' })
  }
  if (r2Key.value) {
    list.push({ id: 'r2-done', label: `第2轮 · 已选 ${r2Key.value}`, round: 2, phase: 'done' })
    list.push({ id: 'r3-story', label: '第3轮 · 剧情', round: 3, phase: 'story' })
  }
  if (r3Key.value) {
    list.push({ id: 'r3-done', label: `第3轮 · 已选 ${r3Key.value}`, round: 3, phase: 'done' })
  }
  return list
})

const endingId = computed(() => {
  const bad = marks.value.filter((m) => m === '失范').length
  const sway = marks.value.filter((m) => m === '摇摆').length
  if (bad >= 2) return '初心失守者'
  if (bad === 0 && sway === 0) return '赤胆守廉者'
  if (bad === 0 && sway === 1) return '迷途知返者'
  return '底线摇摆者'
})

const endingRule = computed(() =>
  character.value?.endingRules?.find((e) => e.id === endingId.value),
)

const endingSummary = computed(() => endingRule.value?.summary || '')
const endingImage = computed(() => assetUrl(endingRule.value?.image))
const endingGlobal = computed(() => historyChoiceGame.globalEndings[endingId.value] || '')

function findCharacterByRun(run) {
  if (!run) return null
  return historyChoiceGame.characters.find(
    (c) => c.id === run.characterId || c.name === run.character,
  )
}

const activeHistoryRun = computed(() => savedRuns.value[historyIndex.value] || null)

const viewCharacter = computed(() => {
  if (screen.value === 'history') return findCharacterByRun(activeHistoryRun.value)
  return character.value
})

const viewEndingId = computed(() => {
  if (screen.value === 'history') return activeHistoryRun.value?.ending || ''
  return endingId.value
})

const viewEndingRule = computed(() =>
  viewCharacter.value?.endingRules?.find((e) => e.id === viewEndingId.value),
)

const viewEndingSummary = computed(() => viewEndingRule.value?.summary || '')

const viewEndingImage = computed(() => {
  const img = viewEndingRule.value?.image
  if (img) return assetUrl(img)
  return assetUrl(viewCharacter.value?.portrait)
})

const viewEndingGlobal = computed(() => historyChoiceGame.globalEndings[viewEndingId.value] || '')

const viewChoicesRecap = computed(() => {
  if (screen.value === 'history') {
    const c = activeHistoryRun.value?.choices || []
    return `本轮选择：第1轮 ${c[0] || '—'} · 第2轮 ${c[1] || '—'} · 第3轮 ${c[2] || '—'}`
  }
  return `本轮选择：第1轮 ${r1Key.value} · 第2轮 ${r2Key.value} · 第3轮 ${r3Key.value}`
})

const historyNavText = computed(() => {
  if (!savedRuns.value.length) return ''
  const run = activeHistoryRun.value
  return `${formatTime(run?.at)} · ${historyIndex.value + 1} / ${savedRuns.value.length}`
})

onLoad((q) => {
  if (q?.course) courseId.value = String(q.course)
})

onMounted(() => {
  try {
    const raw = uni.getStorageSync(STORAGE_KEY)
    savedRuns.value = raw ? JSON.parse(raw) : []
  } catch {
    savedRuns.value = []
  }
})

onShow(() => {
  restoreTeachingFullscreen()
})

function goBackCourse() {
  const pages = getCurrentPages()
  if (pages.length > 1) {
    uni.navigateBack()
    return
  }
  uni.redirectTo({ url: `/pages/classroom?course=${courseId.value}` })
}

function resetGame() {
  round.value = 1
  phase.value = 'story'
  r1Key.value = ''
  r2Key.value = ''
  r3Key.value = ''
  marks.value = []
  lastOption.value = null
  pickingOptionKey.value = ''
  optionLocked.value = false
}

function goToSelect() {
  resetGame()
  selectedCharId.value = ''
  screen.value = 'select'
}

function confirmCharacter() {
  if (!selectedCharId.value) return
  resetGame()
  screen.value = 'play'
}

function onStoryTap() {
  if (phase.value === 'story') phase.value = 'options'
}

function onPlayAreaTap() {
  if (phase.value === 'story') onStoryTap()
  else if (phase.value === 'deduction') nextFromDeduction()
}

function chooseOption(opt) {
  if (phase.value !== 'options' || optionLocked.value) return
  optionLocked.value = true
  pickingOptionKey.value = opt.key

  setTimeout(() => {
    lastOption.value = opt
    marks.value[round.value - 1] = opt.mark || '摇摆'
    if (round.value === 1) r1Key.value = opt.key
    if (round.value === 2) r2Key.value = opt.key
    if (round.value === 3) r3Key.value = opt.key
    pickingOptionKey.value = ''
    optionLocked.value = false
    phase.value = 'deduction'
  }, OPTION_PICK_DELAY)
}

function nextFromDeduction() {
  if (round.value >= 3) {
    finishGame()
    return
  }
  round.value += 1
  phase.value = 'story'
  lastOption.value = null
}

function finishGame() {
  const run = {
    at: Date.now(),
    characterId: character.value?.id,
    character: character.value?.name,
    ending: endingId.value,
    choices: [r1Key.value, r2Key.value, r3Key.value],
    marks: [...marks.value],
  }
  savedRuns.value = [run, ...savedRuns.value].slice(0, 30)
  uni.setStorageSync(STORAGE_KEY, JSON.stringify(savedRuns.value))
  screen.value = 'ending'
}

function openHistory() {
  historyIndex.value = 0
  screen.value = 'history'
}

function prevHistory() {
  if (historyIndex.value > 0) historyIndex.value -= 1
}

function nextHistory() {
  if (historyIndex.value < savedRuns.value.length - 1) historyIndex.value += 1
}

function rewindTo(cp) {
  if (cp.round === 1 && cp.phase === 'story') {
    resetGame()
  } else if (cp.round === 1 && cp.phase === 'done') {
    round.value = 1
    phase.value = 'deduction'
    r2Key.value = ''
    r3Key.value = ''
    marks.value = marks.value.slice(0, 1)
    lastOption.value = character.value.round1.options.find((o) => o.key === r1Key.value) || null
  } else if (cp.round === 2 && cp.phase === 'story') {
    round.value = 2
    phase.value = 'story'
    r2Key.value = ''
    r3Key.value = ''
    marks.value = marks.value.slice(0, 1)
    lastOption.value = null
  } else if (cp.round === 2 && cp.phase === 'done') {
    round.value = 2
    phase.value = 'deduction'
    r3Key.value = ''
    marks.value = marks.value.slice(0, 2)
    lastOption.value = character.value.round2[r1Key.value]?.options?.find((o) => o.key === r2Key.value) || null
  } else if (cp.round === 3 && cp.phase === 'story') {
    round.value = 3
    phase.value = 'story'
    r3Key.value = ''
    marks.value = marks.value.slice(0, 2)
    lastOption.value = null
  }
  showRewind.value = false
  screen.value = 'play'
}

function formatTime(ts) {
  const d = new Date(ts)
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}
</script>

<template>
  <view class="hc-host">
    <view class="hc-topbar">
      <view class="hc-float-back" @click="goBackCourse">← 返回课件</view>
      <text class="hc-badge">教师大屏 · 历史抉择</text>
      <view class="hc-topbar-spacer" />
    </view>

    <!-- 选角 -->
    <view v-if="screen === 'select'" class="hc-select-shell">
      <view class="hc-stage hc-stage--select">
        <text class="hc-page-title">选择扮演人物</text>
        <view class="hc-char-grid">
          <view
            v-for="(c, ci) in historyChoiceGame.characters"
            :key="c.id"
            :class="['hc-char-card', selectedCharId === c.id ? 'selected' : '']"
            @click="selectedCharId = c.id"
          >
            <view class="hc-char-media">
              <image
                v-if="c.portrait"
                class="hc-media-img hc-media-img--contain"
                :src="assetUrl(c.portrait)"
                mode="aspectFit"
              />
              <view v-else class="hc-media-fallback">{{ c.name.slice(0, 1) }}</view>
              <view class="hc-char-seal-badge">{{ charSeal(ci) }}</view>
            </view>
            <view class="hc-char-info">
              <text class="hc-char-name">{{ c.name }}</text>
              <text class="hc-char-title">{{ c.title }}</text>
              <text class="hc-char-intro">{{ c.intro }}</text>
            </view>
          </view>
        </view>
        <view class="hc-action-bar hc-action-bar--select">
          <button type="button" class="hc-btn hc-btn-stele" @click="goBackCourse">返回</button>
          <button type="button" class="hc-btn hc-btn-stele" @click="openHistory">历史结局</button>
          <button type="button" class="hc-btn hc-btn-stele primary" :disabled="!selectedCharId" @click="confirmCharacter">
            确定选择<text class="hc-btn-chevron">›</text>
          </button>
        </view>
      </view>
    </view>

    <!-- 抉择 -->
    <view v-else-if="screen === 'play' && character" class="hc-play-shell hc-play-shell--full">
      <view class="hc-play-main">
        <view class="hc-play-toolbar">
          <view class="hc-play-meta">
            <text class="hc-char-name">{{ character.name }}</text>
            <text class="hc-progress">{{ progressText }} · 第{{ ['壹', '贰', '叁'][round - 1] || round }}轮</text>
          </view>
          <button type="button" class="hc-btn hc-btn-stele hc-btn-stele--compact" @click="showRewind = true">回溯</button>
          <view class="hc-progress-track">
            <view class="hc-progress-fill" :style="{ width: progressPercent + '%' }" />
          </view>
        </view>

        <scroll-view scroll-y class="hc-play-scroll hc-scroll-stage">
          <view class="hc-stage hc-play-stage">
            <view class="hc-media-hero hc-scene-frame clickable" @click="onPlayAreaTap">
              <image
                v-if="playHeroImage"
                class="hc-media-img hc-media-img--contain"
                :src="playHeroImage"
                mode="aspectFit"
              />
              <view v-else class="hc-media-fallback">场景插图</view>
            </view>

            <view v-if="phase === 'story'" class="hc-content-box clickable" @click="onStoryTap">
              <text class="hc-story-text">{{ currentStory }}</text>
            </view>

            <view v-else-if="phase === 'options'" class="hc-options-stack" @click.stop>
              <view class="hc-content-box flat">
                <text class="hc-story-text">{{ currentStory }}</text>
              </view>
              <view class="hc-options-box">
                <text class="hc-block-label">请选择</text>
                <view class="hc-option-list">
                  <button
                    v-for="opt in currentOptions"
                    :key="opt.key"
                    type="button"
                    :class="[
                      'hc-option',
                      pickingOptionKey === opt.key ? 'picked' : '',
                      pickingOptionKey && pickingOptionKey !== opt.key ? 'dimmed' : '',
                    ]"
                    :disabled="optionLocked"
                    @click="chooseOption(opt)"
                  >
                    <text class="hc-option-key">{{ opt.key }}</text>
                    <text class="hc-option-text">{{ opt.text }}</text>
                  </button>
                </view>
              </view>
            </view>

            <view v-else-if="phase === 'deduction'" class="hc-content-box clickable" @click="nextFromDeduction">
              <text class="hc-story-text">{{ deductionText }}</text>
            </view>
          </view>
        </scroll-view>
      </view>
    </view>

    <!-- 结局 / 历史结局（同一套展示） -->
    <scroll-view
      v-else-if="(screen === 'ending' && character) || (screen === 'history' && viewCharacter)"
      scroll-y
      class="hc-scroll-stage"
    >
      <view class="hc-stage hc-ending-stage">
        <view v-if="screen === 'history' && savedRuns.length > 1" class="hc-history-nav">
          <button type="button" class="hc-btn sm" :disabled="historyIndex <= 0" @click="prevHistory">上一条</button>
          <text class="hc-history-nav-text">{{ historyNavText }}</text>
          <button
            type="button"
            class="hc-btn sm"
            :disabled="historyIndex >= savedRuns.length - 1"
            @click="nextHistory"
          >下一条</button>
        </view>
        <view v-else-if="screen === 'history'" class="hc-history-nav single">
          <text class="hc-history-nav-text">{{ historyNavText }}</text>
        </view>

        <view class="hc-media-frame hc-media-hero hc-ending-frame">
          <image
            v-if="viewEndingImage"
            class="hc-media-img hc-media-img--contain"
            :src="viewEndingImage"
            mode="aspectFit"
          />
          <view v-else class="hc-media-fallback">结局插图</view>
        </view>
        <view class="hc-ending-copy">
          <text class="hc-ending-badge">【{{ viewEndingId }}】</text>
          <text class="hc-ending-char">{{ viewCharacter.name }} · 专属总结</text>
          <text class="hc-ending-text">{{ viewEndingSummary }}</text>
          <text class="hc-ending-global">{{ viewEndingGlobal }}</text>
          <view class="hc-choice-recap">
            <text>{{ viewChoicesRecap }}</text>
          </view>
          <view class="hc-action-bar inline hc-action-bar--ending">
            <button
              v-if="screen === 'history'"
              type="button"
              class="hc-btn hc-btn-stele"
              @click="goToSelect"
            >返回选角</button>
            <template v-else>
              <button type="button" class="hc-btn hc-btn-stele" @click="goToSelect">返回选角</button>
              <button type="button" class="hc-btn hc-btn-stele primary" @click="goToSelect">
                再玩一次<text class="hc-btn-chevron">›</text>
              </button>
            </template>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- 历史结局为空 -->
    <view v-else-if="screen === 'history'" class="hc-stage hc-home-stage">
      <text class="hc-section-title">历史结局</text>
      <text class="hc-empty-block">暂无记录，完成一次抉择后将保存在本机</text>
      <view class="hc-action-bar hc-action-bar--ending">
        <button type="button" class="hc-btn hc-btn-stele" @click="goToSelect">返回选角</button>
      </view>
    </view>

    <!-- 公告 -->
    <view v-if="showAnnounce" class="hc-modal" @click="showAnnounce = false">
      <view class="hc-modal-box" @click.stop>
        <text class="hc-modal-title">游戏公告</text>
        <text class="hc-modal-body">{{ historyChoiceGame.announcement }}</text>
        <button type="button" class="hc-btn primary" @click="showAnnounce = false">知道了</button>
      </view>
    </view>

    <!-- 回溯 -->
    <view v-if="showRewind" class="hc-modal" @click="showRewind = false">
      <view class="hc-modal-box" @click.stop>
        <text class="hc-modal-title">回溯到先前节点</text>
        <button
          v-for="cp in checkpoints"
          :key="cp.id"
          type="button"
          class="hc-rewind-item"
          @click="rewindTo(cp)"
        >{{ cp.label }}</button>
        <button type="button" class="hc-btn" @click="showRewind = false">取消</button>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
@import '../styles/history-choice-theme.scss';

.hc-section-title {
  display: block;
  text-align: center;
  font-family: var(--hc-font-display);
  font-size: 44rpx;
  color: #d4563a;
  margin: 16rpx 0 36rpx;
  letter-spacing: 0.12em;
}

.hc-action-bar.inline {
  margin-top: 32rpx;
  justify-content: flex-start;
}

.hc-action-bar.inline .hc-btn-stele {
  flex: 1;
  min-width: 0;
  max-width: 420rpx;
}

.hc-home-stage {
  padding: 40rpx 48rpx;
  text-align: center;
  max-width: 640px;
  margin: 0 auto;
}

.hc-ending-stage {
  padding-top: 16rpx;
}

.hc-media-frame.hc-ending-frame,
.hc-ending-frame {
  width: 100%;
  height: 46vh;
  min-height: 360px;
  margin-bottom: 28rpx;
  padding: 8rpx;
  background: linear-gradient(145deg, rgba(92, 99, 104, 0.4), rgba(58, 64, 68, 0.6));
  border: 3px solid var(--hc-stone);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}

.hc-history-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24rpx;
  margin-bottom: 24rpx;
  flex-wrap: wrap;
}

.hc-history-nav.single {
  justify-content: flex-start;
}

.hc-history-nav-text {
  font-size: 28rpx;
  opacity: 0.75;
}

.hc-empty-block {
  display: block;
  text-align: center;
  font-size: 32rpx;
  opacity: 0.65;
  margin: 48rpx 0;
}

.hc-ending-copy {
  margin-top: 8rpx;
}

.hc-ending-badge {
  display: block;
  font-family: var(--hc-font-display);
  font-size: 56rpx;
  color: var(--hc-gold);
  margin-bottom: 20rpx;
}

.hc-ending-char {
  display: block;
  font-size: 38rpx;
  margin-bottom: 28rpx;
  opacity: 0.88;
}

.hc-ending-text,
.hc-ending-global {
  display: block;
  font-size: 38rpx;
  line-height: 2;
  margin-bottom: 28rpx;
  padding: 32rpx 36rpx;
  background:
    var(--hc-parchment-noise),
    rgba(26, 16, 14, 0.75);
  border: 2px solid rgba(92, 99, 104, 0.45);
  text-align: justify;
}

.hc-choice-recap {
  font-size: 32rpx;
  opacity: 0.8;
  margin-bottom: 12rpx;
}

.hc-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.72);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 300;
  padding: 32rpx;
}

.hc-modal-box {
  width: 100%;
  max-width: 800px;
  max-height: 80vh;
  overflow: auto;
  padding: 40rpx;
  background:
    var(--hc-parchment-noise),
    linear-gradient(180deg, rgba(232, 220, 200, 0.1) 0%, rgba(26, 16, 14, 0.95) 100%);
  border: 2px solid rgba(197, 160, 89, 0.35);
}

.hc-modal-title {
  display: block;
  font-family: var(--hc-font-display);
  font-size: 36rpx;
  color: var(--hc-title-red);
  margin-bottom: 24rpx;
}

.hc-modal-body {
  display: block;
  font-size: 30rpx;
  line-height: 1.85;
  margin-bottom: 28rpx;
  color: var(--hc-text-muted);
}

.hc-rewind-item {
  display: block;
  width: 100%;
  text-align: left;
  padding: 24rpx;
  margin-bottom: 14rpx;
  border: 1px solid rgba(197, 160, 89, 0.25);
  background: rgba(74, 18, 14, 0.25);
  color: var(--hc-text);
  font-size: 28rpx;
}
</style>
