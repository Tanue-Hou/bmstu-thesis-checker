# Invalid instrumentation run

The first control attempt failed because the new tracer tried to read the length of a null native string object in an empty paragraph. The harness rejected the incomplete run; it is not rule evidence. Original input and executable hashes remained unchanged and the owned process was cleaned up. Private raw trace remains retained in the native-reference store. The tracer now treats a null string as zero units; replacement runs use a new directory.
