---
name: amazon-aplus-photoshop-beta
description: Create premium North American streetwear Amazon A+ from user-specified SKU folders and current reference documents, for one SKU or a batch with custom modules, researched scenes, Eagle models, and editable layered Photoshop Beta PSD delivery. Use for campaign, fit/detail, styling and creator/occasion production, not a simple resize or isolated text correction.
---

# Photoshop Beta A+ 制作

以高级北美街头潮牌视觉设计师的标准制作可编辑A+。先读实际商品与当前参考文档，说明本款计划，再执行已授权制作；不要把方案说明变成额外确认关卡。

## 范围和默认值

- 接受单SKU路径、多SKU根目录或显式路径列表，以及独立输出路径、参考文档、指定环境/人物/图片、具体模块内容与尺寸。用户当次要求优先于默认值和案例；只制作请求的模块。
- 默认文档为随 Skill 发布的[文档快照](references/design-reference-snapshot.docx)，明确是 2026-10-10 封装快照。用户通过 `--rules-doc "<当前参考文档.docx>"` 指定其他文档时替换默认值，并读取全部文字、表格及案例图片、记录哈希；指定文档不可读时不能冒充已读或退回旧快照。
- 默认四模块：campaign **1464×1200**；多视图/细节 **1464×1200**；两组搭配 **1464×600**；creator/occasion **1464×600**。总PSD **1464×3600**。用户自定义数量、宽高、合并方式时重新计算；文档尺寸示例不得覆盖用户尺寸。总PSD需统一模块宽度，默认1464，显式另指定则遵循。
- **首屏默认三人自然互动**。campaign、fit/detail、styling使用A组固定人物；**creator/occasion使用B组三位与A组及其他非creator模块不同的人物，各自制作单人素材**。同一人换发型/滤镜/动作不算新人物。默认共六个身份，**不执行“全套最多3人”**。用户指定其他人数或只做部分模块时按范围调整，不额外补齐六人。
- 模特基础形象通过 **Eagle MCP** 查找并目视选择；SKU上身图是服装/版型权威，用户指定人物身份优先。按真实可见信息和用户要求选择性别/人物，不凭文件名猜。A/B分组按SKU独立；不擅自要求跨SKU全球不重复。
- 当前默认个人练习用途：联网参考不限可商用图，记录来源。商业用途按用户要求核对实际条件，不能虚构授权。合成人物是creator-style模拟，不标作真实代言。
- **属性表中存在可用的 Headline／Copy／标题／正文／卖点等文案时，优先采用。** 不因campaign创意或SKU风格差异另写一套替换；空缺或明确不适用的部分才补写。装饰性文字可补充，不能顶替已有可用文案。按[references/copy-policy.md](references/copy-policy.md)核对来源、产品适用性与模块归属，记录修订或排除理由。
- **素材比例与背景节奏**：搭配模块放大人物与独立单品，避免主体过小；场景模块参照用户调整PSD的中等尺度、照片间距和文字区域，避免把三图放成满幅墙。超过3个模块时，每套至少一次明确肌理背景或大campaign/宽景上叠放其他图片；已有这类背景时不再叠加较大的浅色背景装饰文字。相邻模块不得复用同一肌理图或宽景campaign背景，裁切、旋转、调色、改名不算更换。按[references/visual-balance.md](references/visual-balance.md)选取参照、标记背景与验收。

## 执行

1. 用[scripts/workspace.py](scripts/workspace.py)建立单款/批量目录，抽取当前文档案例，读取每SKU的完整属性/尺码表和允许原图。默认排除`弃用`及旧交付，只读原素材。识别真实图像格式，处理伪PNG/WebP。目视读案例和素材，逐款写产品锁定：颜色、领型、拉链/纽扣、logo/刺绣、口袋、袖口、下摆、正背差异。无证据的颜色/功能不加入。
   同时审查`copy_candidates.json`并完成`copy_plan.json`；读取保留合并区域非左上角的原始单元格，不把解析丢失误判为文案空白。所有候选逐项决定采用、必要修订或有依据排除；每条采用文案映射到实际模块与文字层。用户模块与表内section不一致时明确合并/对应，不能默默丢弃。
2. 联网/Pinterest/Eagle研究场景，**把选定真实照片或用户允许的Eagle环境实际作为生成图片输入**；只找到链接不算完成。搭配品优先Aelfric Eden官网；右侧服装、裤裙、鞋必须独立商品平铺/静物，绝不裁剪模特身体代替。缺少平铺时可按确切商品证据另生成独立平铺并如实记录方法。
3. 根据商品及首屏环境制定主题、配色、人物A/B组、shot list、互动、模块信息层级、装饰语汇，遵循当前文档与[references/design-criteria.md](references/design-criteria.md)。优先审查用户明确提供的 A+ 案例目录或调整稿；未提供时使用[模块3快照](references/approved-scale/module3.png)、[模块4快照](references/approved-scale/module4.png)和[来源记录](references/approved-scale/source.json)作为比例、间距与背景克制程度参考。记录选用参考及各模块的素材占比、留白与背景方案。不得将案例的主题、配色或布局作为所有SKU固定模板。
4. 用内置生图工具生成**无排版文字的摄影素材**及独立装饰/icon，细节优先实拍。逐输入标明产品、身份、场景、动作、搭配角色。摄影清晰干净，禁止额外细碎噪点、胶片颗粒及人工脏污。超过工具参考限制时先在PS做清晰输入板；本次验证上限5张，以当前工具限制为准，不丢掉必要参考。不通过人物/产品目视QC的素材不得正式排版。
5. 按[references/photoshop-production.md](references/photoshop-production.md)探测和锁定 **Adobe Photoshop (Beta)**。用[scripts/build_psd.py](scripts/build_psd.py)及[references/layout-schema.md](references/layout-schema.md)实现逐款手工设计的布局：排版文字原生文字层；摄影、特写、搭配品、icon、装饰分别为嵌入式智能对象；保留蒙版/材质剪贴。多人照片可完整保留；不得声称照片内部人物已分别分层。位图icon需如实标注，并支持改色/替换。
6. 保存后**重开PSD**，在丢弃用副本验证每模块文字、icon改色/替换、图片替换，并记录保存后实际文字内容；目视检查全部原尺寸模块及缩略长图。按[references/visual-balance.md](references/visual-balance.md)记录素材比例、第一点的实际呈现、装饰取舍与相邻背景变化。用[scripts/validate_delivery.py](scripts/validate_delivery.py)核对这些视觉规则、属性表文案覆盖、模块归属、实际文字层内容，以及尺寸、来源、身份分组、结构报告及目视QC。文案遗漏、重复背景或视觉规则未通过不得交付；文件存在或脚本PASS不替代审美验收。
7. 用`workspace.py deliver`交付总PSD、各模块PNG、长图、缩略图、来源说明与过程清单，并核对SHA256。默认原SKU中新时间戳文件夹；指定输出根时按SKU分目录。不覆盖或移动原始素材。

## 批量、恢复和进度

读[references/batch-and-recovery.md](references/batch-and-recovery.md)。默认逐款做到交付；各SKU素材、人物、参考、提示词和作业独立。PSD在同一Beta实例串行，禁止脚本争抢活动文档。“批量”不意味着自动开子代理或改生图提供商。

昂贵阶段提交前记录提示词、输入角色、输出目录/预期文件，返回后立即写cell/run/task/session ID；完成即收集原输出并checkpoint。**每45–55秒汇报已确认状态；每次等待≤60秒。** 恢复/用户转向先查记录和现有输出，不盲目重投。三次无新证据后说明最后确认状态与失败层，保留成果，继续独立工作或提出具体缺失输入，不无限静默轮询。

修改本skill前先备份整个目录。机械步骤可复用；主题、场景、风格与布局需根据SKU重新决定。
