# 请求配置与自由布局

自然语言请求由主模型转成任务配置，不要求用户写JSON。每个SKU的主题、构图、留白、框形、景别、装饰和文字排版由主模型设计；文字内容遵循[copy-policy.md](copy-policy.md)，属性表内可用文案优先。构建器仅提供机械能力，不含任何固定SKU或唱片店模板。

## 请求

request.json可以有 sources 路径列表、output_root、rules_doc、usage、modules、sku_overrides。modules中每项有唯一name、kind、width（默认1464）、height，按内容指定people和looks。kind可为campaign、fit_detail、styling、creator_occasion、creator、occasion或custom。people可覆盖默认；A组与B组互斥。只做不含人物模块可设people=0。sku_overrides以完整SKU目录名为键，支持逐SKU不同模块。配置参数与自然语言冲突时用最新用户明确要求；堆叠PSD需要统一模块宽度。

例如两模块：campaign高度800、people3；creator_occasion高度600、people3、solo_each=true；总高1400。没有fit或styling时不要自动补出来。默认四模块1200/1200/600/600。

## layout.json

正式A+构建前必须完成`copy_plan.json`审查。`build_psd.py`检查源文案是否逐项决定、是否放入指定模块的实际文字节点；参考板`kind=reference_board`不走正式文案验收。

按[visual-balance.md](visual-balance.md)标记图片背景：`design_role=background_texture/background_campaign`及稳定的`background_source_id`；全模块图片必须分类。较大浅色背景装饰字标记`design_role=decorative_large_pale_type`，普通Headline/Copy不作这种标记。相邻背景、装饰冲突及超过3模块的第一点要求在构建时检查；导出后另写`checks/visual_balance.json`实际目视记录，验证器才允许交付。自定义模块沿用用户合同，不固定参考稿像素尺寸。

顶层width默认取manifest用户合同（通常1464），output_stem安全文件名，modules顺序/name/height需匹配用户解析后的manifest；每模块含layers数组。kind=reference_board时可采用独立宽度，专用于参考板，不当成正式A+。元素坐标为模块局部坐标，构建时自动加模块起始y；负y或超过height可实现越框，必须目视审查切片。文字position是基线，不是左上角。

节点：

- text：name、text、position=[x,y]、size、color六位hex、font（PS PostScript名）、bold、leading、tracking。原生文本的换行用实际CR/\r；不可保存成两个字符反斜杠+r。
- image：name、file（本SKU工作区相对路径）、box=[x,y,w,h]、fit=cover/contain/stretch、role=photo/detail/product/icon/decor。人物与服装用cover/contain；stretch仅用于材质框/标签。crop_fraction可为alpha包围盒中的[x,y,w,h]归一化裁切，不用于拆透明合图。
- shape：name、box、color、purpose=background/rule；用于底色或极简分割线。装饰框/icon须用真实材质image，不能用此节点画卡通资产。
- group：name、offset=[x,y]、layers；可整体angle旋转，实现轻微拼贴。节点还可有opacity、blend（NORMAL/MULTIPLY/SCREEN/OVERLAY/SOFTLIGHT/COLOR/LUMINOSITY）、clip_to_previous。
- mask_points：image可带模块局部多边形点数组，用于圆角/异形裁切。圆形可用足够多点逼近。不变形服装来适配图框。

同模块图层名唯一；构建器加“模块名 / ”前缀。图片均先收集到当前SKU工作区，不引用其他SKU目录；参数化输入板也按来源记录。只靠新的裁切不算新scene。

crop_assets用于PS像素裁切：source、output（本SKU工作区相对路径）、bounds=[left,top,right,bottom]。从原图副本裁切，不改/关闭用户原件。需要先规范化错误扩展名/真实编码。全新输出不得无声明覆盖其他任务的素材。

## manifest补充

workspace.py update --workspace WS --patch patch.json 更新人工分析：product_lock，model_identities（id、group=A/B、eagle_id/source），scene_research（id、selected、file、source_url或eagle_id、used_in），pairing_products（真实URL及独立图方法），modules内source_ids/scene_ids/qc。每模块qc记录 product_fidelity、scene_logic、visual_variety、typography_readability、layer_editability，全部由实际审查决定，不提前标true。

sources.md由主模型写最终来源、生成/实拍区分、人物设定、材质与字层说明和限制。验证脚本通过后workspace.py deliver负责实际复制及哈希检查。

pairing_products每项包含file、source_url或用户原始source_path，以及method：official_flatlay、official_stilllife、source_flatlay、generated_independent_flatlay之一。裁下上身商品不属于这些方法。缺少明确商品证据不能以生成平铺兜底。jobs默认required=true；未完成、失败或未知的必需作业会阻止交付。只有明确不被采用的可选变体才可记录required=false，仍保留其handle和状态。

人物证据：model_identities每项id为稳定人物标识，不是换张照片就换人；优先以identity_id或identity_name去重，并记录group、eagle_id或user_specified。每个涉及人物的模块增加people_assets=[{file,person_ids}]；campaign主照片应含people指定人数且qc.interaction=true；creator模块应有people个不同文件，每文件person_ids仅一位B组人物。通过清晰脸参考和目视确认身份，不能凭库标签或换发型声称换人。

生成作业references是[{file,role,source_ids}]，场景输入角色含scene（如identity_scene）；合并参考板也需source_ids保留所含实际场景ID。scene_research的selected=true、file存在、used_in包含对应模块，仅有网页URL而未输入图片不能过验收。criteria_read只在完整文字、表格、案例已读后设true。

scene_research用setting_id表示稳定环境，而非单张照片ID；同一地点的不同角度仍用同一setting_id。creator/occasion不得与其他主模块复用同一环境或同一源图。不同文件名、裁切或照片ID不能冒充不同场景。
