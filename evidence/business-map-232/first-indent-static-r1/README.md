# First-line-indent counter: static trace result

The report gate is identified, but its producer remains unresolved. Main function `FUN_0047a528` sets `local_5e0 = local_74+0x158` and reports when `local_5e0[0x51] > 0` (pseudocode `function.c` lines 607–612 and 2055 onward). That gate corresponds to parser counter offset `+0x29c`; its report and emit VAs are 0047ee16 and 0047ee23.

The DOCX property reader `FUN_0040b198` parses `w:firstLine` and `w:hanging` into field `param_2+0x1c` (recovered pseudocode lines 4971–5013), and `FUN_0040e9a8` dispatches `w:ind` to it. This establishes an input-property path, not a counter producer. The related generic helper `FUN_00403318` can increment an indexed report counter, but the reviewed paragraph producer `FUN_00437374` resolves only the neighboring counters +0x290, +0x294 and +0x298.

The PDF route from the main function reaches `FUN_0046ba90` and then `FUN_004645bc`. The visible `local_2a8+0x29c..+0x2a8` use in `FUN_004645bc` is a four-float formatted parse in the nearby page-metadata/MediaBox block; it does not establish a write to the paragraph report counter. A full-entry instruction scan of the 10,191 functions marked decompiled found no memory displacement `0x668`. The search result is limited to that exported function set and does not exclude indirect aliases or code outside it.

No threshold, role guard, producer VA, or producer caller was recovered. The JSON preserves the examined paths, source hashes, search boundary and remaining gap. No native execution or implementation change was made.
