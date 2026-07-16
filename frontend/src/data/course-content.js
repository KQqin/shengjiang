export const courseNames = {
  1: '五四运动与新文化启蒙',
  4: '遵义会议：生死攸关转折点',
  7: '乡村振兴战略解读',
  10: '延安精神与党的优良作风',
  11: '革命年代青年榜样故事',
}

export const defaultGame = {
  title: '🎮 历史抉择',
  scenario: '1919 年 6 月，北洋政府逮捕大批学生。作为李大钊，你收到校方施压，同时学生请求公开声援……',
  choices: [
    { text: 'A. 公开发表文章声援学生', feedback: '正确！李大钊选择了公开发声援学生，以实际行动支持爱国运动。' },
    { text: 'B. 私下资助但保持低调', feedback: '部分正确。李大钊确实在幕后支持学生，但很快便公开发表文章。' },
    { text: 'C. 说服学生停止游行', feedback: '不符合历史。李大钊始终积极支持和引导学生的爱国运动。' },
  ],
}

export const courseContent = {
  11: {
    heroTitle: '革命年代',
    heroHighlight: '青年榜样故事',
    heroSub: '革命年代青年榜样系列 · 人物故事互动课件',
    nodes: ['开篇', '榜样群像', '赵世炎事迹', '青年抉择', '⚡双重互动游戏', '小结'],
    sections: [
      { type: 'hero' },
      {
        type: 'block',
        heading: '革命年代的青年群像',
        paragraphs: [
          '在中国革命波澜壮阔的历程中，一代代青年以热血与理想投身救国救民的伟大事业。他们中有投身五四运动的先锋，有奔赴延安的知识分子，有在隐蔽战线奋斗的无名英雄。',
          '本课程通过人物故事，带领学习者走近那些照亮时代的青年榜样。',
        ],
      },
      {
        type: 'block',
        heading: '赵世炎：信仰之光的青年',
        paragraphs: [
          '赵世炎（1901—1927），四川酉阳人。早年赴法勤工俭学，接受马克思主义，回国后投身工人运动，是中共早期重要领导人之一。1927 年 4 月，他在上海被捕就义，年仅 26 岁。',
        ],
        quote: '「奋斗、奋斗，奋斗到底！」—— 赵世炎',
      },
      {
        type: 'block',
        heading: '青年的选择与担当',
        paragraphs: [
          '面对民族危亡，革命年代的青年面临求学、谋生、革命、归乡等多重选择。他们的每一次抉择，不仅塑造个人命运，也深刻影响着中国革命的历史进程。',
        ],
      },
      { type: 'dual-games' },
      {
        type: 'block',
        heading: '本课小结',
        paragraphs: [
          '革命年代的青年榜样，以理想和生命诠释了「青春向党」的深刻内涵。愿当代青年以史为鉴，传承红色基因，担当时代使命。',
        ],
      },
    ],
  },
}

export const defaultNodes = ['开篇', '1919转折', '历史影像', '李大钊', '⚡互动游戏', '小结']

export const defaultSections = [
  {
    type: 'hero',
    title: '五四运动',
    highlight: '与新文化启蒙',
    sub: '沉浸式互动全景课件 · 向下滚动展开',
  },
  {
    type: 'block',
    heading: '1919 年：一个时代的转折',
    paragraphs: [
      '1919 年 5 月 4 日，北京学生三千余人齐聚天安门，高呼「外争主权、内除国贼」，掀起彻底反帝反封建的伟大爱国革命运动。',
    ],
    quote: '「铁肩担道义，妙手著文章。」—— 李大钊',
  },
  {
    type: 'video',
    heading: '历史影像',
    placeholder: '▶ 五四运动纪实（3:24）',
  },
  {
    type: 'block',
    heading: '李大钊：马克思主义先驱',
    paragraphs: [
      '李大钊是最早系统传播马克思主义的思想家之一，积极支持学生爱国运动。',
    ],
  },
  { type: 'single-game' },
  {
    type: 'block',
    heading: '本课小结',
    paragraphs: [
      '五四运动是中国近代史上具有里程碑意义的伟大事件。',
    ],
  },
]

export function parseHeroFromTitle(title) {
  if (title.includes('：')) {
    const [a, b] = title.split('：')
    return { title: a, highlight: b, sub: '沉浸式互动全景课件 · 向下滚动展开' }
  }
  return { title, highlight: '', sub: '沉浸式互动全景课件 · 向下滚动展开' }
}
