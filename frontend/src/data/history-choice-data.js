/** 历史抉择 · 由 server/tools/build_choice_data.py + map_choice_images.py 生成 */
export const historyChoiceGame = {
  "title": "历史抉择",
  "subtitle": "青春守初心，廉洁担使命",
  "announcement": "欢迎参与历史抉择体验！你将化身革命先辈与新时代青年，在一次次选择中感悟廉洁品格、青春担当。每道选择都会触发不同结果，请认真思考作答，完成全部抉择即可查看专属结局。",
  "characters": [
    {
      "id": "liu-qiyao",
      "name": "刘启耀",
      "title": "江西省苏维埃政府主席，保管党组织经费",
      "intro": "自带干粮办公的省主席，苏区突围后身负重伤，贴身保管党组织13根金条，乞讨两年分文未动公款",
      "round1": {
        "story": "第五次反“围剿”失败，红军主力长征，你奉命留守赣南游击。一场惨烈突围战后你身负重伤，与所有战友失联，腰间贴身藏着省委全部经费：13根金条、多块银元首饰。深山寒冬，你饥寒交迫，身边无任何补给。",
        "options": [
          {
            "key": "A",
            "text": "取出少量经费购买食物",
            "deduction": "一时心软动用公款，廉洁底线出现第一道裂痕，你填饱肚子后开始担忧后续长期流浪缺粮，内心盘算可以再多取用一些。",
            "mark": "失范",
            "branch": "A",
            "deductionImage": "shared/assets/history-choice/deductions/liu-qiyao-r1-A.png"
          },
          {
            "key": "B",
            "text": "坚决不动一分公款，沿路乞讨求生",
            "deduction": "牢记党员职责，集体经费分毫不动，哪怕忍冻挨饿也要完整保管，唯一目标是找到党组织交还经费。",
            "mark": "正向",
            "branch": "B",
            "deductionImage": "shared/assets/history-choice/deductions/liu-qiyao-r1-B.png"
          },
          {
            "key": "C",
            "text": "把经费藏山洞，独自外出乞讨",
            "deduction": "经费脱离自身看管，一旦被白军搜山、村民无意发现，党的全部活动经费将彻底丢失，敌后斗争会直接瘫痪。",
            "mark": "摇摆",
            "branch": "C",
            "deductionImage": "shared/assets/history-choice/deductions/liu-qiyao-r1-C.png"
          }
        ],
        "sceneImage": "shared/assets/history-choice/scenes/liu-qiyao-r1.png"
      },
      "round2": {
        "A": {
          "story": "流浪途中同乡认出你，知晓你随身带有金银，私下劝说：现在组织下落不明，不如带着钱财隐姓埋名，不用再风餐露宿。",
          "options": [
            {
              "key": "A",
              "text": "接受劝说，携带全部经费远走他乡",
              "deduction": "彻底背弃革命信仰，侵占党组织专项经费，完全丢失党员初心。",
              "mark": "失范",
              "node": "A1",
              "deductionImage": "shared/assets/history-choice/deductions/liu-qiyao-r2-A-A.png"
            },
            {
              "key": "B",
              "text": "内心纠结，暂时一边找组织一边保留剩余经费",
              "deduction": "明知挪用公款违规，却抱有侥幸心理，公私界限模糊。",
              "mark": "摇摆",
              "node": "A2",
              "deductionImage": "shared/assets/history-choice/deductions/liu-qiyao-r2-A-B.png"
            },
            {
              "key": "C",
              "text": "立刻停止动用公款，剩余金银妥善包裹封存",
              "deduction": "及时止损，主动守住剩余经费，知错后选择坚守底线。",
              "mark": "正向",
              "node": "A3",
              "deductionImage": "shared/assets/history-choice/deductions/liu-qiyao-r2-A-C.png"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/liu-qiyao-r2-A.png"
        },
        "B": {
          "story": "两年沿街乞讨，你偶然遇上失散的地下联络员，对方告知：临时省委刚刚成立，没有一分钱经费，无法开展钨砂外贸、无法救治伤病游击队员。",
          "options": [
            {
              "key": "A",
              "text": "立刻拿出全部金银完整上交",
              "deduction": "自始至终坚守底线，历尽苦难仍完整守护党的财产。",
              "mark": "正向",
              "node": "B1",
              "deductionImage": "shared/assets/history-choice/deductions/liu-qiyao-r2-B-A.png"
            },
            {
              "key": "B",
              "text": "先截留部分经费，防备后续再度失联挨饿",
              "deduction": "以自保为由私留公款，公私观念出现松动。",
              "mark": "摇摆",
              "node": "B2",
              "deductionImage": "shared/assets/history-choice/deductions/liu-qiyao-r2-B-B.png"
            },
            {
              "key": "C",
              "text": "隐瞒经费存在，先观察组织是否可靠",
              "deduction": "不信任党组织，刻意藏匿核心革命物资。",
              "mark": "失范",
              "node": "B3",
              "deductionImage": "shared/assets/history-choice/deductions/liu-qiyao-r2-B-C.png"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/liu-qiyao-r2-B.png"
        },
        "C": {
          "story": "你把金条藏入山洞外出乞讨，不久后白军大规模搜山，山洞周边被层层封锁，经费随时可能被敌军搜走没收。",
          "options": [
            {
              "key": "A",
              "text": "冒着被抓捕的风险，连夜取回经费",
              "deduction": "不顾个人生死守护集体财产，忠诚底色从未动摇。",
              "mark": "正向",
              "node": "C1",
              "deductionImage": "shared/assets/history-choice/deductions/liu-qiyao-r2-C-A.png"
            },
            {
              "key": "B",
              "text": "放弃山洞内经费，独自逃离搜山区域",
              "deduction": "为保全自身舍弃党的核心经费，属于严重失职。",
              "mark": "失范",
              "node": "C2",
              "deductionImage": "shared/assets/history-choice/deductions/liu-qiyao-r2-C-B.png"
            },
            {
              "key": "C",
              "text": "找当地村民帮忙转移，许诺分一部分金银作为报酬",
              "deduction": "用公家财物换取私人帮助，严重违反苏区财经纪律。",
              "mark": "摇摆",
              "node": "C3",
              "deductionImage": "shared/assets/history-choice/deductions/liu-qiyao-r2-C-C.png"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/liu-qiyao-r2-C.png"
        }
      },
      "round3": {
        "A1": {
          "story": "几年后你拿着经费在白区安稳度日，偶然听闻赣南重建临时省委，敌后同志极度缺少经费购买食盐、西药。",
          "options": [
            {
              "key": "A",
              "text": "无视党组织困境，继续隐藏钱财",
              "deduction": "你选择了：无视党组织困境，继续隐藏钱财",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "拿出极小部分钱财匿名捐助",
              "deduction": "你选择了：拿出极小部分钱财匿名捐助",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "主动将全部金银送回苏区上交",
              "deduction": "你选择了：主动将全部金银送回苏区上交",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/liu-qiyao-r3-A1.png"
        },
        "A2": {
          "story": "你一边流浪寻党，一边藏着剩余经费，偶遇地下联络员告知省委急需资金开展红色贸易。",
          "options": [
            {
              "key": "A",
              "text": "隐瞒身上金银，观望局势",
              "deduction": "你选择了：隐瞒身上金银，观望局势",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "只交出一小部分，自己留存大半",
              "deduction": "你选择了：只交出一小部分，自己留存大半",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "完整上交所有保管经费",
              "deduction": "你选择了：完整上交所有保管经费",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/liu-qiyao-r3-A2.png"
        },
        "A3": {
          "story": "你封存剩余公款，坚持乞讨两年终于找到临时省委，所有干部等着经费打破经济封锁。",
          "options": [
            {
              "key": "A",
              "text": "扣除自己当年消耗的经费再上交",
              "deduction": "你选择了：扣除自己当年消耗的经费再上交",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "分文不少完整上交，如实说明当年失误",
              "deduction": "你选择了：分文不少完整上交，如实说明当年失误",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "谎称从未动用公款，掩盖过往错误",
              "deduction": "你选择了：谎称从未动用公款，掩盖过往错误",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/liu-qiyao-r3-A3.png"
        },
        "B1": {
          "story": "你完整上交全部金条银元，省委干部要记录你的功绩，对外宣传你的事迹。",
          "options": [
            {
              "key": "A",
              "text": "拒绝大肆宣传，认为只是党员本分",
              "deduction": "你选择了：拒绝大肆宣传，认为只是党员本分",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "接受表彰，但不索要任何物资补贴",
              "deduction": "你选择了：接受表彰，但不索要任何物资补贴",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "借机要求组织分配粮食、衣物作为补偿",
              "deduction": "你选择了：借机要求组织分配粮食、衣物作为补偿",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/liu-qiyao-r3-B1.png"
        },
        "B2": {
          "story": "你只上交部分经费，留下少量金银以备不时之需，省委干部询问经费是否完整。",
          "options": [
            {
              "key": "A",
              "text": "如实坦白私留，主动交出剩余",
              "deduction": "你选择了：如实坦白私留，主动交出剩余",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "隐瞒截留，谎称经费仅此一部分",
              "deduction": "你选择了：隐瞒截留，谎称经费仅此一部分",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "上交一半，另一半拖延日后再交",
              "deduction": "你选择了：上交一半，另一半拖延日后再交",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/liu-qiyao-r3-B2.png"
        },
        "B3": {
          "story": "你隐瞒携带的经费，联络员多次诉苦苏区物资极度短缺。",
          "options": [
            {
              "key": "A",
              "text": "始终隐瞒，拒绝交出",
              "deduction": "你选择了：始终隐瞒，拒绝交出",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "犹豫多日后拿出半数经费",
              "deduction": "你选择了：犹豫多日后拿出半数经费",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "看清组织困境，全部主动上交",
              "deduction": "你选择了：看清组织困境，全部主动上交",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/liu-qiyao-r3-B3.png"
        },
        "C1": {
          "story": "你冒死取回经费，长期随身携带继续流浪，两年后成功和临时省委汇合。",
          "options": [
            {
              "key": "A",
              "text": "完整上交所有金银，讲述守护全过程",
              "deduction": "你选择了：完整上交所有金银，讲述守护全过程",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "留下少量金银补贴多年苦难生活",
              "deduction": "你选择了：留下少量金银补贴多年苦难生活",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "隐瞒金银，自行留存",
              "deduction": "你选择了：隐瞒金银，自行留存",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/liu-qiyao-r3-C1.png"
        },
        "C2": {
          "story": "你放弃山洞经费独自逃生，后续得知山洞金银已被白军全部缴获，敌后斗争陷入绝境。",
          "options": [
            {
              "key": "A",
              "text": "主动向组织坦白过错，尽力弥补损失",
              "deduction": "你选择了：主动向组织坦白过错，尽力弥补损失",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "刻意隐瞒藏金一事，假装从未保管经费",
              "deduction": "你选择了：刻意隐瞒藏金一事，假装从未保管经费",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "想尽办法筹款弥补丢失的经费",
              "deduction": "你选择了：想尽办法筹款弥补丢失的经费",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/liu-qiyao-r3-C2.png"
        },
        "C3": {
          "story": "村民帮你转移经费后，多次上门索要许诺的金银分成。",
          "options": [
            {
              "key": "A",
              "text": "拒绝动用公款兑现承诺，向村民耐心解释",
              "deduction": "你选择了：拒绝动用公款兑现承诺，向村民耐心解释",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "拿出少量公款打发村民",
              "deduction": "你选择了：拿出少量公款打发村民",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "直接分予村民大量金银",
              "deduction": "你选择了：直接分予村民大量金银",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/liu-qiyao-r3-C3.png"
        }
      },
      "endingRules": [
        {
          "id": "赤胆守廉者",
          "rule": "三轮全部【正向】",
          "summary": "如同真实历史中的刘启耀，历经饥饿、危险、诱惑仍坚守公私底线，把集体利益放在生命之上，是青年廉洁修身最好的榜样。",
          "image": "shared/assets/history-choice/endings/liu-qiyao-赤胆守廉者.png"
        },
        {
          "id": "迷途知返者",
          "rule": "仅有1次【摇摆】，无【失范】",
          "summary": "中途内心产生短暂动摇，但能及时纠正错误、坚守原则，在反思中筑牢廉洁防线。",
          "image": "shared/assets/history-choice/endings/liu-qiyao-迷途知返者.png"
        },
        {
          "id": "底线摇摆者",
          "rule": "1次【失范】或0次【失范】且多次【摇摆】",
          "summary": "面对苦难与诱惑容易放宽自我要求，公私界限模糊，需要加强理想信念锤炼。",
          "image": "shared/assets/history-choice/endings/liu-qiyao-底线摇摆者.png"
        },
        {
          "id": "初心失守者",
          "rule": "两次及以上【失范】",
          "summary": "多次突破纪律红线，看重个人安危与私利，背离革命先辈忠诚为公的精神。"
        }
      ],
      "portrait": "shared/assets/history-choice/scenes/liu-qiyao-r1.png"
    },
    {
      "id": "zhang-qide",
      "name": "张其德",
      "title": "闽浙赣省财政部长、银行行长，统筹红色贸易",
      "intro": "苏区“好管家”，手握财政大权，厉行勤俭节约，拒绝公物私用，带领群众突破经济封锁",
      "round1": {
        "story": "闽浙赣苏区物资匮乏，你主持采购办公桌椅，采购结束剩余一张断腿破旧木桌。下属提议财政部长应当配置全新办公桌，方便处理钨砂外贸、物资调配账目。",
        "options": [
          {
            "key": "A",
            "text": "同意拨款购置新办公桌",
            "deduction": "放松自我要求，追求干部特殊待遇，违背苏区勤俭节约规定。",
            "mark": "失范",
            "branch": "A",
            "deductionImage": "shared/assets/history-choice/deductions/zhang-qide-r1-A.png"
          },
          {
            "key": "B",
            "text": "婉言拒绝，坚持使用断腿旧桌办公",
            "deduction": "以身作则厉行节俭，富日子当穷日子过，为全体财经干部树立标杆。",
            "mark": "正向",
            "branch": "B",
            "deductionImage": "shared/assets/history-choice/deductions/zhang-qide-r1-B.png"
          },
          {
            "key": "C",
            "text": "暂时先用旧桌，等财政宽裕后再换新桌",
            "deduction": "当下节俭，但内心默认干部应当享受更好条件，底线松动。",
            "mark": "摇摆",
            "branch": "C",
            "deductionImage": "shared/assets/history-choice/deductions/zhang-qide-r1-C.png"
          }
        ],
        "sceneImage": "shared/assets/history-choice/scenes/zhang-qide-r1.png"
      },
      "round2": {
        "A": {
          "story": "消息传到乡下，你的老伴得知你手握全省财政大权，家中老小衣食困难，专程来财政部希望支取公款补贴家用。",
          "options": [
            {
              "key": "A",
              "text": "心软支取公款接济家人",
              "deduction": "动用集体财政资金满足私人家庭需求，公私界限彻底混淆。",
              "mark": "失范",
              "node": "A1",
              "deductionImage": "shared/assets/history-choice/deductions/zhang-qide-r2-A-A.png"
            },
            {
              "key": "B",
              "text": "坚决拒绝，私下靠个人微薄补贴接济家庭",
              "deduction": "即便家中困难，也绝不占用公家物资，守住财经干部核心底线",
              "mark": "正向",
              "node": "A2",
              "deductionImage": "shared/assets/history-choice/deductions/zhang-qide-r2-A-B.png"
            },
            {
              "key": "C",
              "text": "少量支取公款，日后慢慢填补",
              "deduction": "明知挪用公款违规，仍选择小额占用集体资金，抱有侥幸心理。",
              "mark": "失范",
              "node": "A3",
              "deductionImage": "shared/assets/history-choice/deductions/zhang-qide-r2-A-C.png"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/zhang-qide-r2-A.png"
        },
        "B": {
          "story": "你带领群众开凿硝盐厂、通过棺材运盐突破封锁，大批食盐、布匹运回苏区，有干部提议优先分给财经工作人员改善生活。",
          "options": [
            {
              "key": "A",
              "text": "物资全部分配前线与普通群众，干部最后领取",
              "deduction": "牢记为民初心，先群众后干部，不搞特殊化。",
              "mark": "正向",
              "node": "B1",
              "deductionImage": "shared/assets/history-choice/deductions/zhang-qide-r2-B-A.png"
            },
            {
              "key": "B",
              "text": "少量分配给干部，兼顾工作人员辛苦",
              "deduction": "体谅同事，轻微放宽分配原则。",
              "mark": "摇摆",
              "node": "B2",
              "deductionImage": "shared/assets/history-choice/deductions/zhang-qide-r2-B-B.png"
            },
            {
              "key": "C",
              "text": "优先保障财经部门物资供给",
              "deduction": "利用职权为本部门谋福利，破坏分配公平。",
              "mark": "失范",
              "node": "B3",
              "deductionImage": "shared/assets/history-choice/deductions/zhang-qide-r2-B-C.png"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/zhang-qide-r2-B.png"
        },
        "C": {
          "story": "白区客商联系你，暗示可以虚报钨砂采购数量，多出的钱款双方私下平分获利。",
          "options": [
            {
              "key": "A",
              "text": "严词拒绝，严格规范外贸单据",
              "deduction": "坚守财经底线，杜绝利益输送。",
              "mark": "正向",
              "node": "C1",
              "deductionImage": "shared/assets/history-choice/deductions/zhang-qide-r2-C-A.png"
            },
            {
              "key": "B",
              "text": "表面应付，暗中观望有无获利空间",
              "deduction": "内心存在贪念，立场摇摆。",
              "mark": "摇摆",
              "node": "C2",
              "deductionImage": "shared/assets/history-choice/deductions/zhang-qide-r2-C-B.png"
            },
            {
              "key": "C",
              "text": "同意联合虚报，私下分取差价",
              "deduction": "利用红色贸易职权谋取私利，严重违纪。",
              "mark": "失范",
              "node": "C3",
              "deductionImage": "shared/assets/history-choice/deductions/zhang-qide-r2-C-C.png"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/zhang-qide-r2-C.png"
        }
      },
      "round3": {
        "A1": {
          "story": "你动用公款补贴家人，其他财政干部纷纷效仿，苏区开支大幅增加，钨砂换来的物资供给紧张。",
          "options": [
            {
              "key": "A",
              "text": "继续默许公款家用",
              "deduction": "你选择了：继续默许公款家用",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "立刻停止，主动退还全部钱款",
              "deduction": "你选择了：立刻停止，主动退还全部钱款",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "缩减支取金额，不再大额挪用",
              "deduction": "你选择了：缩减支取金额，不再大额挪用",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/zhang-qide-r3-A1.png"
        },
        "A2": {
          "story": "你拒绝动用公款，依靠自己节省口粮补贴家人，有人劝你利用外贸职权赚取补贴。",
          "options": [
            {
              "key": "A",
              "text": "坚决拒绝任何私利渠道",
              "deduction": "你选择了：坚决拒绝任何私利渠道",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "短暂动心后依旧坚守底线",
              "deduction": "你选择了：短暂动心后依旧坚守底线",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "接受客商私下馈赠物资",
              "deduction": "你选择了：接受客商私下馈赠物资",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/zhang-qide-r3-A2.png"
        },
        "A3": {
          "story": "你少量挪用公款补贴家庭，账目出现小额缺口，下属提醒会被审计查出。",
          "options": [
            {
              "key": "A",
              "text": "涂改账目掩盖缺口",
              "deduction": "你选择了：涂改账目掩盖缺口",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "主动补齐钱款，公开检讨",
              "deduction": "你选择了：主动补齐钱款，公开检讨",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "拖延补齐，观望是否会被发现",
              "deduction": "你选择了：拖延补齐，观望是否会被发现",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/zhang-qide-r3-A3.png"
        },
        "B1": {
          "story": "物资全部分给群众后，本部门工作人员生活艰苦，有人抱怨分配规则过于严苛。",
          "options": [
            {
              "key": "A",
              "text": "坚守分配制度，做好思想开导",
              "deduction": "你选择了：坚守分配制度，做好思想开导",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "小幅调整分配方案，均衡兼顾",
              "deduction": "你选择了：小幅调整分配方案，均衡兼顾",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "修改规则优先保障干部",
              "deduction": "你选择了：修改规则优先保障干部",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/zhang-qide-r3-B1.png"
        },
        "B2": {
          "story": "你给干部少量物资补贴，群众得知后产生不满情绪。",
          "options": [
            {
              "key": "A",
              "text": "立刻调整，物资统一平均分配",
              "deduction": "你选择了：立刻调整，物资统一平均分配",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "减少干部补贴，维持现有规则",
              "deduction": "你选择了：减少干部补贴，维持现有规则",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "无视群众意见，保持原有分配",
              "deduction": "你选择了：无视群众意见，保持原有分配",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/zhang-qide-r3-B2.png"
        },
        "B3": {
          "story": "你优先给本部门分配物资，督查组上门核查账目与物资台账。",
          "options": [
            {
              "key": "A",
              "text": "主动认错，重新公平分配物资",
              "deduction": "你选择了：主动认错，重新公平分配物资",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "拒不整改，认为干部理应优待",
              "deduction": "你选择了：拒不整改，认为干部理应优待",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "收回多余物资，全部补给群众",
              "deduction": "你选择了：收回多余物资，全部补给群众",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/zhang-qide-r3-B3.png"
        },
        "C1": {
          "story": "你拒绝客商贿赂，对方多次上门以生活用品拉拢你。",
          "options": [
            {
              "key": "A",
              "text": "始终坚决回绝，上报督查组",
              "deduction": "你选择了：始终坚决回绝，上报督查组",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "收下物资后上交公家",
              "deduction": "你选择了：收下物资后上交公家",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "悄悄收下留作自用",
              "deduction": "你选择了：悄悄收下留作自用",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/zhang-qide-r3-C1.png"
        },
        "C2": {
          "story": "你对虚报一事犹豫不决，客商不断抬高分成诱惑你。",
          "options": [
            {
              "key": "A",
              "text": "主动上报，杜绝违规交易",
              "deduction": "你选择了：主动上报，杜绝违规交易",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "拖延答复，不接受也不举报",
              "deduction": "你选择了：拖延答复，不接受也不举报",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "答应客商，开展虚假报账",
              "deduction": "你选择了：答应客商，开展虚假报账",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/zhang-qide-r3-C2.png"
        },
        "C3": {
          "story": "你和客商串通虚报钨砂账目，缺口越来越大，审计即将来临。",
          "options": [
            {
              "key": "A",
              "text": "主动坦白，补齐公款接受处分",
              "deduction": "你选择了：主动坦白，补齐公款接受处分",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "销毁单据掩盖违纪行为",
              "deduction": "你选择了：销毁单据掩盖违纪行为",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "终止合作，全额退还非法所得",
              "deduction": "你选择了：终止合作，全额退还非法所得",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/zhang-qide-r3-C3.png"
        }
      },
      "endingRules": [
        {
          "id": "赤胆守廉者",
          "rule": "三轮全部【正向】",
          "summary": "身为苏区物资大管家，手握外贸大权却一生节俭、公私分明，平衡军需与民生，是青年干部修身立业的标杆。",
          "image": "shared/assets/history-choice/endings/zhang-qide-赤胆守廉者.png"
        },
        {
          "id": "迷途知返者",
          "rule": "仅有1次【摇摆】，无【失范】",
          "summary": "偶尔会考虑自身与同事便利，但能及时修正，守住廉洁大方向。",
          "image": "shared/assets/history-choice/endings/zhang-qide-迷途知返者.png"
        },
        {
          "id": "底线摇摆者",
          "rule": "1次【失范】或0次【失范】且多次【摇摆】",
          "summary": "容易被生活、人情影响，在公私利益之间难以坚定立场，需持续强化纪律意识。\n两次及以上【失范】→【初心失守者】\n总结：利用管理物资、外贸的便利谋取便利，违背苏区财经干部廉洁准则。",
          "image": "shared/assets/history-choice/endings/zhang-qide-底线摇摆者.png"
        }
      ],
      "portrait": "shared/assets/history-choice/scenes/zhang-qide-r1.png"
    },
    {
      "id": "mao-zemin",
      "name": "毛泽民",
      "title": "中华苏维埃国家银行行长，苏区金融负责人",
      "intro": "红色财经奠基人，严守财务纪律，倡导“不乱花一个铜板”，打造廉洁苏区金融体系",
      "round1": {
        "story": "战时财政极度紧张，有部门负责人想要申请公款宴请上级领导，拿着报销单据找到你审批。",
        "options": [
          {
            "key": "A",
            "text": "默许审批，人情往来难以避免",
            "deduction": "放任公款吃喝，助长铺张浪费风气，破坏财务制度。",
            "mark": "失范",
            "branch": "A",
            "deductionImage": "shared/assets/history-choice/deductions/mao-zemin-r1-A.png"
          },
          {
            "key": "B",
            "text": "坚决驳回，明令禁止任何公款招待",
            "deduction": "严守财务红线，带头践行艰苦奋斗作风。",
            "mark": "正向",
            "branch": "B",
            "deductionImage": "shared/assets/history-choice/deductions/mao-zemin-r1-B.png"
          },
          {
            "key": "C",
            "text": "不安排饭菜，仅批准提供白开水",
            "deduction": "有所约束，但未从制度层面彻底杜绝公款接待。",
            "mark": "摇摆",
            "branch": "C",
            "deductionImage": "shared/assets/history-choice/deductions/mao-zemin-r1-C.png"
          }
        ],
        "sceneImage": "shared/assets/history-choice/scenes/mao-zemin-r1.png"
      },
      "round2": {
        "A": {
          "story": "账务审计时，你发现多笔小额不明支出，金额不大，下属劝说不必深究，避免得罪各部门干部。",
          "options": [
            {
              "key": "A",
              "text": "不予追查，小事无需较真",
              "deduction": "放宽财务审批红线，默许公款吃喝，会带动全苏区铺张浪费风气，破坏艰苦奋斗的财务制度。",
              "mark": "失范",
              "node": "A1",
              "deductionImage": "shared/assets/history-choice/deductions/mao-zemin-r2-A-A.png"
            },
            {
              "key": "B",
              "text": "逐项彻查，完善财务监管制度",
              "deduction": "坚守金融监管底线，从源头杜绝公款浪费，带头树立极简公务接待标准。",
              "mark": "正向",
              "node": "A2",
              "deductionImage": "shared/assets/history-choice/deductions/mao-zemin-r2-A-B.png"
            },
            {
              "key": "C",
              "text": "口头提醒，不落地核查整改",
              "deduction": "当下克制公款支出，但未从制度层面全面管控，仅靠个人约束，存在监管漏洞，底线存在松动。",
              "mark": "摇摆",
              "node": "A3",
              "deductionImage": "shared/assets/history-choice/deductions/mao-zemin-r2-A-C.png"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/mao-zemin-r2-A.png"
        },
        "B": {
          "story": "兄长毛泽东前来银行视察工作，身边工作人员提议用好茶、饭菜招待主席，体现重视。",
          "options": [
            {
              "key": "A",
              "text": "仅简单提供茶水，不搞特殊伙食",
              "deduction": "一视同仁，不利用亲属身份搞特权，公私清晰。",
              "mark": "正向",
              "node": "B1",
              "deductionImage": "shared/assets/history-choice/deductions/mao-zemin-r2-B-A.png"
            },
            {
              "key": "B",
              "text": "简单准备家常饭菜接待",
              "deduction": "顾及亲属情面，轻微突破节俭标准。",
              "mark": "摇摆",
              "node": "B2",
              "deductionImage": "shared/assets/history-choice/deductions/mao-zemin-r2-B-B.png"
            },
            {
              "key": "C",
              "text": "置办丰盛餐食热情招待",
              "deduction": "亲属特殊化，破坏公平财务规矩。",
              "mark": "失范",
              "node": "B3",
              "deductionImage": "shared/assets/history-choice/deductions/mao-zemin-r2-B-C.png"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/mao-zemin-r2-B.png"
        },
        "C": {
          "story": "有熟人找到你，希望利用银行职权低息私人贷款补贴家庭。",
          "options": [
            {
              "key": "A",
              "text": "严格拒绝，公私借贷完全分离",
              "deduction": "坚守金融纪律，杜绝权力私用。",
              "mark": "正向",
              "node": "C1",
              "deductionImage": "shared/assets/history-choice/deductions/mao-zemin-r2-C-A.png"
            },
            {
              "key": "B",
              "text": "内心犹豫，拖延不予答复",
              "deduction": "碍于人情难以果断拒绝，立场摇摆。",
              "mark": "摇摆",
              "node": "C2",
              "deductionImage": "shared/assets/history-choice/deductions/mao-zemin-r2-C-B.png"
            },
            {
              "key": "C",
              "text": "破例发放小额低息贷款",
              "deduction": "利用职务便利给熟人特殊优待，违反制度。",
              "mark": "失范",
              "node": "C3",
              "deductionImage": "shared/assets/history-choice/deductions/mao-zemin-r2-C-C.png"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/mao-zemin-r2-C.png"
        }
      },
      "round3": {
        "A1": {
          "story": "长期放松小额账目核查，多个部门出现小额贪污、虚报现象。",
          "options": [
            {
              "key": "A",
              "text": "继续放宽监管",
              "deduction": "你选择了：继续放宽监管",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "全面清查，从严追责整改",
              "deduction": "你选择了：全面清查，从严追责整改",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "仅严查大额支出，小额不再管控",
              "deduction": "你选择了：仅严查大额支出，小额不再管控",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/mao-zemin-r3-A1.png"
        },
        "A2": {
          "story": "你彻查所有不明支出，多名干部被追责，有人指责你过于严苛。",
          "options": [
            {
              "key": "A",
              "text": "坚持常态化严格审计",
              "deduction": "你选择了：坚持常态化严格审计",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "适当放宽小额支出审核",
              "deduction": "你选择了：适当放宽小额支出审核",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "为缓和关系降低监管标准",
              "deduction": "你选择了：为缓和关系降低监管标准",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/mao-zemin-r3-A2.png"
        },
        "A3": {
          "story": "你只口头提醒不核查，账目漏洞持续扩大，群众反映银行管理松散。",
          "options": [
            {
              "key": "A",
              "text": "立刻开展全面账务清查",
              "deduction": "你选择了：立刻开展全面账务清查",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "选择性抽查部分账目",
              "deduction": "你选择了：选择性抽查部分账目",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "无视群众反馈，维持现状",
              "deduction": "你选择了：无视群众反馈，维持现状",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/mao-zemin-r3-A3.png"
        },
        "B1": {
          "story": "你只用白开水接待主席，其他干部见状纷纷效仿，苏区公款浪费大幅减少。",
          "options": [
            {
              "key": "A",
              "text": "出台制度固定极简接待标准",
              "deduction": "你选择了：出台制度固定极简接待标准",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "仅高层来访简化，普通干部正常接待",
              "deduction": "你选择了：仅高层来访简化，普通干部正常接待",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "后续逐步放宽接待要求",
              "deduction": "你选择了：后续逐步放宽接待要求",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/mao-zemin-r3-B1.png"
        },
        "B2": {
          "story": "你准备家常饭菜接待，其他部门纷纷效仿增加接待开销。",
          "options": [
            {
              "key": "A",
              "text": "统一出台禁令，取消干部招待餐",
              "deduction": "你选择了：统一出台禁令，取消干部招待餐",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "限制接待标准，小幅压缩开销",
              "deduction": "你选择了：限制接待标准，小幅压缩开销",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "放任各部门自主安排接待",
              "deduction": "你选择了：放任各部门自主安排接待",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/mao-zemin-r3-B2.png"
        },
        "B3": {
          "story": "你置办丰盛餐食，各部门争相效仿，银行经费消耗激增。",
          "options": [
            {
              "key": "A",
              "text": "立刻出台禁令，追回超标开销",
              "deduction": "你选择了：立刻出台禁令，追回超标开销",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "维持原有接待方式",
              "deduction": "你选择了：维持原有接待方式",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "全面取消所有公款接待",
              "deduction": "你选择了：全面取消所有公款接待",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/mao-zemin-r3-B3.png"
        },
        "C1": {
          "story": "你拒绝熟人贷款请求，对方多次上门求情，甚至赠送礼品。",
          "options": [
            {
              "key": "A",
              "text": "坚决不收礼品，上报组织",
              "deduction": "你选择了：坚决不收礼品，上报组织",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "收下礼品后上交公家",
              "deduction": "你选择了：收下礼品后上交公家",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "私下收下礼品默许贷款",
              "deduction": "你选择了：私下收下礼品默许贷款",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/mao-zemin-r3-C1.png"
        },
        "C2": {
          "story": "你迟迟不答复贷款申请，熟人四处散播你不近人情的言论。",
          "options": [
            {
              "key": "A",
              "text": "坚守制度，耐心做好解释",
              "deduction": "你选择了：坚守制度，耐心做好解释",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "发放极小额度贷款平息矛盾",
              "deduction": "你选择了：发放极小额度贷款平息矛盾",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "直接破例发放大额贷款",
              "deduction": "你选择了：直接破例发放大额贷款",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/mao-zemin-r3-C2.png"
        },
        "C3": {
          "story": "你给熟人发放低息贷款，其他群众纷纷要求同等优待。",
          "options": [
            {
              "key": "A",
              "text": "收回贷款，统一执行标准",
              "deduction": "你选择了：收回贷款，统一执行标准",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "全面放开私人低息贷款",
              "deduction": "你选择了：全面放开私人低息贷款",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "取消特殊优待，公开金融规则",
              "deduction": "你选择了：取消特殊优待，公开金融规则",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/mao-zemin-r3-C3.png"
        }
      },
      "endingRules": [
        {
          "id": "赤胆守廉者",
          "rule": "三轮全部【正向】",
          "summary": "红色金融奠基人，一分铜板不乱花，制度面前人人平等，用严格财务纪律守护苏区家底。",
          "image": "shared/assets/history-choice/endings/mao-zemin-赤胆守廉者.png"
        },
        {
          "id": "迷途知返者",
          "rule": "仅有1次【摇摆】，无【失范】",
          "summary": "偶尔顾及人情，但始终守住制度底线，能及时完善监管、纠正问题。",
          "image": "shared/assets/history-choice/endings/mao-zemin-迷途知返者.png"
        },
        {
          "id": "底线摇摆者",
          "rule": "1次【失范】或0次失范且多次【摇摆】",
          "summary": "容易被人情、人际关系左右，财务监管标准忽松忽紧，制度意识不足。",
          "image": "shared/assets/history-choice/endings/mao-zemin-底线摇摆者.png"
        },
        {
          "id": "初心失守者",
          "rule": "两次及以上【失范】",
          "summary": "放松财务管控、为特权开绿灯，破坏苏区廉洁金融体系。",
          "image": "shared/assets/history-choice/endings/mao-zemin-初心失守者.png"
        }
      ],
      "portrait": "shared/assets/history-choice/scenes/mao-zemin-r1.png"
    },
    {
      "id": "he-shuheng",
      "name": "何叔衡",
      "title": "临时最高法庭主席，苏区反腐“包公”",
      "intro": "“苏区包公”，铁面反腐，不惧恐吓威胁，坚决查处党内贪腐分子，守护苏区清风正气",
      "round1": {
        "story": "你查办干部谢步升贪污物资大案，嫌疑人背后势力寄送恐吓信，扬言报复你与家人，逼迫你停止调查。",
        "options": [
          {
            "key": "A",
            "text": "心生畏惧，暂停案件查办",
            "deduction": "向黑恶势力妥协，放弃反腐职责，辜负群众信任。",
            "mark": "失范",
            "branch": "A",
            "deductionImage": "shared/assets/history-choice/deductions/he-shuheng-r1-A.png"
          },
          {
            "key": "B",
            "text": "毫不退缩，顶住威胁坚持彻查到底",
            "deduction": "一身正气，以群众利益为先，不惧打击报复。",
            "mark": "正向",
            "branch": "B"
          },
          {
            "key": "C",
            "text": "放缓办案速度，暗中低调取证",
            "deduction": "有反腐决心，但斗争勇气不足，选择妥协迂回。",
            "mark": "摇摆",
            "branch": "C",
            "deductionImage": "shared/assets/history-choice/deductions/he-shuheng-r1-C.png"
          }
        ],
        "sceneImage": "shared/assets/history-choice/scenes/he-shuheng-r1.png"
      },
      "round2": {
        "A": {
          "story": "群众得知你因恐吓放弃查贪，纷纷上门请愿，希望法庭主持公道、惩处蛀虫。",
          "options": [
            {
              "key": "A",
              "text": "坚持搁置案件，不予受理群众诉求",
              "deduction": "无视群众诉求，彻底放弃监督职责，助长基层贪腐风气扩散。",
              "mark": "失范",
              "node": "A1",
              "deductionImage": "shared/assets/history-choice/deductions/he-shuheng-r2-A-A.png"
            },
            {
              "key": "B",
              "text": "重启调查，顶住压力完整查办案件",
              "deduction": "及时自省纠错，依靠群众线索深挖违纪事实，重新扛起反腐重任。",
              "mark": "正向",
              "node": "A2",
              "deductionImage": "shared/assets/history-choice/deductions/he-shuheng-r2-A-B.png"
            },
            {
              "key": "C",
              "text": "简单从轻处理，草草结案了事",
              "deduction": "迫于压力简化办案流程，惩处标准大幅缩水，执纪尺度摇摆不定。",
              "mark": "摇摆",
              "node": "A3",
              "deductionImage": "shared/assets/history-choice/deductions/he-shuheng-r2-A-C.png"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/he-shuheng-r2-A.png"
        },
        "B": {
          "story": "查办高级干部左祥云贪污基建公款案时，部分领导批判你小题大做，要求放宽处理、保全干部脸面。",
          "options": [
            {
              "key": "A",
              "text": "置个人批判于不顾，坚持依法严惩",
              "deduction": "以政权安危为重，反腐不分职位高低。",
              "mark": "正向",
              "node": "B1",
              "deductionImage": "shared/assets/history-choice/deductions/he-shuheng-r2-B-A.png"
            },
            {
              "key": "B",
              "text": "适当减轻处罚，平衡各方意见",
              "deduction": "顾及上层看法，反腐标准有所退让。",
              "mark": "摇摆",
              "node": "B2",
              "deductionImage": "shared/assets/history-choice/deductions/he-shuheng-r2-B-B.png"
            },
            {
              "key": "C",
              "text": "听从意见撤销立案，不再追究",
              "deduction": "屈服于压力，放弃反腐职责。",
              "mark": "失范",
              "node": "B3",
              "deductionImage": "shared/assets/history-choice/deductions/he-shuheng-r2-B-C.png"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/he-shuheng-r2-B.png"
        },
        "C": {
          "story": "多起账目舞弊、物资侵占案件办结后，部分干部提议放松检察监管，减少巡查频次。",
          "options": [
            {
              "key": "A",
              "text": "坚决拒绝，保持常态化监督核查",
              "deduction": "居安思危，持续筑牢防腐防线。",
              "mark": "正向",
              "node": "C1"
            },
            {
              "key": "B",
              "text": "适度减少巡查频次，简化流程",
              "deduction": "斗争意识弱化，监管力度下降。",
              "mark": "摇摆",
              "node": "C2"
            },
            {
              "key": "C",
              "text": "全面放宽监管，减少约束条款",
              "deduction": "放松制度防线，给贪腐留下空间。",
              "mark": "失范",
              "node": "C3"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/he-shuheng-r2-C.png"
        }
      },
      "round3": {
        "A1": {
          "story": "你长期搁置贪腐案件，苏区物资贪污、账目舞弊现象越来越多。",
          "options": [
            {
              "key": "A",
              "text": "持续放松反腐查处",
              "deduction": "你选择了：持续放松反腐查处",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "全面重启反腐专项整治",
              "deduction": "你选择了：全面重启反腐专项整治",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "仅查处小额违纪，大案不予过问",
              "deduction": "你选择了：仅查处小额违纪，大案不予过问",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/he-shuheng-r3-A1.png"
        },
        "A2": {
          "story": "你重新启动案件，顶住所有威胁依法惩处贪污干部，震慑全区。",
          "options": [
            {
              "key": "A",
              "text": "常态化开展反腐巡查",
              "deduction": "你选择了：常态化开展反腐巡查",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "本次结案后减少案件查办力度",
              "deduction": "你选择了：本次结案后减少案件查办力度",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "后续不再触碰高层贪腐案件",
              "deduction": "你选择了：后续不再触碰高层贪腐案件",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/he-shuheng-r3-A2.png"
        },
        "A3": {
          "story": "你从轻草草结案，违纪干部未受严肃处理，群众心生不满。",
          "options": [
            {
              "key": "A",
              "text": "重新复核，从严追责",
              "deduction": "你选择了：重新复核，从严追责",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "维持轻判，简单口头警告",
              "deduction": "你选择了：维持轻判，简单口头警告",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "彻底封存卷宗不再处理",
              "deduction": "你选择了：彻底封存卷宗不再处理",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/he-shuheng-r3-A3.png"
        },
        "B1": {
          "story": "你坚持从严惩处高级贪污干部，苏区反腐风气焕然一新。",
          "options": [
            {
              "key": "A",
              "text": "持续高压常态化反腐",
              "deduction": "你选择了：持续高压常态化反腐",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "普通干部严查，高层适度宽容",
              "deduction": "你选择了：普通干部严查，高层适度宽容",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "后续减少重大贪腐案件查办",
              "deduction": "你选择了：后续减少重大贪腐案件查办",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/he-shuheng-r3-B1.png"
        },
        "B2": {
          "story": "你减轻违纪干部处罚，群众反映法庭判罚不公。",
          "options": [
            {
              "key": "A",
              "text": "重新复核，依法加重处分",
              "deduction": "你选择了：重新复核，依法加重处分",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "维持现有从轻判决",
              "deduction": "你选择了：维持现有从轻判决",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "全面放宽所有贪腐处罚标准",
              "deduction": "你选择了：全面放宽所有贪腐处罚标准",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/he-shuheng-r3-B2.png"
        },
        "B3": {
          "story": "你撤销案件不予追责，各类物资舞弊、挪用公款行为持续增多。",
          "options": [
            {
              "key": "A",
              "text": "重新立案开展全面调查",
              "deduction": "你选择了：重新立案开展全面调查",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "长期回避高层贪腐案件",
              "deduction": "你选择了：长期回避高层贪腐案件",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "建立常态化物资审计、反腐机制",
              "deduction": "你选择了：建立常态化物资审计、反腐机制",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/he-shuheng-r3-B3.png"
        },
        "C1": {
          "story": "你持续严格巡查，及时发现多起萌芽状态的违纪行为，提前制止。",
          "options": [
            {
              "key": "A",
              "text": "完善检察制度，扩大巡查范围",
              "deduction": "你选择了：完善检察制度，扩大巡查范围",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "只定期开展季度核查",
              "deduction": "你选择了：只定期开展季度核查",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "接受提议大幅减少巡查",
              "deduction": "你选择了：接受提议大幅减少巡查",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/he-shuheng-r3-C1.png"
        },
        "C2": {
          "story": "你简化巡查流程，部分基层物资账目出现监管空白。",
          "options": [
            {
              "key": "A",
              "text": "恢复高频全面巡查",
              "deduction": "你选择了：恢复高频全面巡查",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "重点抽查大额物资账目",
              "deduction": "你选择了：重点抽查大额物资账目",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "长期简化监管流程",
              "deduction": "你选择了：长期简化监管流程",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/he-shuheng-r3-C2.png"
        },
        "C3": {
          "story": "你全面放宽监管，多地货栈、贸易站出现集体虚报账目。",
          "options": [
            {
              "key": "A",
              "text": "立刻收紧监管，开展专项整顿",
              "deduction": "你选择了：立刻收紧监管，开展专项整顿",
              "mark": "摇摆"
            },
            {
              "key": "B",
              "text": "维持宽松监管模式",
              "deduction": "你选择了：维持宽松监管模式",
              "mark": "摇摆"
            },
            {
              "key": "C",
              "text": "出台严格物资审计条例常态化巡查",
              "deduction": "你选择了：出台严格物资审计条例常态化巡查",
              "mark": "摇摆"
            }
          ],
          "sceneImage": "shared/assets/history-choice/scenes/he-shuheng-r3-C3.png"
        }
      },
      "endingRules": [
        {
          "id": "赤胆守廉者",
          "rule": "三轮全部【正向】",
          "summary": "一身正气、铁面无私，不惧威胁、不畏强权，以反腐守护苏区群众与集体财产，是青年坚守正义的榜样。",
          "image": "shared/assets/history-choice/endings/he-shuheng-赤胆守廉者.png"
        },
        {
          "id": "迷途知返者",
          "rule": "仅有1次【摇摆】，无【失范】",
          "summary": "办案时会短暂权衡各方压力，但最终坚守公平正义，能够完善监督制度。",
          "image": "shared/assets/history-choice/endings/he-shuheng-迷途知返者.png"
        },
        {
          "id": "底线摇摆者",
          "rule": "1次【失范】或0次【失范】多次【摇摆】",
          "summary": "面对恐吓、高层压力容易妥协，反腐、监督的立场不够坚定。",
          "image": "shared/assets/history-choice/endings/he-shuheng-底线摇摆者.png"
        },
        {
          "id": "初心失守者",
          "rule": "两次及以上【失范】",
          "summary": "畏惧打击、顾及人情放弃执纪，放任贪腐损害红色贸易与苏区群众利益。",
          "image": "shared/assets/history-choice/endings/he-shuheng-初心失守者.png"
        }
      ],
      "portrait": "shared/assets/history-choice/scenes/he-shuheng-r1.png"
    }
  ],
  "globalEndings": {
    "赤胆守廉者": "你全程坚守廉洁底线，面对饥饿、诱惑、威胁始终不改初心，和刘启耀、张其德、毛泽民、何叔衡等苏区先辈一样，把集体、群众、革命事业放在个人得失之前。新时代青年无论今后从事什么岗位，都要守住公私边界，永葆纯粹初心。",
    "迷途知返者": "途中你曾出现短暂动摇，但能及时自省、纠正选择。成长本就是不断修正自我的过程，只要知错能改、持续锤炼思想，就能筑牢廉洁修身的根基。",
    "底线摇摆者": "面对利益、压力、人情时，你的立场容易发生偏移，公私界限模糊。今后需要加强党史学习，牢记红色财经、反腐先辈的事迹，时刻警醒自己守住纪律底线。",
    "初心失守者": "你多次突破廉洁与正义底线，看重个人安危、私利、人情而放弃集体利益。革命年代无数先辈用一生守护清风正气，我们应当以此为镜，深刻反思价值观，重塑责任与担当。"
  },
  "endingOrder": [
    "赤胆守廉者",
    "迷途知返者",
    "底线摇摆者",
    "初心失守者"
  ],
  "assetsBase": "shared/assets/history-choice",
  "teacherMode": true
}
