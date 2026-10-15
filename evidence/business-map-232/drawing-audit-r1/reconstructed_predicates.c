/* Analyst reconstruction, not recovered original source.
 * Target: TestVkr232 SHA256
 * 5c04b57acdbda79073604d6e3cacc2994bc87c5ed316e3b8706555ca92b6a8f0
 * Corroboration: adjacent audit.json, drawing-boundaries-r2/r3 traces,
 * agent-v027/decompilation/recovered_pseudocode.c (00438304,0041c6ac),
 * file-entry-decompilation-r1/function.c (0047a528).
 * Slots are uint32 indices into main result state; area is float32 slot0x73.
 * Native predicates are shown; independent parser supports a narrower profile.
 */
float native_mm(unsigned emu) { return (float)emu * (float)(1.0/36000.0); }
void ordinary_png_anchor(int native_mode, unsigned cx, unsigned cy) {
    if (native_mode == 7) { /* observed wrapNone */
        ++state[0x26];
        area = (float)(area + (float)(native_mm(cx) * native_mm(cy)));
    } else { /* observed wrapSquare; other modes still require proof */
        ++state[0x27];
    }
}
void observed_simple_vml_textbox(float width_mm, float height_mm) {
    ++state[0x28]; ++state[0x30];
    /* General helper has additional flags/gates; this is the tested path. */
    if (width_mm < 2.0f || height_mm < 2.0f) ++state[0x2e];
}
void drawing_report() { /* native main 0047a528 */
    if (state[0x26]+state[0x27] > 0 && area > 500.0f) emit_FloatingImages();
    if (state[0x28]+state[0x29] > 0) emit_FloatingShapes();
    if (state[0x30]+state[0x32] > 0) emit_FloatingLabels();
    if (state[0x2e] > 10) emit_SmallLabels();
}
