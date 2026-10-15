# Invalid intended landscape boundary fixtures

The six `landscape*` inputs in this generated batch are not valid intended
threshold probes: a generator variable collision replaced the shape width with
the page-width twip string11906, then emitted it as millimeters. The native runs
are actual observations of those incorrect fixtures, not evidence for the
intended263.99/264/264.01 or165.99/166/166.01 boundaries. No verification context
may use these six inputs or `shape-landscape-native-r1` to prove boundaries.

The generator is corrected to keep page-width twips separate from shape width.
Corrected immutable inputs are in `shape-bounds-inputs-r4`, with actual native
observations in `shape-landscape-native-r2`. The invalid artifacts are retained
only to explain the failed experiment; source hashes are not rewritten.
