/* Analyst reconstruction from native instructions and synthetic hardware-watch traces. */
/* For the observed calibration execution, FUN_006acec0 stores the existing zero
   x87 value to 8-byte ranges; the second qword overlaps the watched first slot. */
store_qword(dst + offset, current_x87_value);

/* In the observed calibration execution, FUN_00403318 reaches INC [ECX] with
   ECX equal to the report-bound left-counter address. */
*(uint32_t *)counter_address += 1;

/* PDF trace: same-value zeroing writes and report binding observed; no first
   increment in this trace is not evidence that another execution cannot do so. */
