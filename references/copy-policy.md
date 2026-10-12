# 属性表文案优先与模块映射

属性表中可用于当前商品与请求范围的 Headline、Copy、Title、Subheadline、Tagline、正文、描述和卖点，优先作为成稿内容。视觉主题、字体、排版和装饰可以重新设计；不能为了风格差异把已有可用文案换成全套自创口号。原文空缺时才补写；额外装饰文字不替代商品标题和正文。

## 读取与适用性

`workspace.py init`以只读流式方式读取全部原始单元格，保留部分WPS文件合并区域中非左上角的文字、全部工作表和合并范围，输出`attributes.json`、`copy_candidates.json`及待审查的`copy_plan.json`。不能仅按常规A/B列或正常模式的合并锚点判断是否有文案。恢复旧工作区时用`workspace.attributes(原属性表路径)`刷新旧读取结果并重新整理文案计划；不要覆盖原Excel或已经交付的PSD来修复读取。

候选提取器支持字段式（Section1 Headline / 值）、按行标注式（Section / Headline / 值）和列式（Section / Headline列 / Copy列）。模型仍需完整读表，手工补入语义明确但未被标签识别的文案单元格；不得把自动提取列表当作完整语义理解。手工条目也使用真实`工作表!单元格`来源ID。

- 从商品原图与属性内容判断哪个工作表适用；其他商品的工作表、明显错误的功能/材质表述可排除，但逐项留下具体证据。局部冲突只处理该句，不整体弃用同section的其他可用文案。
- 默认保持原文，仅调整大小写、断行及视觉层级。必要的拼写纠正、精简、翻译或产品事实修正，保留原文来源并说明修改内容与理由；不能用“更符合风格”作为替换标题或删除正文的理由。
- 用户模块合同优先。表内版型与细节可合并进入一个用户模块，按语义映射并保留各自适用文字；场景/穿搭文案放到实际承担对应内容的模块，不凭section编号硬塞到另一个模块。请求未含尺码等内容时标记范围外，不自动增模块。
- 当前用户明确要求不显示文字、指定新文案或限制某些模块内容时遵循该要求，记录其覆盖的条目，避免与本规则冲突。

## copy_plan.json

正式生图规划与排版前逐项审查后设`reviewed=true`。每个非空候选必须有一个条目，不能只把采用的内容列出来而隐藏未采用项。

```json
{
  "reviewed": true,
  "entries": [
    {
      "id": "1-产品属性表!B25",
      "decision": "adopt",
      "placements": [
        {"module": "campaign", "layer": "Product headline", "text": "Aelfric Eden Fleece Hoodie"}
      ]
    }
  ]
}
```

`placements`可包含同模块或合并后的多个文字层，顺序拼接应覆盖原文，保留自然阅读顺序。`layer`用布局节点名或`module / 节点名`；`text`是该层最终完整内容。装饰文字、原生标题的强调副本可以增加，不要求来自属性表，但原表文案仍须在明确位置采用。

`decision=adapt`需有`reason_code`（typo / shorten / translate / product_correction / user_override）、`reason`及`evidence`，说明确切修订与依据。`decision=exclude`需有`reason_code`（product_mismatch / not_product_supported / out_of_scope / user_override）、`reason`及`evidence`。空字段不算遗漏；没有非空可用候选时仍审查空候选列表后再创作，不把占位符或另一商品信息当成可用文案。

## 检查与交付

`build_psd.py`正式A+构建前核对全部候选决策与布局中的实际文字节点。未处理、无理由修订/排除、错误模块、遗漏或替换的采用文案会阻止构建；参考板不受此关卡影响。

`verify.jsx`重开PSD，在修改测试前记录实际原生文字内容、可见性与不透明度。`validate_delivery.py`对照来源、文案计划、布局与保存后的文字层；不是只看`copy_fidelity=true`或文件存在。模型另需目视检查长文是否被遮挡、裁切或过小，以及精简是否保留必要信息；机械比对不能判断事实或审美。交付同时保存文案候选、计划与检查结果，并校验文案证据文件未在验收后变动。
