/* RECOVERED PSEUDOCODE, not original source; 004d0a08 */

void FUN_004d0a08(int param_1,undefined4 param_2)

{
  ushort uVar1;
  int *piVar2;
  bool bVar3;
  char cVar4;
  undefined4 uVar5;
  byte *pbVar6;
  undefined4 uVar7;
  undefined4 *puVar8;
  int iVar9;
  undefined4 uVar10;
  ushort *puVar11;
  uint uVar12;
  undefined4 *in_FS_OFFSET;
  int local_80;
  int local_7c;
  undefined1 local_75;
  int *local_74;
  undefined4 local_70;
  int local_6c;
  undefined4 local_68;
  undefined2 local_58;
  int local_4c;
  int *local_44;
  int local_40;
  undefined4 local_3c;
  undefined4 local_38;
  undefined1 local_34 [4];
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
  
  local_70 = param_2;
  local_6c = param_1;
  FUN_006ad628(&DAT_006fb0a0);
  local_74 = (int *)FUN_005405fc(PTR_PTR_00534324,1);
  local_58 = 0xc;
  uVar5 = FUN_00477d3c(&local_75);
  pbVar6 = (byte *)FUN_00477d70(uVar5,0);
  uVar12 = (uint)*pbVar6;
  uVar7 = FUN_0046fa54(&local_14);
  local_4c = local_4c + 1;
  puVar8 = (undefined4 *)FUN_006bf04c(local_10,&DAT_006fa6b4);
  local_4c = local_4c + 1;
  uVar5 = *puVar8;
  puVar8 = (undefined4 *)FUN_006bf04c(local_c,&DAT_006fa6b0);
  local_4c = local_4c + 1;
  uVar10 = *puVar8;
  puVar8 = (undefined4 *)FUN_006bef70(local_8,local_70);
  local_4c = local_4c + 1;
  FUN_00560954(*puVar8,uVar10,uVar5,uVar7,uVar12);
  (**(code **)(*local_74 + 0x2c))(local_74,local_14);
  local_4c = local_4c + -1;
  FUN_006bf0b0(&local_14,2);
  local_4c = local_4c + -1;
  FUN_006bf0b0(local_10,2);
  local_4c = local_4c + -1;
  FUN_006bf0b0(local_c,2);
  local_4c = local_4c + -1;
  FUN_006bf0b0(local_8,2);
  local_7c = 0;
  do {
    iVar9 = (**(code **)(*local_74 + 0x14))();
    if (iVar9 <= local_7c) {
      local_80 = 0;
      while( true ) {
        iVar9 = (**(code **)(*local_74 + 0x14))();
        if (iVar9 <= local_80) break;
        uVar5 = FUN_0046fa54(local_34);
        local_4c = local_4c + 1;
        (**(code **)(*local_74 + 0xc))(local_74,local_80,uVar5);
        uVar5 = FUN_00476b14(local_34);
        local_58 = 0x30;
        uVar10 = FUN_0046fa54(local_30);
        local_4c = local_4c + 1;
        (**(code **)(*local_74 + 0xc))(local_74,local_80,uVar10);
        puVar11 = (ushort *)FUN_0047699c(local_30,uVar5);
        uVar1 = *puVar11;
        local_4c = local_4c + -1;
        FUN_006bf0b0(local_30,2);
        local_4c = local_4c + -1;
        FUN_006bf0b0(local_34,2);
        local_58 = 0x3c;
        uVar5 = FUN_0046fa54(&local_38);
        local_4c = local_4c + 1;
        (**(code **)(*local_74 + 0xc))(local_74,local_80,uVar5);
        piVar2 = *(int **)(local_6c + 0x80 + (uVar1 - 0x430) * 4);
        iVar9 = (**(code **)(*piVar2 + 0x54))(piVar2,local_38);
        local_4c = local_4c + -1;
        FUN_006bf0b0(&local_38,2);
        if (iVar9 == -1) {
          local_58 = 0x48;
          uVar5 = FUN_0046fa54(&local_3c);
          local_4c = local_4c + 1;
          (**(code **)(*local_74 + 0xc))(local_74,local_80,uVar5);
          piVar2 = *(int **)(local_6c + 0x80 + (uVar1 - 0x430) * 4);
          (**(code **)(*piVar2 + 0x38))(piVar2,local_3c);
          local_4c = local_4c + -1;
          FUN_006bf0b0(&local_3c,2);
        }
        local_58 = 0;
        local_80 = local_80 + 1;
      }
      local_44 = local_74;
      if (local_74 != (int *)0x0) {
        local_40 = *local_74;
        local_58 = 0x6c;
        (**(code **)(*local_74 + -4))(local_74,3);
      }
      *in_FS_OFFSET = local_68;
      return;
    }
    local_58 = 0x18;
    uVar5 = FUN_0046fa54(local_18);
    local_4c = local_4c + 1;
    (**(code **)(*local_74 + 0xc))(local_74,local_7c,uVar5);
    FUN_006bf04c(local_1c,&DAT_006fa6ba);
    local_4c = local_4c + 1;
    cVar4 = FUN_006bf184(local_18,local_1c);
    if (cVar4 == '\0') {
      uVar5 = FUN_0046fa54(local_20);
      local_4c = local_4c + 1;
      (**(code **)(*local_74 + 0xc))(local_74,local_7c,uVar5);
      FUN_006bf04c(local_24,&DAT_006fa6be);
      local_4c = local_4c + 1;
      cVar4 = FUN_006bf184(local_20,local_24);
      local_4c = local_4c + -1;
      FUN_006bf0b0(local_24,2);
      local_4c = local_4c + -1;
      FUN_006bf0b0(local_20,2);
      if (cVar4 != '\0') goto LAB_004d0bf1;
      uVar5 = FUN_0046fa54(local_28);
      local_4c = local_4c + 1;
      (**(code **)(*local_74 + 0xc))(local_74,local_7c,uVar5);
      FUN_006bf04c(local_2c,&DAT_006fa6c0);
      local_4c = local_4c + 1;
      cVar4 = FUN_006bf184(local_28,local_2c);
      local_4c = local_4c + -1;
      FUN_006bf0b0(local_2c,2);
      local_4c = local_4c + -1;
      FUN_006bf0b0(local_28,2);
      if (cVar4 != '\0') goto LAB_004d0bf1;
      bVar3 = false;
    }
    else {
LAB_004d0bf1:
      bVar3 = true;
    }
    local_4c = local_4c + -1;
    FUN_006bf0b0(local_1c,2);
    local_4c = local_4c + -1;
    FUN_006bf0b0(local_18,2);
    if (bVar3) {
      (**(code **)(*local_74 + 0x48))(local_74,local_7c);
      local_7c = local_7c + -1;
    }
    local_7c = local_7c + 1;
  } while( true );
}

