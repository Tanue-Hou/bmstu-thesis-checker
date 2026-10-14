/* ENTRY 0048f730 NAME FUN_0048f730 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0048f730(int param_1,undefined4 param_2,undefined1 param_3)

{
  char cVar1;
  undefined4 uVar2;
  undefined4 *puVar3;
  LPCWSTR lpFileName;
  DWORD DVar4;
  undefined4 *in_FS_OFFSET;
  undefined4 local_3c [4];
  undefined2 local_2c;
  int local_20;
  undefined1 local_14 [4];
  undefined1 local_10 [4];
  undefined1 local_c [8];
  
  FUN_006ad628(&DAT_006e07f8);
  *(undefined1 *)(param_1 + 8) = param_3;
  FUN_0048fbc0(param_1 + 0x524);
  if (*(int *)(param_1 + 0xc) != 0) {
    FUN_00696e30();
  }
  *(undefined4 *)(param_1 + 0xc) = 0;
  *(undefined4 *)(param_1 + 0x10) = 0;
  *(undefined4 *)(param_1 + 0x14) = 0;
  FUN_0048a214(param_1);
  FUN_0051afd8(param_1 + 0x268);
  FUN_004a91e8(param_1 + 0x3b0);
  FUN_0048f64c(param_1,0);
  *(undefined4 *)(param_1 + 0x210) = 0;
  *(undefined4 *)(param_1 + 0x214) = 0;
  *(undefined4 *)(param_1 + 0x218) = 0;
  *(undefined4 *)(param_1 + 0x21c) = 0;
  FUN_00480540();
  FUN_00484680();
  *(undefined1 *)(param_1 + 0x38) = 0;
  *(undefined4 *)(param_1 + 0x1ec) = 0;
  (**(code **)(**(int **)(param_1 + 0x924) + 0x44))();
  *(undefined4 *)(param_1 + 600) = 0;
  *(undefined4 *)(param_1 + 0x25c) = 0;
  *(undefined4 *)(param_1 + 0x260) = 0;
  *(undefined4 *)(param_1 + 0x264) = 0;
  *(undefined1 *)(param_1 + 0x3a8) = 0;
  *(undefined4 *)(param_1 + 0x3ac) = 0;
  FUN_00486618(*(undefined4 *)(param_1 + 0x248));
  FUN_00486560(*(undefined4 *)(param_1 + 0x24c));
  FUN_004ada34(*(undefined4 *)(param_1 + 0x254));
  FUN_00473c54(*(undefined4 *)(param_1 + 0x250));
  local_2c = 0xc;
  FUN_006bf04c(local_c,s_Unknown____006ddfb6 + 0xc);
  local_20 = local_20 + 1;
  uVar2 = FUN_006bf184(param_2,local_c);
  local_20 = local_20 + -1;
  FUN_006bf0b0(local_c,2);
  if ((char)uVar2 != '\0') {
    local_2c = 0x18;
    puVar3 = (undefined4 *)
             FUN_006bf04c(local_10,&DAT_006ddfc4,uVar2,0,FUN_0046fb30,1,0,0,0,local_3c);
    local_20 = local_20 + 1;
    FUN_0055e6e8(PTR_PTR_00553904,1,*puVar3);
    FUN_006bd4ac();
  }
  lpFileName = (LPCWSTR)FUN_00476b38(param_2);
  DVar4 = GetFileAttributesW(lpFileName);
  if (DVar4 == 0xffffffff) {
    *(undefined1 *)(param_1 + 0x6e8) = 1;
    *in_FS_OFFSET = local_3c[0];
  }
  else {
    FUN_006bf0d8(param_1 + 0x51c,param_2);
    local_2c = 0x24;
    cVar1 = FUN_0048f3d8(param_1,param_1 + 0x51c);
    if (cVar1 == '\0') {
      *(undefined1 *)(param_1 + 0x6e8) = 1;
    }
    else {
      (**(code **)(**(int **)(param_1 + 0x924) + 0x44))();
      local_2c = 0x30;
      puVar3 = (undefined4 *)FUN_006bf04c(local_14,&DAT_006de008);
      local_20 = local_20 + 1;
      (**(code **)(**(int **)(param_1 + 0x924) + 0x38))(*(int **)(param_1 + 0x924),*puVar3);
      local_20 = local_20 + -1;
      FUN_006bf0b0(local_14,2);
      FUN_004888c8(param_1,0xffffffff);
      if (0x1e < *(int *)(param_1 + 0x20)) {
        *(undefined1 *)(param_1 + 0x6ea) = 1;
      }
      local_2c = 0x24;
      if (*(int *)(param_1 + 600) + *(int *)(param_1 + 0x25c) == 0) {
        *(undefined4 *)(param_1 + 0x684) = 100;
      }
      else if (_DAT_0048fbb4 <
               ((float)*(int *)(param_1 + 0x25c) * _DAT_0048fbb0) /
               (float)(*(int *)(param_1 + 600) + *(int *)(param_1 + 0x25c))) {
        uVar2 = FUN_006b7054();
        *(undefined4 *)(param_1 + 0x684) = uVar2;
      }
      if (*(int *)(param_1 + 0x684) == 0) {
        if (*(int *)(param_1 + 0x260) + *(int *)(param_1 + 0x264) == 0) {
          *(undefined4 *)(param_1 + 0x684) = 100;
        }
        else if (_DAT_0048fbbc <
                 ((float)*(int *)(param_1 + 0x264) * _DAT_0048fbb0) /
                 (float)(*(int *)(param_1 + 0x260) + *(int *)(param_1 + 0x264))) {
          uVar2 = FUN_006b7054();
          *(undefined4 *)(param_1 + 0x684) = uVar2;
        }
      }
    }
    *in_FS_OFFSET = local_3c[0];
  }
  return;
}


