# Photoshop Beta 通道与分层

优先用load_workspace_dependencies发现当前捆绑Python（需Pillow/openpyxl）及运行环境，不依赖上一台电脑的Python路径。默认内置生图；失败时记录并说明，不因批量或参考限制自动切换收费提供商。用户明确指定其他提供商时再按相应工具/skill执行。

当前验证安装为 C:\Program Files\Adobe\Adobe Photoshop (Beta)\Photoshop.exe，27.5的BridgeTalk specifier为 photoshop-200.064；这不是未来版本常量。

1. 运行 probe_beta.py --workspace WS，可指定 --beta-executable。由 launch_beta.ps1 -Script WS\scripts\probe_beta.jsx 启动，读取 checks/beta_probe.json，确认实际路径、版本、specifier和字体。新启动Beta需要等待其完成加载，保持有界检查。
2. build_psd.py --workspace WS --layout WS\layout.json 读取已验证specifier生成专用JSX。不能使用泛化 #target photoshop，它曾路由到Photoshop2020。所有脚本有安装路径guard，误路由时不得修改文档。
3. 用 launch_beta.ps1 串行启动build.jsx，等待 build_status.json明确completed；再启动verify.jsx，等待editability.json为verified。Start-Process仅表示提交，不表示完成。字体不存在时修正方案，不静默替换。程序不可用时报告实际失败层，不降级2020。

若自动审查拒绝混合命令，将写文件、下载和启动拆成独立有界操作，不绕过审查。COM ProgId存在不代表Version/DoJavaScript可用；不能无限重试COM。隐藏启动，不退出应用或关闭用户文档。

## 图层和源图

- 排版文字原生type，显式leading防止继承旧行距；72ppi下字号数值对应像素。字体需在Beta probe中实际存在。
- 图片/实拍细节/商品/icon/装饰分别嵌入式智能对象，保留裁切蒙版。照片内刺绣/招牌不能误称原生字。标题材质独立剪贴，摄影不叠颗粒滤镜。
- 位图icon可以改色或替换，不声称矢量。装饰用实拍/生成物料；基础填充、细线、裁切蒙版可原生制作，但不以基本形状画卡通贴纸。
- 透明合图先按源图像像素坐标拆单人物/单物料。Layer.bounds是alpha包围盒，不能把其分数坐标当作整张透明合图的像素坐标。实体图框先裁紧边距，可单独stretch适配；人物/服装照片不拉伸。
- 伪PNG/WebP先检测实际格式，以像素保持的格式规范化处理，不重复生图。创意编辑、抠图和换装用PS或内置生图。

## Eagle和输入板

优先发现可调用Eagle读工具。没有按钮不等于无服务；可用 eagle_read.py --out tools.json 通过现有配置initialize/tools-list，再按返回schema填写call JSON。脚本不打印凭据URL，不修改库。连接拒绝时检查Eagle/插件、发现安装位置后隐藏启动，做有界恢复；不能拿旧图冒充本次MCP查询。

工具参考上限目前验证为5张，以当前工具为准；超过时PS做原始身份/产品/搭配板，脸和商品结构必须清楚，输入角色逐格说明。不把身份服装当作要穿的商品。保存原始输出并登记来源。材质sheet可逐元素PS拆分，保留实际alpha。

## 编辑验收

verify.jsx重开已保存PSD的临时文件副本：修改所有原生排版字、替换至少一张独立图片、改色/替换至少一个icon；测试副本丢弃，最终文件不被修改。逐模块原尺寸及缩略长图人工检查，特别是字体、产品、噪点、图框、跨界元素。原生图层测试不能替代视觉QC。
