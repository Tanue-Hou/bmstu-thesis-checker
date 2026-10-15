# 行为重建伪源码

本文是可审阅的算法说明，**不是机器码反编译结果，也不是原作者源码**。实际可运行实现位于 scripts。真正的新版机器码反编译在 `evidence/agent-v027/decompilation/recovered_pseudocode.c`，附函数索引、调用关系和来源哈希。成功导出10,191/10,192个已发现函数；这个比例不是语义恢复完整度。build232 与230的代码节不同，历史证据不能自动移植。

```text
CHECK(path, mode, native_build, optional_school_reference):
    identify source bytes by SHA256
    parse DOCX XML / PDF spans
    DOCX: resolve defaults -> basedOn style chains -> direct properties
          enumerate structure text including tables and content controls
    identify VKR / NKR / degree dissertation
    run entry, structure, images, formatting, dictionary candidate checks
    optionally compare separate school reference configuration
    for every candidate:
        attach effective properties and reproducible source coordinates
        preserve original-program verification scope and evidence references
        classify action eligibility independently from anomaly detection
        mode mismatch -> cannot establish a thesis violation
        unconfirmed reference -> applicability review
        mixed scripts / floating pictures -> advisory
        front matter font anomaly -> role review
        otherwise -> clause and source/page review
    return all candidates, evidence limits and action summary

MASTER_WORK_NAME(cover):
    recovered build232 function 0044a748 references two VKR word lists:
        DAT_006d6ac8 = oblique phrase tokens
        DAT_006d6b0c = nominative phrase tokens
    local implementation correction: accept exact oblique phrase
        'выпускной квалификационной работе'
    do not rewrite a valid oblique phrase to satisfy the checker

PLAN_COPY(source, actions, target_font, native_build):
    require explicitly validated build / format / mode / policy
    require intact evidence, supported DOCX and permitted actions
    protect cover, fields, math, drawings, tables, headers and footers
    produce exact changes + skips + source SHA256 + deterministic plan ID

APPLY_COPY(source, plan):
    recompute source SHA256 and current plan ID; reject drift
    write uniquely named copy; preserve other ZIP parts
    recheck output; retain before/after values, hashes and change log
```

Build232 currently has four independent font boundary controls. They do not establish complex-document counting, school compliance or copy-repair equivalence. The 298 review records retain individual evidence dispositions; unresolved compliance must not be recast as passed.
