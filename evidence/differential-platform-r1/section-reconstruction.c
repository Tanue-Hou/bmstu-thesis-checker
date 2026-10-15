/* Analyst reconstruction of the native section header/footer distance path.
   It is a behavioral summary, not recovered author source. See
   section-function-map.json for source hashes, short instruction bytes, and
   bounded runtime evidence. */

typedef struct {
    /* Other native section properties are omitted. */
    float header_distance_mm; /* section record +0x28 */
    float footer_distance_mm; /* section record +0x2c */
} SectionRecordExcerpt;

static const float TWIPS_TO_MM = 0.017638888210058212f;
static const float EXPECTED_DISTANCE_MM = 12.5f;
static const float DISTANCE_EPSILON_MM = 0.20000000298023224f;

static int within_native_distance_tolerance(float actual_mm) {
    /* Native helper implements both inclusive bounds. */
    /* Keep promoted operands; do not round the tolerance sum/difference to
       float32 before comparison. Summary is limited to the finite tested range. */
    if ((double)EXPECTED_DISTANCE_MM - (double)DISTANCE_EPSILON_MM > (double)actual_mm)
        return 0;
    if ((double)EXPECTED_DISTANCE_MM + (double)DISTANCE_EPSILON_MM < (double)actual_mm)
        return 0;
    return 1;
}

static void read_section_distance_attributes(SectionRecordExcerpt *section,
                                            int has_header, int header_twips,
                                            int has_footer, int footer_twips) {
    /* FUN_0040b31c parses w:header into record +0x28 and w:footer into +0x2c.
       FILD/FMUL/FSTP stores the integer-twips conversion rounded to float32. */
    if (has_header)
        section->header_distance_mm = (float)header_twips * TWIPS_TO_MM;
    if (has_footer)
        section->footer_distance_mm = (float)footer_twips * TWIPS_TO_MM;
}

static void count_section_distance_mismatches(const SectionRecordExcerpt *section,
                                              int *parser_counter_0x28c) {
    /* Native INC [EAX+0x28c] uses EAX=parser base in the observed runs.
       Header and footer mismatch each increment the same parser counter. */
    if (!within_native_distance_tolerance(section->header_distance_mm))
        ++*parser_counter_0x28c;
    if (!within_native_distance_tolerance(section->footer_distance_mm))
        ++*parser_counter_0x28c;
}

static int should_emit_main_report_item(int main_report_slot_0x4d) {
    /* FUN_0047a528 emits this report item when the mapped main slot is > 0. */
    return main_report_slot_0x4d > 0;
}

/* Static prediction: integer twips 698..720 inclusive pass. Runtime receipt
   section-boundaries-r2 confirms 697/721 mismatch and 698/720 pass for both
   fields and both tested work types (16 synthetic boundary cases total). */
