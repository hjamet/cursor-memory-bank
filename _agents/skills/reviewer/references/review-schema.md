# Red-team Report Schema(red-team 报告的唯一权威定义)

一份 red-team 报告 = **N 份模拟 review** + **1 份 AC meta-review** + **1 张 fix-list**。
下面定义每一块的字段、规则、空白模板和质量门。`SKILL.md` 只讲流程,字段一律以本文件为准。

报告默认存到 `redteam/<paper-slug>.md`(`<paper-slug>` = 论文短标题的 kebab-case,如 `redteam/emotion-value-updating.md`)。

---

## 出处标注规则(整份报告通用)

每一条批评、每一处"作者声称",都要能指回草稿。格式:

```
[§3.2]            指向某节
[图4 / 表2]        指向图表
[第6段 / L120]     指向段落或 .tex 行号
["原文短引 ≤15词"]  直接钉一句原话(最强,优先用)
[⚠ MISSING]       本该有、却遍寻不到 —— 缺失本身就是 finding
[⚠ 未定位]         你怀疑有问题但定位不到原文 —— 必须标这个,不许装作有出处
```

**铁律:没有出处的批评不许进报告。** 要么钉到位置,要么标 `⚠ MISSING` / `⚠ 未定位`。

---

## Weakness 分级(三色,贯穿全报告)

每条 weakness 必须标一个级别——它们修法完全不同:

| 级别 | 含义 | 典型 | 怎么修 |
|---|---|---|---|
| 🔴 **Substance** | 方法/实验**真的站不住** | 缺关键 baseline、有混淆变量、结论超出证据、无显著性检验 | 补实验 / 改方法 / 收回结论 |
| 🟡 **Misread-risk** | 其实**站得住**,但写法会**触发审稿人** | 卖点写得像过度承诺、关键澄清藏在附录、记号混乱让人误判 | 改写 / 前移澄清 / 加一句话堵枪眼 |
| 🟢 **Polish** | 表述/呈现层面 | 图太小、术语前后不一、typo、related work 漏引 | 顺手改 |

> 区分 🔴 和 🟡 是本技能最值钱的判断:🔴 要动真格(可能赶不上 deadline),🟡 往往一句话就能拆掉审稿人的枪。**别把 🟡 当 🔴 吓用户,也别把 🔴 粉饰成 🟡。**

---

## 一、单份 Review 的字段

每个审稿人格出一份。照 NeurIPS/ICLR 风格。

```markdown
### Reviewer: <R1 The Champion / R2 The Skeptic / R3·AC The Novelty Hawk>

**Summary.**
<2–4 句,用你自己的话复述这篇在做什么、怎么做、声称贡献什么。
 这段是诚意证明——复述得准,后面的批评才有分量。>

**Strengths.**
- <真实优点,带出处>。[§ / 图]
- （R1 尤其要找够;若一个像样的优点都找不到,这本身是给作者的强烈信号,直说。）

**Weaknesses.**
1. 🔴/🟡/🟢 <一句话讲清问题> — <为什么这是问题 / 审稿人会怎么想>。[出处]
2. 🔴/🟡/🟢 ...
   （每条都要：分级 + 出处。按严重度从高到低排。）

**Questions to authors.**
- <审稿人会在 rebuttal 阶段逼问的问题——这些正是 rebuttal 要提前备好弹药的点>

**Ratings.**（量表以 `reviewing-rubric.md` 第二节为准;默认 NeurIPS 量表。模拟值,非真实评审）
- Soundness:      <n>/4 — <一句话>
- Presentation:   <n>/4 — <一句话>
- Contribution:   <n>/4 — <一句话>
- **Overall:**    <n>/10 — <一句话>
- Confidence:     <n>/5
```
> 换 venue 换量表:ARR 用 Soundness/Excitement/Overall/Reproducibility;ICLR 不强制数字、答四个核心问题。详见 rubric 第二节。

---

## 二、AC Meta-review 的字段

```markdown
## Area Chair Meta-review

**Consensus weaknesses（多个审稿人都点到的 = 最危险）.**
- 🔴/🟡 <问题> — R2 与 R3 均提及。[出处]

**Split opinions（分歧点）.**
- <一个审稿人在意、另一个不在意的地方,以及谁更可能对>

**Decisive factors（真正左右结局的 2–3 条）.**
1. <这条若不解决,基本会被毙 / 这条是录用的关键支点>

**Predicted outcome.** `Reject / Borderline / Accept`
> ⚠️ 模拟结果,非真实评审。真实评审受 venue、审稿人抽样、当年竞争激烈程度影响,这里只反映"以当前草稿的状态,大概率会撞上哪些枪"。

**One-line verdict.** <一句话总判>
```

---

## 三、Fix-list 的字段(本技能的真正交付物)

把所有 weakness 收敛去重,按 **影响×成本** 排序。

```markdown
## Pre-submission Fix List（按优先级）

### 🔥 高影响 · 低成本（先改这些,最划算）
- [ ] **<动作>** [出处] — 由 <R2/R3> 提出。
      怎么改:<具体动作,如"补 §4.2 对 Strong-Baseline-X 的对比">。
      赶得上吗:✅ deadline 内可做。

### 🧱 高影响 · 高成本（尽早动手,可能需要新实验）
- [ ] **<动作>** [出处] — 由 <…> 提出。
      怎么改:<如"补一个控制了混淆变量 Z 的 ablation">。
      赶得上吗:⏳ 需要新实验 / 🛟 实在赶不上就写进 Limitations 缓冲并在 intro 收回过度承诺。

### 🧹 低成本打磨（顺手清掉,别让审稿人扣印象分）
- [ ] **<动作>** [出处] — 🟢 <如"图4 字号放大 / 统一 notation / 补引 Smith 2024">。
```

排序 / 标注规则:
- **影响** = 看 meta-review 的 decisive factors 和 consensus,不是看单个审稿人嗓门大小。
- **成本** 三档:`✅ deadline 内可做` / `⏳ 需要新实验` / `🛟 只能写进 limitations 缓冲`。
- "赶得上吗"**必须诚实**:把"需要两周新实验"标成"顺手就改",是这份报告最致命的失败。

> 说明:上面 **二、三** 是 **Mode A(审自己)** 专属产物(meta-review + fix-list)。**一(单份 review)** 两种模式通用。下面 **四** 是 **Mode B(审别人)** 专属产物。

---

## 四、Mode B:正式评审模板(可直接提交,存 `reviews/<paper-slug>.md`)

> 公正裁判口吻:专业、中性、善意。**所有 weakness 必须已过 H1–H17 防火墙。** 用具体化写法(别写"X 不清楚",写"X 缺了 Y 和 Z")。

```markdown
# Review — <paper title>
**Venue:** <NeurIPS / ICLR / ACL ARR / 期刊…>   **Reviewer aid:** paper-redteam (draft for your review & sign-off)

**Paper Summary.**
<3–5 句,用你自己的话复述问题、做法、声称的贡献。证明你读懂了。>

**Strengths.**
- <真实优点,带出处>。[§ / 图]

**Weaknesses.**（均已过公正性防火墙;按严重度排,带出处+分级）
1. 🔴/🟡 <问题> — <为什么影响 soundness/clarity/significance/originality>。[出处]

**Questions for Authors.**
- <能在 rebuttal 阶段澄清、可能改变你判断的问题>

**Suggestions（非拒稿点,纯帮作者改进）.**
- <可执行的小建议;明确标这些不计入决定>

**Ratings.**（按 venue;默认 NeurIPS。见 rubric 第二节）
- Soundness <n>/4 · Presentation <n>/4 · Contribution <n>/4 · **Overall <n>/10** · Confidence <n>/5

**Recommendation.** <Accept / Borderline / Reject> — <一两句关键理由>
```

> ⚠️ 这是**供用户审阅定稿的草稿评审**。提醒用户:对照论文核对每个 `[出处]`、为最终评分负责后再提交;打分是建议值。

---

## 质量门(交报告前逐条打勾,任一不过就回去补)

**通用(两种模式):**
1. ✅ 每条 weakness 都有出处或 `⚠ MISSING / 未定位` 标注?(无裸批评)
2. ✅ 每条 weakness 都分了级(🔴/🟡/🟢)?
3. ✅ 🔥 **每条 weakness 都过了 H1–H17 公正性防火墙?**(没有"没超 SOTA""方法太简单""有局限=有缺陷"之类不正当批评漏网)
4. ✅ 有没有为凑数硬挑的假 weakness?宁可写"该维度未发现实质问题"。
5. ✅ 每份 review 的 Summary 都能证明真读懂了(不是套话)?
6. ✅ 🔴 与 🟡 分得清?(没把一句话能拆的 🟡 当成要补实验的 🔴)

**Mode A 专项:**
7. ✅ 预测结局显式标了"模拟,非真实评审"?
8. ✅ fix-list 按"影响×成本"排序,每条都有"赶得上吗"标注?

**Mode B 专项:**
9. ✅ 口吻专业、中性、无挖苦?(守"写一份你愿收到的评审")
10. ✅ 标明了"供用户审阅定稿、打分需用户负责"?
