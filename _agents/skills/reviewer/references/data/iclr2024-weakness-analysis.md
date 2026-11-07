# 真实评审蒸馏:ICLR 2024 weakness 分析(可复现)

> 这份文件支撑 `reviewing-rubric.md` 第三·补节的"真实数据校准"表。
> 数据来自 **OpenReview 公开 API**(ICLR 评审公开),抓取日期 2026-06-23。

## 样本
- 来源:`https://api2.openreview.net`,ICLR 2024 Conference 的 `Official_Review` notes。
- 范围:前 **800 篇**投稿的全部官方评审 → **2956 份**带 `weaknesses` 字段的评审(均有 `rating`)。
- 整体平均 rating = **4.95**(ICLR 2024 录用阈值 ≈ 6)。

## 方法
1. 拉取投稿(`details=directReplies`),抽出 reply 中 invitation 含 `Official_Review` 的 note,取其 `content.weaknesses` 与 `content.rating`。
2. 把 rating 文本(如 `"6: marginally above..."`)解析成整数。
3. 用 **大小写不敏感的关键词正则**把每条 `weaknesses` 归入若干批评类型(**非语义、可多重命中**)。
4. 每类算:① 出现率(命中评审 / 全样本);② 命中评审的平均 rating;③ 与整体均分 4.95 的差(=该批评的"杀伤力")。

## 结果(按杀伤力排序)

| 批评类型 | 出现率 | 提到时均分 | vs 4.95 |
|---|--:|--:|--:|
| 数据集/任务范围窄 | 1.3% | 4.18 | −0.77 |
| 过度承诺 / claim 无支撑 | 3.0% | 4.27 | −0.68 |
| novelty 不足 / 增量 | 19.9% | 4.34 | −0.60 |
| related work / 漏引 | 18.5% | 4.44 | −0.50 |
| 无误差棒 / seed / 显著性 | 6.8% | 4.61 | −0.34 |
| 缺与 SOTA / 对手比较 | 28.7% | 4.63 | −0.31 |
| 泛化 / 过拟合 | 12.0% | 4.64 | −0.30 |
| 清晰度 / 写作 | 33.2% | 4.65 | −0.29 |
| 弱 / 缺 baseline | 18.1% | 4.65 | −0.29 |
| 理论 / 证明不足 | 16.4% | 4.69 | −0.26 |
| 强假设 | 9.4% | 4.71 | −0.23 |
| 超参敏感 | 3.6% | 4.75 | −0.19 |
| 可扩展性 / 效率 / 成本 | 16.5% | 4.82 | −0.12 |
| 缺 ablation | 8.4% | 4.83 | −0.12 |
| 实验不足 / 要更多数据集 | 3.9% | 4.92 | −0.02 |

## 结论
1. **定位类硬伤最致命**:novelty、related work、过度承诺、范围窄 → 降分最多。
2. **"没超 SOTA""该多做实验"虽常见但杀伤力小** → 经验上印证 ACL H5/H13 把它们列为不正当理由。

## 局限(诚实声明)
- **关键词非语义**:正则会错分(如 "significance" 兼指统计显著性与重要性);数字是量级参考,非精确测量。
- **相关非因果**:低分评审的 weakness 段本就更长更狠,命中率天然偏高。
- **单会议单年份**:仅 ICLR 2024 前 800 投稿;其它 venue/年份分布会变。
- 想更严谨:扩样到多年多会、改用语义分类、做回归控制评审长度。

## 复现脚本
```python
import urllib.request, json, re
# 1) 抓取
OUT="/tmp/iclr2024_reviews.jsonl"
BASE=("https://api2.openreview.net/notes?invitation="
      "ICLR.cc/2024/Conference/-/Submission&limit=100&details=directReplies&offset=")
val=lambda d,k:(d.get(k).get("value") if isinstance(d.get(k),dict) else d.get(k))
with open(OUT,"w") as f:
    for page in range(8):
        req=urllib.request.Request(BASE+str(page*100),headers={"User-Agent":"Mozilla/5.0"})
        for nt in json.load(urllib.request.urlopen(req,timeout=40)).get("notes",[]):
            for ri in nt.get("details",{}).get("directReplies",[]):
                if any("Official_Review" in iv for iv in ri.get("invitations",[])):
                    c=ri.get("content",{}); w=val(c,"weaknesses"); r=val(c,"rating")
                    if w: f.write(json.dumps({"w":w,"rating":r},ensure_ascii=False)+"\n")
# 2) 分析:见上表的类目正则,关联 rating 求均分差
```
（完整类目正则见本仓库 commit 历史 / `reviewing-rubric.md` 第三节清单。）
