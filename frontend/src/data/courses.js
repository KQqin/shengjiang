export const courses = [
  { id: 11, title: '革命年代青年榜样故事', series: '革命年代青年榜样系列', filter: 'youth', h: 't', hot: 92, new: 0, games: 2, grad: 'linear-gradient(135deg,#FF8FAB,#C62828)', cover: 'assets/course-covers/11.png' },
  { id: 1, title: '五四运动与新文化启蒙', series: '觉醒年代系列', filter: 'awakening', h: 't', hot: 98, new: 1, grad: 'linear-gradient(135deg,#FF6B6B,#C62828)', cover: 'assets/course-covers/1.png' },
  { id: 2, title: '李大钊与马克思主义传播', series: '觉醒年代系列', filter: 'awakening', h: 'm', hot: 85, new: 3, grad: 'linear-gradient(135deg,#FF8FAB,#9B2335)', cover: 'assets/course-covers/2.jpeg' },
  { id: 3, title: '陈独秀与新文化运动', series: '觉醒年代系列', filter: 'awakening', h: 's', hot: 72, new: 5, grad: 'linear-gradient(135deg,#FFB347,#E84855)', cover: 'assets/course-covers/3.jpg' },
  { id: 4, title: '遵义会议：生死攸关转折点', series: '长征精神系列', filter: 'longmarch', h: 't', hot: 95, new: 2, grad: 'linear-gradient(135deg,#4A7C23,#2D5016)', cover: 'assets/course-covers/4.png' },
  { id: 5, title: '飞夺泸定桥', series: '长征精神系列', filter: 'longmarch', h: 'm', hot: 88, new: 4, grad: 'linear-gradient(135deg,#6B8E23,#3D5C1A)', cover: 'assets/course-covers/5.jpeg' },
  { id: 6, title: '爬雪山过草地', series: '长征精神系列', filter: 'longmarch', h: 's', hot: 76, new: 6, grad: 'linear-gradient(135deg,#558B2F,#33691E)', cover: 'assets/course-covers/6.jpeg' },
  { id: 7, title: '乡村振兴战略解读', series: '新时代思政系列', filter: 'newera', h: 'm', hot: 80, new: 7, grad: 'linear-gradient(135deg,#FFD166,#E84855)', cover: 'assets/course-covers/7.jpeg' },
  { id: 8, title: '文化自信与传承', series: '新时代思政系列', filter: 'newera', h: 't', hot: 74, new: 8, grad: 'linear-gradient(135deg,#C9A0DC,#6B2737)', cover: 'assets/course-covers/8.jpeg' },
  { id: 9, title: '井冈山精神永放光芒', series: '红色革命系列', filter: 'revolution', h: 's', hot: 82, new: 9, grad: 'linear-gradient(135deg,#E84855,#8B0000)', cover: 'assets/course-covers/9.jpeg' },
  { id: 10, title: '延安精神与党的优良作风', series: '红色革命系列', filter: 'revolution', h: 'm', hot: 90, new: 10, grad: 'linear-gradient(135deg,#FF6B6B,#6B2737)', cover: 'assets/course-covers/10.jpeg' },
]

export const slides = [
  { title: '革命年代青年榜样故事', tag: '革命年代青年榜样系列', desc: '全新上线 · 含历史抉择生成器 + 红色剧本杀', id: 11 },
  { title: '五四运动与新文化启蒙', tag: '觉醒年代系列', desc: '沉浸式互动全景课件 · 含 2 个游戏节点', id: 1 },
  { title: '遵义会议：生死攸关转折点', tag: '长征精神系列', desc: '策略推演 + 历史抉择互动', id: 4 },
  { title: '乡村振兴战略解读', tag: '新时代思政系列', desc: 'AI 生成 · 可直接开课授课', id: 7 },
]

export const seriesMap = {
  all: '全部',
  youth: '革命年代青年榜样系列',
  awakening: '觉醒年代系列',
  longmarch: '长征精神系列',
  newera: '新时代思政系列',
  revolution: '红色革命系列',
}

export function getCourseById(id) {
  return courses.find((c) => c.id === id)
}

export function getCourseCoverPath(id) {
  return getCourseById(id)?.cover || ''
}
