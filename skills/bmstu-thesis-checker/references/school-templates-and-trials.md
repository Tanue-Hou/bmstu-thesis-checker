# 学校配置与案例交叉检测（0.2.5）

先调用 list_school_templates，再指定 template_id 或 template_path；document_kind 为 auto/vkr/nkr/dissertation。读取 [学校来源与边界](../../../docs/SCHOOL_TEMPLATES.zh.md) 和 [试用流程](../../../docs/REAL_TRIAL_WORKFLOW.zh.md)。

案例不是标准答案；原论文与TestVkr结果都可能有问题。Template.* 的 school_template_reference_not_native_proof 不得升级为原程序验证。学校院系/年份不明时保留 applicability_confirmed=false。PDF的源边距和段落属性不可可靠恢复。

使用 precise_locations 的页/bbox、XML/段落/run/表格坐标帮助查找，说明样本截断。小字号可能是公式上下标，混合字符可能是技术符号；不能直接判定为错误或人为规避查重。

原程序对照必须有真实原输出和输入/模式/build/输出哈希；未运行就写 pending_native_capture。通过 compare_native_trial.py 的结果仍需人工看完整俄文输出；不要由数量差异直接判错。

修复先预览，执行时传 expected_input_sha256，核对 plan_id。封面/前置页保护可能使原程序字号提示保留，这是有意保留人工判断。学位论文 dissertation 不接受NKR自动修复。完成副本布局QA和前后对照才称修复验证通过。不得公开真实案例内容。
