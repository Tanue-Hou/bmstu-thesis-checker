/* RECOVERED PSEUDOCODE, not original source; 004d0694 */

void FUN_004d0694(int param_1,undefined4 param_2)

{
  ushort uVar1;
  undefined4 uVar2;
  int *piVar3;
  bool bVar4;
  char cVar5;
  undefined4 uVar6;
  byte *pbVar7;
  undefined4 uVar8;
  undefined4 *puVar9;
  int iVar10;
  ushort *puVar11;
  uint uVar12;
  undefined4 *in_FS_OFFSET;
  int local_7c;
  int local_78;
  undefined1 local_71;
  int *local_70;
  undefined4 local_6c;
  int local_68;
  undefined4 local_64;
  undefined2 local_54;
  int local_48;
  int *local_40;
  int local_3c;
  undefined4 local_38;
  undefined4 local_34;
  undefined1 local_30 [4];
  undefined1 local_2c [4];
  undefined1 local_28 [4];
  undefined1 local_24 [4];
  undefined1 local_20 [4];
  undefined1 local_1c [4];
  undefined1 local_18 [4];
  undefined4 local_14;
  undefined1 local_10 [4];
  undefined1 local_c [4];
  undefined1 local_8 [4];
  
  local_6c = param_2;
  local_68 = param_1;
  FUN_006ad628(&DAT_006faf5c);
  local_70 = (int *)FUN_005405fc(PTR_PTR_00534324,1);
  local_54 = 0xc;
  uVar6 = FUN_00477d3c(&local_71);
  pbVar7 = (byte *)FUN_00477d70(uVar6,0);
  uVar12 = (uint)*pbVar7;
  uVar8 = FUN_0046fa54(&local_14);
  local_48 = local_48 + 1;
  puVar9 = (undefined4 *)FUN_006bf04c(local_10,&DAT_006fa6a0);
  local_48 = local_48 + 1;
  uVar6 = *puVar9;
  puVar9 = (undefined4 *)FUN_006bf04c(local_c,&DAT_006fa69c);
  local_48 = local_48 + 1;
  uVar2 = *puVar9;
  puVar9 = (undefined4 *)FUN_006bef70(local_8,local_6c);
  local_48 = local_48 + 1;
  FUN_00560954(*puVar9,uVar2,uVar6,uVar8,uVar12);
  (**(code **)(*local_70 + 0x2c))(local_70,local_14);
  local_48 = local_48 + -1;
  FUN_006bf0b0(&local_14,2);
  local_48 = local_48 + -1;
  FUN_006bf0b0(local_10,2);
  local_48 = local_48 + -1;
  FUN_006bf0b0(local_c,2);
  local_48 = local_48 + -1;
  FUN_006bf0b0(local_8,2);
  local_78 = 0;
  do {
    iVar10 = (**(code **)(*local_70 + 0x14))();
    if (iVar10 <= local_78) {
      local_7c = 0;
      while( true ) {
        iVar10 = (**(code **)(*local_70 + 0x14))();
        if (iVar10 <= local_7c) break;
        local_54 = 0x30;
        uVar6 = FUN_0046fa54(local_30);
        local_48 = local_48 + 1;
        (**(code **)(*local_70 + 0xc))(local_70,local_7c,uVar6);
        puVar11 = (ushort *)FUN_0047699c(local_30,1);
        uVar1 = *puVar11;
        local_48 = local_48 + -1;
        FUN_006bf0b0(local_30,2);
        local_54 = 0x3c;
        uVar6 = FUN_0046fa54(&local_34);
        local_48 = local_48 + 1;
        (**(code **)(*local_70 + 0xc))(local_70,local_7c,uVar6);
        piVar3 = *(int **)(local_68 + (uVar1 - 0x430) * 4);
        iVar10 = (**(code **)(*piVar3 + 0x54))(piVar3,local_34);
        local_48 = local_48 + -1;
        FUN_006bf0b0(&local_34,2);
        if (iVar10 == -1) {
          local_54 = 0x48;
          uVar6 = FUN_0046fa54(&local_38);
          local_48 = local_48 + 1;
          (**(code **)(*local_70 + 0xc))(local_70,local_7c,uVar6);
          piVar3 = *(int **)(local_68 + (uVar1 - 0x430) * 4);
          (**(code **)(*piVar3 + 0x38))(piVar3,local_38);
          local_48 = local_48 + -1;
          FUN_006bf0b0(&local_38,2);
        }
        local_54 = 0;
        local_7c = local_7c + 1;
      }
      local_40 = local_70;
      if (local_70 != (int *)0x0) {
        local_3c = *local_70;
        local_54 = 0x6c;
        (**(code **)(*local_70 + -4))(local_70,3);
      }
      *in_FS_OFFSET = local_64;
      return;
    }
    local_54 = 0x18;
    uVar6 = FUN_0046fa54(local_18);
    local_48 = local_48 + 1;
    (**(code **)(*local_70 + 0xc))(local_70,local_78,uVar6);
    FUN_006bf04c(local_1c,&DAT_006fa6a6);
    local_48 = local_48 + 1;
    cVar5 = FUN_006bf184(local_18,local_1c);
    if (cVar5 == '\0') {
      uVar6 = FUN_0046fa54(local_20);
      local_48 = local_48 + 1;
      (**(code **)(*local_70 + 0xc))(local_70,local_78,uVar6);
      FUN_006bf04c(local_24,&DAT_006fa6aa);
      local_48 = local_48 + 1;
      cVar5 = FUN_006bf184(local_20,local_24);
      local_48 = local_48 + -1;
      FUN_006bf0b0(local_24,2);
      local_48 = local_48 + -1;
      FUN_006bf0b0(local_20,2);
      if (cVar5 != '\0') goto LAB_004d087d;
      uVar6 = FUN_0046fa54(local_28);
      local_48 = local_48 + 1;
      (**(code **)(*local_70 + 0xc))(local_70,local_78,uVar6);
      FUN_006bf04c(local_2c,&DAT_006fa6ac);
      local_48 = local_48 + 1;
      cVar5 = FUN_006bf184(local_28,local_2c);
      local_48 = local_48 + -1;
      FUN_006bf0b0(local_2c,2);
      local_48 = local_48 + -1;
      FUN_006bf0b0(local_28,2);
      if (cVar5 != '\0') goto LAB_004d087d;
      bVar4 = false;
    }
    else {
LAB_004d087d:
      bVar4 = true;
    }
    local_48 = local_48 + -1;
    FUN_006bf0b0(local_1c,2);
    local_48 = local_48 + -1;
    FUN_006bf0b0(local_18,2);
    if (bVar4) {
      (**(code **)(*local_70 + 0x48))(local_70,local_78);
      local_78 = local_78 + -1;
    }
    local_78 = local_78 + 1;
  } while( true );
}

