<sub><a href="README.md">🌐 English</a> · <b>中文</b></sub>

<div align="center">

# huashu-slide-doubao

> **豆包专用 AI 视觉物料生产 skill（seedream 5.0 生图）。**
> 说一句话 → 一份能交付的 PPT / 公众号头图 / B站封面 / YouTube 缩略图。

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Doubao Only](https://img.shields.io/badge/Runtime-Doubao%20Only-orange)](https://www.doubao.com)
[![Built-in image_gen](https://img.shields.io/badge/Uses-seedream%205.0%20Pro-blueviolet)](https://www.doubao.com)
[![No API fees](https://img.shields.io/badge/API%20fees-Zero-green)](#为什么是-豆包-only)

</div>

---

## 为什么是豆包-only？

大部分"AI PPT" skill 都会包一层 Gemini / OpenAI Image / Nano Banana API 调用——每张 slide 都要花钱。**豆包自带 `image_gen`（默认 seedream_5.0_pro 模型）**：这部分能力你的豆包会员里已经付过了。本 skill 存在的全部理由就是**用这套内置能力**，而不是再烧一遍第三方 API。

在 Claude Code / Cursor / Codex 里跑本 skill 不会有效——那里没有豆包内置 `image_gen`。这些 runtime 建议用 [`huashu-design`](https://github.com/alchaincyf/huashu-design)（HTML-native）或 [`huashu-wechat-image`](https://github.com/alchaincyf/huashu-skills)（Gemini API）。

## 它做什么

四条交付路径，全部走豆包内置 `image_gen`（seedream_5.0_pro）：

| 路径 | 产出 | 适用场景 |
|---|---|---|
| **Path 1 · AI 图片 PPT**（默认） | PPTX + HTML deck，每张 slide 是完整图片 | 演讲、课件、提案、宣传 deck |
| **Path 2 · HTML 图片 Deck** | 全屏单页演示（左右键切页） | 快速预览、网页发布、不需要 PPT 文件 |
| **Path 3 · 可编辑 HTML → PPTX** | 文字可编辑的 PPTX | **仅在**用户明说"要可编辑文字"时启用 |
| **Path 4 · 单张封面图** | 公众号 / B站 / YouTube / 小红书封面 PNG | 头条封面、视频缩略图、营销主视觉 |

## 上手

在豆包会话里：

```
用 huashu-slide-doubao 帮我做一份 10 页 PPT，主题是 [你的题目]
```

就这样。skill 会：

1. 问 1-3 个澄清问题（受众、调性、交付格式）
2. 推荐 3 个差异化设计哲学方向（Bloomberg / Field Notes / Pentagram 等）
3. 如果题目涉及具体品牌，跑核心资产协议（下载 logo / 产品图 / UI 截图 → 写项目级 `brand-spec.md`）
4. 用 `image_gen`（seedream_5.0_pro）逐页生图 → curl 下载到项目目录 → 组装 PPTX + HTML

做单张封面：

```
用 huashu-slide-doubao 帮我做一张公众号头图，主题是 [...]
```

重要单图默认生成 **3 个差异化版本**让你挑——不是"AI 觉得最好的那张"，是真的有选择。

## 安装

```bash
cd ~/.agents/skills/  # 或你的豆包 skill 目录
# 把 huashu-slide-doubao 文件夹放进去
```

或者你的豆包 skill 目录在哪就放哪。

### 可选：图床配置

如果要发布到公众号等需要永久 URL 的平台，配置 ImgBB：

```bash
cp .env.example .env
# 在 .env 里填 ImgBB key（https://api.imgbb.com 免费注册）
```

自带的 `scripts/upload_image.py` 用纯 Python stdlib，无 pip 依赖。

## 核心机制

### 🔴 默认路径锁定铁律

在豆包环境下，skill **永远默认走 Path 1（AI 图片 PPT）**。切到 Path 3（HTML / 可编辑）的**唯二**触发条件是：

1. 用户原话明说"要可编辑 PPT" / "不要图片 PPT"
2. `image_gen` 真的调用失败（≥3 次）

skill 里明确列了一份"严禁自我合理化"清单，阻止 agent 用各种借口绕开默认路径。这条规则的来源是真实踩坑——曾经有 agent 自我合理化说"内容需要严格的版本号准确性"就切到了 HTML 路线，本意是用内置生图的成本优势直接被废掉。

### 页面类型 + 密度分级

不是每张 slide 都该一样密。skill 强制 4 种页面类型：

| 类型 | 文字上限 | 必含元素 |
|---|---|---|
| 封面页（slide 01 永远是） | 标题 ≤8 字 + 副标题 ≤16 字 | 大标题 + 主视觉，不要信息块 |
| 章节扉页 | ≤30 字 | 1 句强判断 + 1 个视觉隐喻 |
| 内容页（主要） | 80-180 字典型 / 220 字上限 | 标题 + 1-3 句解释 + 2-4 标签 + 视觉 |
| 结论页 | ≤40 字 | 1 句大判断 + 1 个标志性视觉 |

skill 里明确写：**上限不是目标**——"稀疏的内容页比塞满字的内容页更专业"。

### 核心资产协议（涉及具体品牌时强制）

题目涉及具体品牌（Anthropic、Linear、你自己的公司）→ skill 跑 5 步协议：

1. 问用户手上有什么资料（logo / 产品图 / UI 截图 / brand guidelines）
2. 搜官方渠道（`<brand>.com/brand`、`/press-kit`、新闻稿、App Store）
3. `curl` 下载
4. 验证 + grep 提取色值（inline CSS / brand guidelines）
5. 写项目级 `brand-spec.md` + **强制用户确认 checkpoint** 才能开始生图

协议存在的原因是：没有真实品牌资产的封面 / deck 一定是"通用 AI 科技感"。30 分钟的资产搜集省 2 小时返工。

### Spread Frame + Mascot Continuity（吉祥物穿线）

信息手册类风格（Field Notes × Anthropic / Penguin Books / Bloomberg Businessweek）推荐两条模式：

- **Spread Frame**：所有内容页用同一个 3 元素跨页框——顶部品牌条 + 自由正文 + 底部结论条。正文随内容变，框不动。
- **Mascot Continuity**：品牌如果有吉祥物（虾 / 像素角色 / 企业 IP 形象），让 ta 在不同 slide 以不同姿态反复出现——把 deck 从"8 张独立信息图"升级成"连环画"。

两条都由真实交付验证（OpenClaw 橙皮书宣传 PPT，2026-05-23）。

### 个人品牌触发（自带花叔像素风为示例）

skill 自带 3 张花叔的像素风参考图（`assets/personal-brand/像素风头像.png` / `像素公众号头图示例.png` / `像素品牌资产.png`），作为"个人 IP 自动注入"模式的工作示例。

其他用户两种选择：

1. **替换**：把自己的 logo / 头像 / 风格示例 PNG 放进去，并改 SKILL.md 里的触发词（搜"花叔风格"）
2. **关闭**：直接删掉 `assets/personal-brand/` 目录；skill 主体功能（slides / 单图 / 品牌资产协议）完全不受影响

## 内容清单

```
huashu-slide-doubao/
├── SKILL.md                   # Agent 指令（中文，agent 双语 OK）
├── test-prompts.json          # 7 个测试 prompt，覆盖全部路径
├── assets/personal-brand/     # 3 张像素风示例资产（可换可删）
├── references/
│   ├── design-principles.md
│   ├── prompt-templates.md
│   ├── proven-styles-gallery.md
│   ├── proven-styles-snoopy.md
│   └── design-movements.md
└── scripts/
    ├── create_slides.py       # PPTX 组装（python-pptx）
    ├── image_deck_html.py     # HTML deck 组装
    ├── html2pptx.js           # Path 3 HTML → PPTX 转换
    └── upload_image.py        # ImgBB 上传（纯 stdlib，零依赖）
```

SKILL.md 里所有脚本引用都用 `[SKILL_DIR]/...` 占位符。完全 self-contained，无机器特定的绝对路径。

## 迭代历史

发布前经过 8 轮迭代，绝大部分由真实交付驱动。完整优化日志在 [darwin-skill 的 results.tsv](https://github.com/alchaincyf/darwin-skill) 里。关键学习：

- **R3 实测**：像素风触发但生图模型把花叔放在马克杯图案上而不是主角位置 → 加了"角色必须作为画面主体出现"铁律。
- **R4 实测**：重要单图默认生成 3 个差异化版本（不同设计哲学）几乎永远是值得的。
- **R6 实测**：AI 默认把每页拉到密度上限 → 加了页面类型分级 + "上限不是目标"。
- **R7 实测**：OpenClaw deck 成功 → codify 了 Spread Frame + Mascot Continuity。
- **R8 实测**：agent 自我合理化切 HTML 路线 → 加了 🔴 默认路径锁定铁律 + 禁止句式清单。

## 相关 skill

- [`huashu-design`](https://github.com/alchaincyf/huashu-design)：HTML-native 设计 skill，任何 runtime 都能用
- [`huashu-skills`](https://github.com/alchaincyf/huashu-skills)：其他 skill（AI 审校 / 选题生成 / 图片生成 等）
- [`darwin-skill`](https://github.com/alchaincyf/darwin-skill)：用来迭代本 skill 的自主优化框架

## License

MIT —— 个人和商业使用都免费，无需授权。

## 作者

[花叔 · @AlchainHust](https://x.com/AlchainHust) —— AI Native Coder，独立开发者，30 万粉自媒体。做了很多 AI skill，做了很多 AI 产品。
