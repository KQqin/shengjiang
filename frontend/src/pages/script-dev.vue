<script setup>
import { ref, computed, onMounted } from 'vue'
import { getSharedUrl } from '@/utils/config'
import { buildPlayerContent } from '@/utils/script-content'

const scriptData = ref(null)
const roleIndex = ref(0)
const phaseIndex = ref(0)
const currentTab = ref('public')

const tabs = [
  { key: 'public', label: '公开身份' },
  { key: 'script', label: '个人剧本' },
  { key: 'secret', label: '本场任务' },
  { key: 'clue1', label: '线索 ①' },
  { key: 'clue2', label: '线索 ②' },
  { key: 'vote', label: '投票' },
  { key: 'reveal', label: '揭晓' },
]

const currentRole = computed(() => scriptData.value?.roles?.[roleIndex.value])
const currentPhase = computed(() => scriptData.value?.phases?.[phaseIndex.value])

const playerContent = computed(() => {
  if (!scriptData.value || !currentRole.value) return null
  return buildPlayerContent(currentRole.value, phaseIndex.value, scriptData.value)
})

const unlocked = computed(() => playerContent.value?.unlocked || [])
const isTabLocked = (key) => !unlocked.value.includes(key)

const contentHtml = computed(() => {
  const c = playerContent.value
  if (!c) return { type: 'wait', text: '加载中…' }

  const u = c.unlocked || []
  if (currentTab.value === 'public' && u.includes('public')) {
    return { type: 'public', data: c.public }
  }
  if (currentTab.value === 'script' && u.includes('script')) {
    return { type: 'script', paragraphs: c.personalScript || [] }
  }
  if (currentTab.value === 'secret' && u.includes('secret')) {
    return { type: 'secret', tasks: c.secretTasks || [] }
  }
  if (currentTab.value === 'clue1' && u.includes('clue1')) {
    return { type: 'clue', title: '私人线索 ①', text: c.clue1 }
  }
  if (currentTab.value === 'clue2' && u.includes('clue2')) {
    return { type: 'clue', title: '私人线索 ②', text: c.clue2 }
  }
  if (currentTab.value === 'vote' && u.includes('vote')) {
    return { type: 'vote', fields: c.voteForm?.fields || [] }
  }
  if (currentTab.value === 'reveal' && u.includes('reveal')) {
    return { type: 'reveal', data: c.truth }
  }
  return { type: 'locked' }
})

onMounted(async () => {
  const res = await uni.request({ url: getSharedUrl('script-data.json') })
  scriptData.value = res.data
})

function switchTab(key) {
  if (isTabLocked(key)) return
  currentTab.value = key
}

function onRoleChange(e) {
  roleIndex.value = Number(e.detail.value)
}

function onPhaseChange(e) {
  phaseIndex.value = Number(e.detail.value)
}

function goBack() {
  uni.navigateBack()
}
</script>

<template>
  <view class="dev-page">
    <view class="header">
      <text class="back" @click="goBack">← 返回</text>
      <text class="title">🧪 角色预览 · 开发者模式</text>
      <text class="subtitle">无需联机，单独预览 12 个角色在各环节的手机端内容</text>
    </view>

    <view class="pickers">
      <view class="picker-row">
        <text class="picker-label">角色</text>
        <picker
          :range="scriptData?.roles || []"
          range-key="name"
          :value="roleIndex"
          @change="onRoleChange"
        >
          <view class="picker-value">{{ currentRole?.name || '选择角色' }}</view>
        </picker>
      </view>
      <view class="picker-row">
        <text class="picker-label">环节</text>
        <picker
          :range="scriptData?.phases || []"
          range-key="name"
          :value="phaseIndex"
          @change="onPhaseChange"
        >
          <view class="picker-value">{{ currentPhase?.name || '选择环节' }}</view>
        </picker>
      </view>
    </view>

    <view class="preview-badge">预览：{{ currentRole?.name }} · 第 {{ phaseIndex }} 环节</view>

    <view class="tabs">
      <text
        v-for="tab in tabs"
        :key="tab.key"
        :class="['tab', currentTab === tab.key ? 'active' : '', isTabLocked(tab.key) ? 'locked' : '']"
        @click="switchTab(tab.key)"
      >{{ tab.label }}</text>
    </view>

    <view class="content-card">
      <template v-if="contentHtml.type === 'public'">
        <text class="h2">{{ contentHtml.data.name }}</text>
        <text class="meta">{{ contentHtml.data.gender }} · {{ contentHtml.data.title }}</text>
        <text class="tag">{{ contentHtml.data.tag }}</text>
        <text class="p"><text class="bold">公开介绍：</text>{{ contentHtml.data.publicIntro }}</text>
      </template>

      <template v-else-if="contentHtml.type === 'script'">
        <text class="h2">个人剧本</text>
        <text v-for="(para, i) in contentHtml.paragraphs" :key="i" class="p">{{ para }}</text>
      </template>

      <template v-else-if="contentHtml.type === 'secret'">
        <text class="h2">本场任务</text>
        <text v-for="(task, i) in contentHtml.tasks" :key="i" class="p">{{ i + 1 }}. {{ task }}</text>
      </template>

      <template v-else-if="contentHtml.type === 'clue'">
        <text class="h2">{{ contentHtml.title }}</text>
        <text class="p">{{ contentHtml.text }}</text>
      </template>

      <template v-else-if="contentHtml.type === 'vote'">
        <text class="h2">填写推理结论</text>
        <view v-for="field in contentHtml.fields" :key="field.key" class="vote-field-preview">
          <text class="vote-field-label">{{ field.label }}</text>
          <view class="vote-field-placeholder">{{ field.placeholder }}</view>
        </view>
      </template>

      <template v-else-if="contentHtml.type === 'reveal'">
        <text class="h2">真相揭晓</text>
        <text class="p">{{ contentHtml.data.summary }}</text>
        <text v-for="(item, i) in contentHtml.data.timeline" :key="i" class="timeline-item">{{ item }}</text>
        <text class="moral">{{ contentHtml.data.moral }}</text>
      </template>

      <text v-else-if="contentHtml.type === 'locked'" class="muted">🔒 该内容在本环节尚未解锁</text>
      <text v-else class="muted">{{ contentHtml.text }}</text>
    </view>

    <text class="notice">此页面仅用于 UI 开发预览，不影响真实联机房间。</text>
  </view>
</template>

<style scoped lang="scss">
.dev-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #1a0a0a, #0d0d12);
  color: #fff;
  padding: 24rpx;
  padding-bottom: 48rpx;
}

.header {
  margin-bottom: 24rpx;
}

.back {
  display: block;
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.85);
  margin-bottom: 12rpx;
}

.title {
  display: block;
  font-size: 34rpx;
  color: #ffd166;
  font-weight: 700;
}

.subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.45);
  line-height: 1.6;
}

.pickers {
  margin-bottom: 20rpx;
}

.picker-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 12rpx;
}

.picker-label {
  width: 80rpx;
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.55);
}

.picker-value {
  flex: 1;
  padding: 20rpx 24rpx;
  border-radius: 12rpx;
  background: #16161f;
  border: 1px solid rgba(255, 209, 102, 0.25);
  font-size: 28rpx;
}

.preview-badge {
  display: inline-block;
  margin-bottom: 16rpx;
  padding: 8rpx 20rpx;
  border-radius: 20rpx;
  background: rgba(255, 209, 102, 0.15);
  color: #ffd166;
  font-size: 22rpx;
}

.tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-bottom: 16rpx;
}

.tab {
  padding: 12rpx 24rpx;
  border-radius: 24rpx;
  border: 1px solid rgba(255, 255, 255, 0.15);
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.5);
}

.tab.active {
  background: #e84855;
  border-color: #e84855;
  color: #fff;
}

.tab.locked {
  opacity: 0.35;
}

.content-card {
  padding: 32rpx;
  background: #16161f;
  border-radius: 20rpx;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.h2 {
  display: block;
  font-size: 34rpx;
  font-weight: 700;
  margin-bottom: 12rpx;
}

.meta, .p, .muted {
  display: block;
  font-size: 26rpx;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.65);
  margin-bottom: 12rpx;
}

.tag {
  display: inline-block;
  font-size: 22rpx;
  padding: 6rpx 16rpx;
  border-radius: 20rpx;
  background: rgba(232, 72, 85, 0.2);
  margin-bottom: 16rpx;
}

.vote-field-preview {
  margin-bottom: 20rpx;
}

.vote-field-label {
  display: block;
  font-size: 26rpx;
  color: #ffd166;
  margin-bottom: 8rpx;
}

.vote-field-placeholder {
  padding: 20rpx;
  border-radius: 12rpx;
  border: 1px dashed rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.45);
  font-size: 24rpx;
}

.bold { font-weight: 700; color: #fff; }

.timeline-item {
  display: block;
  padding: 16rpx 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 26rpx;
}

.moral {
  display: block;
  margin-top: 16rpx;
  color: #ffd166;
  line-height: 1.8;
}

.notice {
  display: block;
  margin-top: 24rpx;
  padding: 20rpx;
  font-size: 24rpx;
  color: #ffd166;
  background: rgba(255, 209, 102, 0.1);
  border: 1px solid rgba(255, 209, 102, 0.25);
  border-radius: 12rpx;
  line-height: 1.6;
}
</style>
