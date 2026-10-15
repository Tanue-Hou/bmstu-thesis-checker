# 学校参考配置与适用边界

核查日期：2026-10-15。案例论文是待检材料，不是正确模板，不据此推断学校标准。

| 配置 | 官方出处 | 已实现的参考值 | 适用边界 |
|---|---|---|---|
| bmstu-master-reference | [硕士附件](https://e-learning.bmstu.ru/iu5/pluginfile.php/7455/mod_folder/content/0/756_Prilozheniya%20k%20Polozheniyu%20o%20VKRM.pdf?forcedownload=1)，PDF第5页，2.1 | A4；正文14pt；TNR/Arial及Liberation对应字体；1.5倍行距；首行1.25cm；左/右/上/下30/10/20/20mm | IU5站点发布的历史校级附件，SM1及当前年份适用性未确认 |
| bmstu-dissertation-reference | [学位委员会要求页面](https://mf.bmstu.ru/info/dissovet/requirements/)及[附件](https://mf.bmstu.ru/assets/info/dissovet/requirements/docs/diss_requirements.pdf)，PDF第4页 | A4；TNR14pt；1.5倍行距；左/右/上/下30/10/20/25mm | Мытищи分校委员会参考，不能直接宣称适用于所有莫斯科院系 |

[RK6毕业设计页面](https://rk6.bmstu.ru/students/дипломное-проектирование/)列出了通用DOCX模板；下载入口 archrk6.bmstu.ru/f/809404 要求校内登录，本轮未取得空白模板。未绕过登录。

上述是格式参考配置，不是完整空白模板。硕士附件包含页码等尚未实现的要求；当前不检查完整封面布局、目录对应关系、参考文献合规性。不同来源不得混成一套“鲍曼统一标准”。

原程序的 phd 对应 НКР аспиранта；候选人/科学博士学位 диссертация 另设 document_kind=dissertation。封面识别只是启发式，可显式指定；识别冲突需人工确认。不得把NKR边距25/10/20/20或修复证据转移到学位论文。

配置位于 templates/*.json，可复制到私人目录，更新适用院系、年份、来源和 targets，再通过 template_path 选择。applicability_confirmed 仅记录使用者确认，不代表签名、学校认证或原程序验证。当前所有 Template.* 提示均需人工复核，auto_repair=false；误用未知字段会报错。

PDF只测页面、字体/字号候选；不能从裁切框可靠推断原始页边距、段落行距和缩进。正文识别排除表格、标题和特殊内容，仍是启发式。字体子集、粗斜体名称归一化不证明完整字体合规。
