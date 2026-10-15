# Native Russian diagnostic string map (r2)

Static scan of `runtime/TestVkr232.exe`, SHA-256 `5c04b57acdbda79073604d6e3cacc2994bc87c5ed316e3b8706555ca92b6a8f0`; PE image base `0x00400000`. The scanner first verified both known literals against provenance and their exact file offsets and decoded text: `006d6b5a` and `006d6bee`.

The JSON contains 8,713 decodable Russian UTF-16LE NUL-terminated strings. Of these, 32 contain configured diagnostic terms; 8 diagnostic candidates have at least one pseudocode address reference. Each candidate records function address/name and pseudocode line. A reference equal to the string's first VA is `direct_addr`; an address pointing later within the string's byte range is `reference_inside_literal`, with its byte offset.

All links are static candidates, not evidence that code executed or a diagnostic fired. The scan omits non-UTF-16LE or unterminated text and the reference map can include bare hexadecimal constants; see `limits` in the JSON for scope.

Printable sequences containing Cyrillic code units can include random binary false positives. The total is not a count of meaningful messages or rules. Revision2 sorts by VA, handles nested intervals with prefix maximum ends, and excludes odd-byte offsets into UTF-16 code units. Prior evidence is preserved.

Rebuild from the project root with:

```powershell
& 'C:\Users\Tanue Hou\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' implementation/scripts/reverse_engineering/map_native_diagnostics.py
```
