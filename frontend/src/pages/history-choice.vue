<script setup>
import { ref, computed, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { historyChoiceGame } from '../data/history-choice-data.js'
import { getSharedUrl } from '@/utils/config'

const courseId = ref('11')
const screen = ref('home') // home | select | play | ending
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

const STORAGE_KEY = 'history-choice-runs'

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

function goBackCourse() {
  uni.navigateBack()
}

function resetGame() {
  round.value = 1
  phase.value = 'story'
  r1Key.value = ''
  r2Key.value = ''
  r3Key.value = ''
  marks.value = []
  lastOption.value = null
}

function startSelect() {
  resetGame()
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
  if (phase.value !== 'options') return
  lastOption.value = opt
  marks.value[round.value - 1] = opt.mark || '摇摆'
  if (round.value === 1) r1Key.value = opt.key
  if (round.value === 2) r2Key.value = opt.key
  if (round.value === 3) r3Key.value = opt.key
  phase.value = 'deduction'
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
    <view class="hc-float-back" @click="goBackCourse">← 返回课件</view>
    <view class="hc-badge">教师大屏 · 历史抉择生成器</view>

    <!-- 主页 -->
    <view v-if="screen === 'home'" class="hc-home-shell">
      <view class="hc-stage hc-home-stage">
        <text class="hc-hero-title">{{ historyChoiceGame.title }}</text>
        <view class="hc-home-btns">
          <button type="button" class="hc-btn primary lg" @click="startSelect">开启游戏</button>
          <button type="button" class="hc-btn lg" @click="showAnnounce = true">游戏公告</button>
          <button type="button" class="hc-btn lg" @click="openHistory">历史结局</button>
        </view>
      </view>
    </view>

    <!-- 选角 -->
    <scroll-view v-else-if="screen === 'select'" scroll-y class="hc-scroll-stage">
      <view class="hc-stage">
        <text class="hc-section-title">选择扮演人物</text>
        <view class="hc-char-grid">
          <view
            v-for="c in historyChoiceGame.characters"
            :key="c.id"
            :class="['hc-char-card', selectedCharId === c.id ? 'selected' : '']"
            @click="selectedCharId = c.id"
          >
            <view class="hc-media-frame hc-media-compact hc-char-media">
              <image
                v-if="c.portrait"
                class="hc-media-img"
                :src="assetUrl(c.portrait)"
                mode="aspectFit"
              />
              <view v-else class="hc-media-fallback">{{ c.name.slice(0, 1) }}</view>
            </view>
            <view class="hc-char-info">
              <text class="hc-char-name">{{ c.name }}</text>
              <text class="hc-char-title">{{ c.title }}</text>
              <text class="hc-char-intro">{{ c.intro }}</text>
            </view>
          </view>
        </view>
        <view class="hc-action-bar">
          <button type="button" class="hc-btn" @click="screen = 'home'">返回</button>
          <button type="button" class="hc-btn primary" :disabled="!selectedCharId" @click="confirmCharacter">确定选择</button>
        </view>
      </view>
    </scroll-view>

    <!-- 抉择：上图下文，文字优先 -->
    <view v-else-if="screen === 'play' && character" class="hc-play-shell">
      <view class="hc-play-toolbar">
        <view class="hc-play-meta">
          <text class="hc-char-name">{{ character.name }}</text>
          <text class="hc-progress">{{ progressText }}</text>
        </view>
        <view class="hc-toolbar-actions">
          <button type="button" class="hc-btn ghost md" @click="showRewind = true">回溯</button>
        </view>
        <view class="hc-progress-track">
          <view class="hc-progress-fill" :style="{ width: progressPercent + '%' }" />
        </view>
      </view>

      <scroll-view scroll-y class="hc-scroll-stage hc-play-scroll">
        <view class="hc-stage hc-play-stage">
          <view
            class="hc-media-frame hc-media-hero hc-scene-frame clickable"
            @click="onPlayAreaTap"
          >
            <image
              v-if="playHeroImage"
              class="hc-media-img"
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
                  class="hc-option"
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
            class="hc-media-img"
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
          <view class="hc-action-bar inline">
            <button
              v-if="screen === 'history'"
              type="button"
              class="hc-btn"
              @click="screen = 'home'"
            >返回主页</button>
            <template v-else>
              <button type="button" class="hc-btn" @click="screen = 'home'; resetGame()">返回主页</button>
              <button type="button" class="hc-btn primary" @click="startSelect">再玩一次</button>
            </template>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- 历史结局为空 -->
    <view v-else-if="screen === 'history'" class="hc-stage hc-home-stage">
      <text class="hc-section-title">历史结局</text>
      <text class="hc-empty-block">暂无记录，完成一次抉择后将保存在本机</text>
      <view class="hc-action-bar">
        <button type="button" class="hc-btn primary" @click="screen = 'home'">返回主页</button>
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
.hc-host {
  height: 100vh;
  background: radial-gradient(ellipse at 50% 0%, #2a1215 0%, #0d0d12 55%);
  color: #f5e6d0;
  position: relative;
  padding: 24rpx 40rpx 32rpx;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.hc-scroll-stage {
  flex: 1;
  height: 0;
  width: 100%;
}

.hc-play-shell {
  flex: 1;
  height: 0;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.hc-play-scroll {
  flex: 1;
  height: 0;
}

.hc-float-back {
  position: fixed;
  top: 20rpx;
  left: 20rpx;
  z-index: 90;
  padding: 12rpx 28rpx;
  font-size: 26rpx;
  background: rgba(0, 0, 0, 0.55);
  border-radius: 12rpx;
}

.hc-badge {
  display: block;
  text-align: center;
  font-size: 26rpx;
  color: #d4a574;
  letter-spacing: 2rpx;
  margin-bottom: 12rpx;
  flex-shrink: 0;
}

.hc-stage {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  padding-bottom: 48rpx;
}

.hc-home-shell {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 0;
  width: 100%;
}

.hc-home-stage {
  padding: 40rpx 48rpx;
  text-align: center;
  width: 100%;
  max-width: 640px;
  margin: 0 auto;
}

.hc-hero-title {
  display: block;
  font-size: 72rpx;
  font-weight: 700;
  line-height: 1.45;
  margin-bottom: 56rpx;
}

.hc-home-btns {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 28rpx;
  max-width: 520px;
  margin: 0 auto;
}

.hc-home-btns .hc-btn {
  width: 100%;
  box-sizing: border-box;
}

.hc-section-title {
  display: block;
  text-align: center;
  font-size: 44rpx;
  font-weight: 700;
  margin: 16rpx 0 36rpx;
}

.hc-char-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 28rpx;
}

.hc-char-card {
  display: flex;
  flex-direction: column;
  border-radius: 20rpx;
  overflow: hidden;
  border: 2px solid rgba(212, 165, 116, 0.22);
  background: rgba(255, 255, 255, 0.04);
  transition: border-color 0.2s;
}

.hc-char-card.selected {
  border-color: #e05a5a;
  box-shadow: 0 0 0 2px rgba(224, 90, 90, 0.25);
}

.hc-media-frame {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  background: #120a08;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 选角页等：适中配图 */
.hc-media-compact {
  max-width: 100%;
  margin: 0 auto;
  aspect-ratio: 16 / 9;
  max-height: 32vh;
}

/* 剧情/推演/结局：占页面上半部分 */
.hc-media-hero {
  width: 100%;
  height: 50vh;
  min-height: 400px;
  aspect-ratio: unset;
  max-width: none;
  margin: 0 0 32rpx;
  border-radius: 16rpx;
  border: 1px solid rgba(212, 165, 116, 0.22);
}

.hc-media-img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: contain;
  object-position: center center;
}

.hc-media-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.35);
  font-size: 40rpx;
  font-weight: 700;
}

.hc-char-media {
  width: 100%;
  max-height: 28vh;
}

.hc-char-info {
  padding: 28rpx 32rpx 32rpx;
}

.hc-char-name {
  display: block;
  font-size: 40rpx;
  font-weight: 700;
  margin-bottom: 10rpx;
}

.hc-char-title {
  display: block;
  font-size: 28rpx;
  color: #d4a574;
  margin-bottom: 12rpx;
  line-height: 1.5;
}

.hc-char-intro {
  display: block;
  font-size: 30rpx;
  line-height: 1.75;
  opacity: 0.9;
}

.hc-action-bar {
  display: flex;
  gap: 24rpx;
  margin-top: 36rpx;
  justify-content: center;
}

.hc-action-bar.inline {
  margin-top: 32rpx;
  justify-content: flex-start;
}

.hc-btn {
  padding: 26rpx 48rpx;
  border-radius: 14rpx;
  border: 1px solid rgba(212, 165, 116, 0.35);
  background: rgba(255, 255, 255, 0.06);
  color: #f5e6d0;
  font-size: 34rpx;
}

.hc-btn.primary {
  background: linear-gradient(135deg, #8b3a3a, #c45c5c);
  border-color: transparent;
  color: #fff;
}

.hc-btn.ghost {
  background: transparent;
}

.hc-btn.lg {
  min-width: 280rpx;
  padding: 30rpx 56rpx;
  font-size: 38rpx;
}

.hc-btn.md {
  padding: 20rpx 36rpx;
  font-size: 32rpx;
}

.hc-btn.xl {
  min-width: 360rpx;
  padding: 36rpx 72rpx;
  font-size: 40rpx;
}

.hc-btn.sm {
  padding: 16rpx 32rpx;
  font-size: 30rpx;
}

.hc-btn[disabled] {
  opacity: 0.4;
}

.hc-play-toolbar {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 12rpx 24rpx;
  align-items: center;
  margin-bottom: 20rpx;
  flex-shrink: 0;
  max-width: 1200px;
  width: 100%;
  margin-left: auto;
  margin-right: auto;
}

.hc-toolbar-actions {
  display: flex;
  gap: 16rpx;
  align-items: center;
}

.hc-play-meta {
  display: flex;
  align-items: baseline;
  gap: 24rpx;
  flex-wrap: wrap;
}

.hc-play-meta .hc-char-name {
  font-size: 44rpx;
  font-weight: 700;
}

.hc-progress {
  font-size: 36rpx;
  opacity: 0.75;
}

.hc-progress-track {
  grid-column: 1 / -1;
  height: 10rpx;
  border-radius: 5rpx;
  background: rgba(255, 255, 255, 0.1);
  overflow: hidden;
}

.hc-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #8b3a3a, #e05a5a);
  transition: width 0.35s ease;
}

.hc-play-stage {
  padding-top: 8rpx;
}

.hc-scene-frame,
.hc-ending-frame {
  margin-bottom: 32rpx;
}

.hc-block-label {
  display: block;
  font-size: 34rpx;
  color: #d4a574;
  margin-bottom: 24rpx;
  letter-spacing: 4rpx;
  font-weight: 600;
}

.hc-content-box,
.hc-story-box,
.hc-options-box {
  padding: 40rpx 44rpx;
  border-radius: 20rpx;
  background: rgba(0, 0, 0, 0.38);
  border: 1px solid rgba(212, 165, 116, 0.2);
  margin-bottom: 28rpx;
}

.hc-content-box.flat,
.hc-story-box.flat {
  margin-bottom: 24rpx;
}

.clickable {
  cursor: pointer;
}

.hc-story-text {
  display: block;
  font-size: 44rpx;
  line-height: 2;
  text-align: justify;
  letter-spacing: 1rpx;
}

.hc-options-stack {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.hc-option-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.hc-option {
  display: flex;
  gap: 24rpx;
  align-items: flex-start;
  width: 100%;
  text-align: left;
  padding: 32rpx 36rpx;
  border-radius: 16rpx;
  border: 1px solid rgba(212, 165, 116, 0.3);
  background: rgba(255, 255, 255, 0.06);
  color: #f5e6d0;
}

.hc-option-key {
  flex-shrink: 0;
  width: 64rpx;
  height: 64rpx;
  line-height: 64rpx;
  text-align: center;
  border-radius: 12rpx;
  background: rgba(139, 58, 58, 0.65);
  font-weight: 700;
  font-size: 36rpx;
}

.hc-option-text {
  flex: 1;
  font-size: 40rpx;
  line-height: 1.8;
}

.hc-ending-stage {
  padding-top: 16rpx;
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
  font-size: 60rpx;
  font-weight: 700;
  color: #ffd166;
  margin-bottom: 20rpx;
}

.hc-ending-char {
  display: block;
  font-size: 40rpx;
  margin-bottom: 28rpx;
  opacity: 0.88;
}

.hc-ending-text,
.hc-ending-global {
  display: block;
  font-size: 42rpx;
  line-height: 2;
  margin-bottom: 28rpx;
  padding: 32rpx 36rpx;
  border-radius: 16rpx;
  background: rgba(255, 255, 255, 0.05);
  text-align: justify;
}

.hc-choice-recap {
  font-size: 36rpx;
  opacity: 0.8;
  margin-bottom: 12rpx;
}

.hc-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.65);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 32rpx;
}

.hc-modal-box {
  width: 100%;
  max-width: 800px;
  max-height: 80vh;
  overflow: auto;
  padding: 40rpx;
  border-radius: 20rpx;
  background: #1f1410;
  border: 1px solid rgba(212, 165, 116, 0.25);
}

.hc-modal-box.wide {
  max-width: 960px;
}

.hc-modal-title {
  display: block;
  font-size: 38rpx;
  font-weight: 700;
  margin-bottom: 24rpx;
}

.hc-modal-body {
  display: block;
  font-size: 32rpx;
  line-height: 1.85;
  margin-bottom: 28rpx;
}

.hc-history-list {
  max-height: 480rpx;
  margin-bottom: 20rpx;
}

.hc-history-item {
  padding: 18rpx 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.hc-history-meta {
  display: block;
  font-size: 26rpx;
  opacity: 0.6;
}

.hc-history-ending {
  display: block;
  font-size: 30rpx;
  margin-top: 8rpx;
}

.hc-empty {
  font-size: 30rpx;
  opacity: 0.6;
  padding: 24rpx 0;
}

.hc-rewind-item {
  display: block;
  width: 100%;
  text-align: left;
  padding: 24rpx;
  margin-bottom: 14rpx;
  border-radius: 12rpx;
  border: 1px solid rgba(212, 165, 116, 0.2);
  background: rgba(255, 255, 255, 0.04);
  color: #f5e6d0;
  font-size: 30rpx;
}

/* 投屏大屏进一步放大字号 */
@media (min-width: 1200px) {
  .hc-media-hero {
    height: 52vh;
    min-height: 420px;
  }

  .hc-story-text {
    font-size: 36px;
    line-height: 1.95;
  }

  .hc-option-text {
    font-size: 32px;
    line-height: 1.75;
  }

  .hc-option-key {
    width: 52px;
    height: 52px;
    line-height: 52px;
    font-size: 28px;
  }

  .hc-block-label {
    font-size: 26px;
  }

  .hc-play-meta .hc-char-name {
    font-size: 32px;
  }

  .hc-progress {
    font-size: 28px;
  }

  .hc-btn {
    font-size: 28px;
  }

  .hc-btn.xl {
    font-size: 34px;
    min-width: 280px;
    padding: 22px 56px;
  }

  .hc-btn.md {
    font-size: 26px;
  }

  .hc-char-intro {
    font-size: 24px;
  }

  .hc-char-name {
    font-size: 30px;
  }

  .hc-char-title {
    font-size: 22px;
  }

  .hc-ending-text,
  .hc-ending-global {
    font-size: 32px;
  }

  .hc-ending-badge {
    font-size: 44px;
  }

  .hc-section-title {
    font-size: 40px;
  }

  .hc-hero-title {
    font-size: 52px;
  }
}

@media (max-width: 900px) {
  .hc-char-grid {
    grid-template-columns: 1fr;
  }
}
</style>
