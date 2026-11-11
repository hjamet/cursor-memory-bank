# Example Red-team Report (illustrative)

> ⚠️ **诚实说明:** 这份示例跑在一篇**虚构论文**上,用来展示 red-team 报告的*结构与判断方式*,**不是真实评审结论**。出处标的是这篇虚构稿的假想位置。换成你真实的草稿,才是真结论。
>
> 虚构论文:*"AdaPrompt: Adaptive Prompt Tuning for Low-Resource Text Classification"* —— 声称一个自适应 prompt 调优法在低资源文本分类上"显著且通用地"超越现有方法。

---

### Reviewer: R1 — The Champion

**Summary.** 论文提出 AdaPrompt:在 prompt-tuning 中按每个样本难度自适应分配可学习 token 预算,在 5 个低资源分类任务上报告了相对 vanilla prompt-tuning 的提升。核心想法是"难样本多给 token"。

**Strengths.**
- 想法直观且实现轻量,自适应预算的动机讲得清楚。[§1, §3.1]
- 在 5 个数据集上都做了实验,覆盖面比不少同类工作宽。[表1]

**Weaknesses.**
1. 🟡 最强的卖点"通用"目前只由分类任务支撑,但 intro 把话说得更大。[摘要 / §1 第2段]

**Questions to authors.** 自适应预算相对"固定但更大的预算"的增量有多少?

**Ratings.**（模拟值,非真实评审）Soundness 6/10 · Presentation 7/10 · Contribution 6/10 · **Overall 6/10** · Confidence 3/5

---

### Reviewer: R2 — The Methodological Skeptic

**Summary.** 一个按样本难度分配 prompt token 预算的方法,声称在低资源分类上 SOTA。提升主要来自表1的平均分。

**Weaknesses.**
1. 🔴 **Baseline 偏弱、且躲开了最该比的对手。** 对照里只有 vanilla prompt-tuning 和 fine-tuning,没有近两年公认的强 prompt 方法(如 P-Tuning v2 类)。不比最强对手,"SOTA"无从谈起。[表1 / §4.1]
2. 🔴 **混淆变量没控住:自适应 ≠ 提升来源。** AdaPrompt 平均用了更多 token,提升可能只是"总预算更大"。缺一个"固定但等量总预算"的对照,无法把功劳归给"自适应"。[§4.2 / ⚠ MISSING]
3. 🔴 **统计不可信。** 全表单次跑、无误差棒、无显著性检验,而低资源场景方差极大;多处提升 <0.5 个点,可能是噪声。[表1 脚注 ⚠ MISSING]
4. 🟡 **"significantly" 用词没有检验支撑。** 摘要与 §5 多次用"significant",但无任何统计检验。[摘要 / §5 第1段]

**Questions to authors.** 控制总 token 预算相等后,自适应还剩多少增量?每个数字是几个 seed 的均值±方差?

**Ratings.**（模拟值,非真实评审）Soundness 3/10 · Presentation 6/10 · Contribution 4/10 · **Overall 4/10** · Confidence 4/5

---

### Reviewer: R3 · AC — The Novelty Hawk

**Summary.** 把"按难度分配资源"这一经典思路套到 prompt token 预算上。新意取决于相对已有自适应 prompt 工作的真实增量。

**Weaknesses.**
1. 🔴 **增量存疑:"这不就是 difficulty-aware allocation 换了个场景?"** related work 没讨论已有的自适应/动态 prompt 长度工作,回避了最近的对手。[§2 / ⚠ MISSING]
2. 🟡 **三条"贡献"里有注水。** 贡献2、3 基本是实验观察而非方法贡献。[§1 贡献列表]

**Ratings.**（模拟值,非真实评审）Soundness 4/10 · Presentation 6/10 · Contribution 3/10 · **Overall 4/10** · Confidence 4/5

---

## Area Chair Meta-review

**Consensus weaknesses（最危险）.**
- 🔴 提升的**归因不成立**:既没比强 baseline(R2#1),又没控总预算(R2#2),还可能是噪声(R2#3)。R2 与 R3 都指向"增量没被证明"。

**Split opinions.** R1 认为想法和覆盖面够发了;R2/R3 认为在归因与新意被证明前,结果不可信。低资源方差问题上 R2 更可能对。

**Decisive factors.**
1. 等总预算对照 + 强 baseline —— 不补,几乎必被毙。
2. 多 seed + 显著性 —— 不补,所有数字都站不住。
3. 相对已有自适应 prompt 工作的定位 —— 不补,novelty 不成立。

**Predicted outcome.** `Reject`
> ⚠️ 模拟结果,非真实评审。反映的是"以当前草稿状态会撞上哪些枪",不是判决。

**One-line verdict.** 想法不错,但提升的**因果归因**和**新意**都还没被证明,当前状态大概率被毙。

---

## Pre-submission Fix List（按优先级）

### 🔥 高影响 · 低成本
- [ ] **加"固定等量总预算"对照** [§4.2] — R2#2、AC#1。
      怎么改:加一行 baseline,总 token 预算与 AdaPrompt 平均值相等但均匀分配。这是把功劳归给"自适应"的唯一证据。
      赶得上吗:✅ 复用现有 pipeline,deadline 内可做。
- [ ] **收回过度承诺的措辞** [摘要 / §1 / §5] — R1#1、R2#4。
      怎么改:无显著性检验前,把"significantly / general"改成"consistent improvements on classification";把"通用"的话收窄到"分类任务"。
      赶得上吗:✅ 改字即可。

### 🧱 高影响 · 高成本
- [ ] **补强 baseline + 多 seed + 误差棒** [表1] — R2#1、R2#3、AC#1/2。
      怎么改:至少补一个近年强 prompt 方法;每格跑 ≥5 seed 报均值±方差,主表做显著性检验。
      赶得上吗:⏳ 需要新实验,**立刻开跑**;实在跑不全,先保证主表 + 最强对手那一格。

### 🧹 低成本打磨
- [ ] **related work 补"自适应/动态 prompt 长度"一类工作并讲清区别** [§2] — 🟡 AC#1。
- [ ] **贡献列表删注水项**,把实验观察从"贡献"挪到结果段。[§1] — 🟢 R3#2。
