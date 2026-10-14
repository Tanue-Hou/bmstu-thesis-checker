/* ENTRY 00495ee8 NAME FUN_00495ee8 */

int FUN_00495ee8(int *param_1,int param_2,int param_3,char param_4,int param_5,undefined4 param_6)

{
  char cVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 *in_FS_OFFSET;
  undefined1 *puVar5;
  int local_54;
  int local_50;
  undefined4 local_48;
  undefined1 local_24 [4];
  undefined1 local_20 [4];
  undefined1 local_1c [4];
  undefined1 local_18 [4];
  undefined1 local_14 [4];
  undefined1 local_10 [4];
  undefined1 local_c [4];
  undefined1 local_8 [4];
  
  FUN_006ad628(&DAT_006e55ac);
  local_54 = param_3;
  local_50 = param_2;
  if (param_4 == '\0') {
    if (param_2 < 0) {
      local_50 = 0;
    }
    if (param_3 < 0) {
      local_54 = (**(code **)(*param_1 + 0x14))();
    }
    FUN_0046fa54(local_18);
    for (; local_50 < local_54; local_50 = local_50 + 1) {
      uVar2 = FUN_0046fa54(local_1c);
      (**(code **)(*param_1 + 0xc))(param_1,local_50,uVar2);
      FUN_006bf0d8(local_18,local_1c);
      FUN_006bf0b0(local_1c,2);
      if (param_5 == 0) {
        cVar1 = FUN_006bf184(local_18,param_6);
        if (cVar1 != '\0') {
          FUN_006bf0b0(local_18,2);
          *in_FS_OFFSET = local_48;
          return local_50;
        }
      }
      else if (param_5 == 1) {
        uVar2 = FUN_0046fa54(local_20);
        uVar3 = FUN_00476b14(param_6);
        FUN_006bf458(local_18,1,uVar3,uVar2);
        puVar5 = local_20;
        uVar2 = FUN_0046fa54(local_24);
        FUN_006bf3cc(puVar5,uVar2);
        cVar1 = FUN_006bf184(local_24,param_6);
        FUN_006bf0b0(local_24,2);
        FUN_006bf0b0(local_20,2);
        if (cVar1 != '\0') {
          FUN_006bf0b0(local_18,2);
          *in_FS_OFFSET = local_48;
          return local_50;
        }
      }
      else {
        iVar4 = FUN_006bf2a8(local_18,param_6);
        if (iVar4 != 0) {
          FUN_006bf0b0(local_18,2);
          *in_FS_OFFSET = local_48;
          return local_50;
        }
      }
    }
    FUN_006bf0b0(local_18,2);
  }
  else {
    if (param_2 < 0) {
      local_50 = (**(code **)(*param_1 + 0x14))();
      local_50 = local_50 + -1;
    }
    if (param_3 < 0) {
      local_54 = 0;
    }
    FUN_0046fa54(local_8);
    for (; local_54 <= local_50; local_50 = local_50 + -1) {
      uVar2 = FUN_0046fa54(local_c);
      (**(code **)(*param_1 + 0xc))(param_1,local_50,uVar2);
      FUN_006bf0d8(local_8,local_c);
      FUN_006bf0b0(local_c,2);
      if (param_5 == 0) {
        cVar1 = FUN_006bf184(local_8,param_6);
        if (cVar1 != '\0') {
          FUN_006bf0b0(local_8,2);
          *in_FS_OFFSET = local_48;
          return local_50;
        }
      }
      else if (param_5 == 1) {
        uVar2 = FUN_0046fa54(local_10);
        uVar3 = FUN_00476b14(param_6);
        FUN_006bf458(local_8,1,uVar3,uVar2);
        puVar5 = local_10;
        uVar2 = FUN_0046fa54(local_14);
        FUN_006bf3cc(puVar5,uVar2);
        cVar1 = FUN_006bf184(local_14,param_6);
        FUN_006bf0b0(local_14,2);
        FUN_006bf0b0(local_10,2);
        if (cVar1 != '\0') {
          FUN_006bf0b0(local_8,2);
          *in_FS_OFFSET = local_48;
          return local_50;
        }
      }
      else {
        iVar4 = FUN_006bf2a8(local_8,param_6);
        if (iVar4 != 0) {
          FUN_006bf0b0(local_8,2);
          *in_FS_OFFSET = local_48;
          return local_50;
        }
      }
    }
    FUN_006bf0b0(local_8,2);
  }
  *in_FS_OFFSET = local_48;
  return -1;
}


