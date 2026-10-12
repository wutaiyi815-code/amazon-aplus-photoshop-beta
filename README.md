# Amazon A+ Photoshop Beta

为一个或多个服装 SKU 制作北美街头风 Amazon A+，交付可编辑的 Photoshop Beta 分层 PSD、模块 PNG、长图、预览图、来源说明和可恢复的过程记录。工作流把产品事实、属性表文案、人物分组、素材来源、视觉平衡和 PSD 可编辑性纳入同一套验证。

## 基础信息

| 项目 | 内容 |
| --- | --- |
| 名称 | `amazon-aplus-photoshop-beta` |
| 类型 | Codex Skill / Photoshop Beta 制作工作流 |
| 源目录创建时间 | 2026-10-09 |
| 公开版本 | `2026.10.12` |
| 发布日期 | 2026-10-12 |
| 当前状态 | Beta；已包含自动化校验与匿名化参考快照 |

入口文件是 `SKILL.md`；工作区管理入口是 `scripts/workspace.py`；PSD 构建入口是 `scripts/build_psd.py`。

## 适用场景

适合需要 campaign、版型/细节、搭配和 creator/occasion 模块，并要求原生文字层、独立智能对象、可替换图片和可追溯来源的 A+ 制作。支持单 SKU、包含多个 SKU 的根目录，以及多次 `--source` 指定的路径列表。

不适合只改一个文字、简单缩放、无产品证据的自由创作，或不需要 Photoshop 分层交付的普通拼图。

## 严格输入要求

### SKU 目录

每个 SKU 目录必须包含且只包含一个文件名匹配 `*产品属性表*.xlsx` 的工作簿。多 SKU 根目录可以嵌套 SKU 文件夹，发现属性表后该文件夹即被视为一个 SKU。

```text
<SKU目录>/
  <SKU>产品属性表.xlsx       # 恰好一个
  <商品图、上身图和允许使用的原始图片>
  <可选子目录>
```

- 图片支持 `.png`、`.jpg`、`.jpeg`、`.webp`、`.bmp`、`.tif`、`.tiff`；程序会读取真实格式、尺寸和颜色模式。
- 默认排除 `弃用`、`过程文件`、`流程准备`、`output`、`.git`、`.cache`，以及名称以 `aplus_` 开头的旧交付目录。
- 属性表中的 Headline、Copy、标题、正文、卖点等候选会写入 `copy_candidates.json`，必须逐项在 `copy_plan.json` 中采用、修订或说明排除理由。

### 参考文档

不传 `--rules-doc` 时使用 `references/design-reference-snapshot.docx`，这是 2026-10-10 的匿名化快照。若要求最新规范，必须通过 `--rules-doc "<当前参考文档.docx>"` 指定可读 DOCX；显式文件不可用时流程会停止，不会假装读取成功。

### 模块尺寸

默认四模块：

| 模块 | 尺寸 |
| --- | --- |
| campaign | 1464×1200 |
| fit/detail | 1464×1200 |
| styling | 1464×600 |
| creator/occasion | 1464×600 |

默认总 PSD 为 1464×3600。自定义模块 JSON 必须是非空数组；每项至少包含唯一 `name`、正整数 `height`，可包含 `kind`、`width`、`people`、`looks`、`solo_each`。用于纵向合并的全部模块宽度必须一致，且宽度不超过 Photoshop PSD 限制。

### 布局 JSON

`scripts/build_psd.py` 使用经人工设计的布局 JSON。图像节点引用的素材必须已复制到当前 SKU 工作区，路径不能逃逸工作区；模块、图层类型、box、角色、原生文字和智能对象字段详见 `references/layout-schema.md`。

## 环境与依赖

- Windows 与 Adobe Photoshop (Beta)。默认探测标准安装位置，也可显式传入 Beta 可执行文件路径。
- Python 3.10+。
- Python 包：`Pillow`、`openpyxl`。
- 可选 Eagle MCP：用于只读搜索和获取人物/环境素材；也可以使用用户直接提供的素材。
- 内置图像生成工具：用于生成无排版文字的摄影素材及独立装饰元素。

```powershell
python -m pip install -r requirements.txt
```

## 基本流程

建立不覆盖源素材的工作区：

```powershell
python scripts/workspace.py init `
  --source "<SKU目录或多SKU根目录>" `
  --work-root "<独立工作目录>" `
  --output-root "<可选交付根目录>" `
  --rules-doc "<可选当前参考文档.docx>"
```

随后完成产品锁定、文案计划、人物 A/B 分组、来源记录、生成任务 checkpoint 和人工 QC；探测 Photoshop Beta 后，根据 `references/layout-schema.md` 编写布局并构建 PSD：

```powershell
python scripts/probe_beta.py --workspace "<SKU工作区>"
python scripts/build_psd.py --workspace "<SKU工作区>" --layout "<layout.json>"
python scripts/validate_delivery.py --workspace "<SKU工作区>"
python scripts/workspace.py deliver --workspace "<SKU工作区>"
```

长时间生成必须记录 run/task/session ID、输出目录和预期文件。中断后先检查已有 checkpoint 和成品，不重复提交可能仍在运行的付费任务。

## 交付物

- 总 PSD，文字为原生文字层，摄影、特写、搭配品、图标和装饰为独立智能对象。
- 各模块 PNG、长图和缩略预览图。
- `sources.md`、交付收据和 SHA-256。
- `流程准备` 中的 manifest、属性数据、文案计划、布局、提示词、检查和脚本记录。

详细设计、文案、恢复和生产规则见 `references/`。
