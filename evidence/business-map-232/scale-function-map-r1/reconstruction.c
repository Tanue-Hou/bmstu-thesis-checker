/* Analyst reconstruction from static 2.32 evidence; not original source. */
intermediate.size = parse_w_w_val();       /* intermediate +0x9c */
intermediate.spacing = parse_w_spacing_val(); /* intermediate +0xa0 */
style.size = intermediate.size;            /* style +0xa0 */
style.spacing = intermediate.spacing;      /* style +0xa4 */
if (style.size < 70 && run_enabled) {
    if (style.size > 30) add_text(parser + 0x198);
    else if (style.size > 1) add_text(parser + 0x19c);
}
if (style.size > 130 && run_enabled) add_text(parser + 0x1a0);
if (main[0x10] > 10) emit_ordinary_report();
if (main[0x12] > *(int32_t*)0x006e51c0) emit_size_report();
/* Runtime behavior and exact XML inheritance are not asserted here. */
