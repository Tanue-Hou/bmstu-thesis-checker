; TestVkr232.exe SHA-256 5c04b57acdbda79073604d6e3cacc2994bc87c5ed316e3b8706555ca92b6a8f0
; Complete function 006b70b8-006b70e8 (48 bytes), decoded at its entry.
006b70b8 push    ebp
006b70b9 mov     ebp, esp
006b70bb lea     esp, [ebp - 0xc]
006b70be wait
006b70bf fnstcw  word ptr [ebp - 4]
006b70c2 wait
006b70c3 mov     ax, word ptr [ebp - 4]
006b70c7 or      dword ptr [ebp - 4], 0xc01
006b70ce fldcw   word ptr [ebp - 4]
006b70d1 fistp   qword ptr [ebp - 0xc]
006b70d4 mov     word ptr [ebp - 4], ax
006b70d8 wait
006b70d9 fnclex
006b70db fldcw   word ptr [ebp - 4]
006b70de mov     eax, dword ptr [ebp - 0xc]
006b70e1 mov     edx, dword ptr [ebp - 8]
006b70e4 mov     esp, ebp
006b70e6 pop     ebp
006b70e7 ret
