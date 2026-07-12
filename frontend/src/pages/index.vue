<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { courses, slides, seriesMap } from '../data/courses.js'

const slideIdx = ref(0)
const filter = ref('all')
const libView = ref('waterfall')
const searchQuery = ref('')
const columnsRendered = ref(false)

const trackStyle = computed(() => ({
  transform: `translateX(-${slideIdx.value * 100}%)`,
}))

const rankNew = computed(() =>
  [...courses].sort((a, b) => a.new - b.new).slice(0, 5),
)

const rankHot = computed(() =>
  [...courses].sort((a, b) => b.hot - a.hot).slice(0, 5),
)

const waterfallList = computed(() =>
  filter.value === 'all' ? courses : courses.filter((c) => c.filter === filter.value),
)

const seriesEntries = computed(() =>
  Object.entries(seriesMap).filter(([k]) => k !== 'all'),
)

function matchesSearch(text) {
  const q = searchQuery.value.trim().toLowerCase()
  return !q || text.toLowerCase().includes(q)
}

function goCourse(id) {
  uni.navigateTo({ url: `/pages/classroom?course=${id}` })
}

function goSlide(i) {
  slideIdx.value = i
}

function prevSlide() {
  goSlide((slideIdx.value - 1 + slides.length) % slides.length)
}

function nextSlide() {
  goSlide((slideIdx.value + 1) % slides.length)
}

function setFilter(key) {
  filter.value = key
}

function setLibView(view) {
  libView.value = view
  if (view === 'columns') columnsRendered.value = true
}

function onSearchInput(e) {
  searchQuery.value = e.detail?.value ?? e.target?.value ?? ''
}

let carouselTimer = null

onMounted(() => {
  carouselTimer = setInterval(() => {
    goSlide((slideIdx.value + 1) % slides.length)
  }, 5000)
})

onUnmounted(() => {
  if (carouselTimer) clearInterval(carouselTimer)
})
</script>

<template>
  <view class="page-home">
    <view class="header">
      <view class="header-inner">
        <view class="logo" @click="goCourse(11)">
          <view class="logo-mark">红</view>
          <text class="logo-name">数智红途</text>
        </view>
        <view class="nav-main">
          <text class="nav-link active">智学课堂</text>
          <text class="nav-link">星火素材</text>
          <text class="nav-link">创意工坊</text>
          <text class="nav-link">我的足迹</text>
        </view>
        <view class="search-bar">
          <input
            class="search-input"
            type="text"
            placeholder="搜索党课、系列、主讲人…"
            :value="searchQuery"
            @input="onSearchInput"
          />
          <button type="button" class="search-btn">搜索</button>
        </view>
        <view class="header-user">
          <text class="user-link">个人中心</text>
          <text class="user-link">消息</text>
          <text class="user-link">帮助</text>
          <view class="avatar" />
        </view>
      </view>
    </view>

    <view class="hero-wrap">
      <view class="hero">
        <view class="carousel">
          <view class="carousel-track" :style="trackStyle">
            <view
              v-for="s in slides"
              :key="s.id"
              class="carousel-slide"
              @click="goCourse(s.id)"
            >
              <view class="slide-bg" :class="s.bg" />
              <view class="slide-content">
                <text class="slide-tag">{{ s.tag }}</text>
                <view class="slide-title">{{ s.title }}</view>
                <view class="slide-desc">{{ s.desc }}</view>
                <text class="slide-cta">进入课件 →</text>
              </view>
            </view>
          </view>
          <button type="button" class="carousel-arrow carousel-arrow--prev" @click.stop="prevSlide">‹</button>
          <button type="button" class="carousel-arrow carousel-arrow--next" @click.stop="nextSlide">›</button>
          <view class="carousel-dots">
            <button
              v-for="(_, i) in slides"
              :key="i"
              type="button"
              class="carousel-dot"
              :class="{ active: slideIdx === i }"
              @click.stop="goSlide(i)"
            />
          </view>
        </view>
        <view class="user-panel">
          <view class="user-avatar" />
          <view class="user-name">郑同学</view>
          <view class="user-hint">最近学习 · 觉醒年代系列</view>
          <button type="button" class="btn btn-primary" @click="goCourse(11)">我的课程</button>
          <button type="button" class="btn btn-outline">我的制作</button>
        </view>
      </view>
    </view>

    <view class="features">
      <view class="feature-card feature-card--material">
        <view class="feature-icon">🔥</view>
        <view class="feature-text">
          <view class="feature-title">星火素材</view>
          <view class="feature-desc">采集上传红色素材卡片，万物皆卡片</view>
        </view>
        <text class="feature-arrow">→</text>
      </view>
      <view class="feature-card feature-card--workshop">
        <view class="feature-icon">⚙️</view>
        <view class="feature-text">
          <view class="feature-title">创意工坊</view>
          <view class="feature-desc">AI 生成互动党课课件，一键植入游戏</view>
        </view>
        <text class="feature-arrow">→</text>
      </view>
    </view>

    <view class="section">
      <view class="section-head">
        <view class="section-title">课程<text class="em">排行推荐</text></view>
        <text class="section-more">查看全部 →</text>
      </view>
      <view class="rankings">
        <view class="rank-col">
          <view class="rank-col-head">
            <view class="rank-col-title">最新课程</view>
            <text class="rank-col-sub">NEW COURSES</text>
          </view>
          <view
            v-for="(c, i) in rankNew"
            :key="'new-' + c.id"
            v-show="matchesSearch(c.title + c.series)"
            class="rank-item"
            @click="goCourse(c.id)"
          >
            <text class="rank-num" :class="{ top: i < 3 }">{{ i + 1 }}</text>
            <view class="rank-thumb" :class="'rank-thumb--' + ((i % 5) + 1)" />
            <view class="rank-info">
              <view class="rank-info-title">{{ c.title }}</view>
              <view class="rank-info-meta">{{ c.series }} · {{ c.hot }} 人参与</view>
            </view>
          </view>
        </view>
        <view class="rank-col">
          <view class="rank-col-head">
            <view class="rank-col-title">最热课程</view>
            <text class="rank-col-sub">HOT COURSES</text>
          </view>
          <view
            v-for="(c, i) in rankHot"
            :key="'hot-' + c.id"
            v-show="matchesSearch(c.title + c.series)"
            class="rank-item"
            @click="goCourse(c.id)"
          >
            <text class="rank-num" :class="{ top: i < 3 }">{{ i + 1 }}</text>
            <view class="rank-thumb" :class="'rank-thumb--' + ((i % 5) + 1)" />
            <view class="rank-info">
              <view class="rank-info-title">{{ c.title }}</view>
              <view class="rank-info-meta">{{ c.series }} · {{ c.hot }} 人参与</view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view class="section">
      <view class="section-head">
        <view class="section-title">精品互动<text class="em">党课库</text></view>
      </view>
      <view class="library-tabs">
        <button
          type="button"
          class="lib-tab"
          :class="{ active: libView === 'waterfall' }"
          @click="setLibView('waterfall')"
        >
          精品课程
        </button>
        <button
          type="button"
          class="lib-tab"
          :class="{ active: libView === 'columns' }"
          @click="setLibView('columns')"
        >
          专栏系列
        </button>
      </view>
      <view class="series-filter">
        <button
          v-for="([key, label]) in Object.entries(seriesMap)"
          :key="key"
          type="button"
          class="series-chip"
          :class="{ active: filter === key }"
          @click="setFilter(key)"
        >
          {{ label }}
        </button>
      </view>
      <view class="waterfall-view" :class="{ hide: libView === 'columns' }">
        <view class="waterfall">
          <view
            v-for="c in waterfallList"
            :key="c.id"
            v-show="matchesSearch(c.title + c.series)"
            class="poster-card"
            @click="goCourse(c.id)"
          >
            <view
              class="poster-img"
              :class="'poster-img--' + c.h"
              :style="{ background: c.grad }"
            >
              <view class="poster-title">{{ c.title }}</view>
            </view>
            <view class="poster-body">
              <view class="poster-series">{{ c.series }}</view>
              <view class="poster-meta">
                <text>🎮 {{ c.games || 1 }} 个互动</text>
                <text>{{ c.hot }} 人学习</text>
              </view>
            </view>
          </view>
        </view>
      </view>
      <view class="columns-view" :class="{ show: libView === 'columns' }">
        <view v-if="columnsRendered">
          <view
            v-for="([key, name]) in seriesEntries"
            :key="key"
            class="series-block"
          >
            <view
              v-if="courses.filter((c) => c.filter === key).length"
              class="series-block-inner"
            >
              <view class="series-row-head">
                <view class="series-row-title">{{ name }}</view>
                <text class="section-more">查看全部 →</text>
              </view>
              <view class="series-scroll">
                <view
                  v-for="c in courses.filter((item) => item.filter === key)"
                  :key="c.id"
                  v-show="matchesSearch(c.title + c.series)"
                  class="poster-card"
                  @click="goCourse(c.id)"
                >
                  <view
                    class="poster-img"
                    :class="'poster-img--' + c.h"
                    :style="{ background: c.grad }"
                  >
                    <view class="poster-title">{{ c.title }}</view>
                  </view>
                  <view class="poster-body">
                    <view class="poster-series">{{ c.series }}</view>
                    <view class="poster-meta">
                      <text>🎮 {{ c.games || 1 }} 个互动</text>
                      <text>{{ c.hot }} 人学习</text>
                    </view>
                  </view>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view class="footer">© 2026 数智红途 · AI 驱动大思政实践教育平台</view>
  </view>
</template>

<style lang="scss">
@import '../styles/home.scss';

.page-home {
  .nav-link {
    padding: 8px 14px;
    font-size: 14px;
    font-weight: 500;
    color: var(--text-sec);
    border-radius: 8px;
    transition: 0.2s;
    display: inline-block;
  }

  .nav-link.active {
    color: var(--red);
    background: var(--red-light);
  }

  .search-input {
    flex: 1;
    border: none;
    outline: none;
    padding: 0 16px;
    font-size: 13px;
    font-family: inherit;
    background: transparent;
  }

  .search-btn {
    width: 72px;
    height: 100%;
    border: none;
    background: linear-gradient(135deg, var(--red-soft), var(--red));
    color: white;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    font-family: inherit;
  }

  .user-link {
    font-size: 13px;
    color: var(--text-sec);
  }

  .section-title .em {
    font-style: normal;
    color: var(--red);
  }

  .rank-col-title {
    font-size: 18px;
    font-weight: 700;
    color: var(--red);
  }

  .rank-col-sub {
    font-size: 12px;
    color: var(--text-mut);
  }

  .rank-info-title {
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 4px;
    line-height: 1.4;
  }

  .rank-info-meta {
    font-size: 12px;
    color: var(--text-mut);
  }

  .feature-title {
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 4px;
  }

  .feature-desc {
    font-size: 13px;
    color: var(--text-sec);
  }

  .series-row-title {
    font-size: 18px;
    font-weight: 700;
  }
}
</style>
