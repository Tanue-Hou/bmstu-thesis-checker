/* Analyst reconstruction, not original author source. Exact target in map.json. */
if (enabled && half_points > 0 && half_points < 2*minimum_pt) {
    if (half_points > minimum_pt) add_utf16_text(small_bucket);
    else add_utf16_text(tiny_bucket);
}
if (enabled && half_points > 2*maximum_pt && c8 == 0 &&
    (f0 == 0 || previous_textbox_units > 100)) add_utf16_text(large_bucket);
if (small_count > 10) report_small();
if (large_count > 10) report_large();
/* The producer has an outer AC/enabled gate; unknown flags are not generalized. */
