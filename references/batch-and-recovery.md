# 单SKU、批量与恢复

## 指定输入

使用用户的SKU路径、含多个SKU的根目录或显式列表；`workspace.py init --source PATH`可重复。可指定`--output-root`，否则在每个原SKU目录创建新交付文件夹；过程文件留在用户工作区。用`--modules modules.json`或`--config request.json`描述不同模块。config可含`sources`、`output_root`、`rules_doc`、`modules`、`sku_overrides`（以完整SKU目录名为键）。最新自然语言指令需同步到请求配置，不依赖用户一定提供JSON。

根目录自动发现含`*产品属性表*.xlsx`的SKU，跳过旧交付/弃用/过程目录。遇到无属性表、多个候选表或路径歧义时，保留原图、列出具体情况，由主模型判断或询问，不把其他SKU表配过来。

## 每款状态

manifest保存源目录、最新文档哈希、产品锁、原图分类、人物A/B身份与Eagle来源、场景照片实际输入、搭配来源、手工视觉计划、模块尺寸、生成输入/提示词/handles、PSD/PNG输出及QC证据。批量根目录保存每款workspace、状态与交付目录。

每款开始前可执行 workspace.py refresh-rules --work-root ROOT，比对当前原文档哈希；发生更新时重新抽取内容/案例，未交付SKU标criteria_changed并保留旧规则与现有作业，要求重新阅读。已交付款保留原生产依据，不在后台擅自重做。

默认逐SKU：读取→研究/计划→生成→目视QC→Beta排版→重开编辑验证→交付；失败的款记录具体失败层，继续不依赖它的其他款，最终报告成功/失败/未完成数量。不要因首款成功就声称整批完成。只做用户模块，不隐性补全四模块。

远程生成可在工具允许时有界并发，但所有参考、人物与结果必须按SKU归属，提交/状态写入串行；**同一Photoshop实例的构建/验证/拆图串行**。不自动使用第三方API、子代理或外部发布。

## 有状态生成

1. 提交前将prompt保存UTF-8文件；在`workspace.py job`登记job key、输入文件与角色、预期输出、提交时间。
2. 返回cell/provider/task/session ID后立即更新handle。等待≤60秒，每45–55秒给用户已确认事件和下一步，不把采样或未查明延迟说成工具运行时长。
3. 完成后复制原生成文件到本SKUassets，登记原路径和相对路径、尺寸、哈希、QC；内置生图原件留在默认目录。明确成功文件再进入下一阶段。
4. 中断恢复先读取manifest/jobs、日志、目标文件、已记录handle。callback丢失但可靠完成文件已存在时直接继续，不重复收费生成。未知状态不得自动重投；先恢复或说明需要人工核实。
5. 三次有界检查都无新证据：查现有任务状态、预计输出和相关进程CommandLine，区分仍在运行、连接丢失、认证失败、进程停止。不能靠Python进程名字断言是本任务，更不能批量杀进程。

Beta通过CLI提交JSX也属异步：先记录脚本/日志/预期文件，启动后读`build_status.json`直到明确completed/error；等待文件就绪再启动下一个脚本，不能将`Start-Process`成功当作构建完成。

## 交付和恢复

`validate_delivery.py`通过并有真实目视QC后才执行`workspace.py deliver`。复制后比较SHA256，再标delivered。重新连接后若已有交付回执，检查其文件一致性，不重做生图。最终展示预览、PSD链接和真实交付路径；如有未完成款单独说明。
