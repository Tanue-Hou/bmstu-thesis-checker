/* ENTRY 00494dd0 NAME FUN_00494dd0 */

undefined4 FUN_00494dd0(int param_1)

{
  char cVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 *puVar4;
  int iVar5;
  undefined4 *in_FS_OFFSET;
  undefined1 *puVar6;
  undefined1 local_d4 [20];
  int *local_c0;
  int *local_bc;
  int *local_b8;
  int *local_b4;
  int local_b0;
  int *local_ac;
  int *local_a8;
  int *local_a4;
  int *local_a0;
  int *local_9c;
  int local_98;
  undefined4 local_94 [4];
  undefined2 local_84;
  int local_78;
  int *local_70;
  int local_6c;
  int *local_68;
  int local_64;
  undefined1 local_60 [4];
  undefined1 local_5c [4];
  undefined1 local_58 [4];
  undefined1 local_54 [4];
  undefined1 local_50 [4];
  undefined1 local_4c [4];
  undefined1 local_48 [4];
  undefined1 local_44 [4];
  undefined1 local_40 [4];
  undefined1 local_3c [4];
  undefined1 local_38 [4];
  undefined1 local_34 [4];
  undefined1 local_30 [4];
  undefined1 local_2c [4];
  undefined1 local_28 [4];
  undefined1 local_24 [4];
  undefined1 local_20 [4];
  undefined1 local_1c [4];
  undefined1 local_18 [4];
  undefined1 local_14 [4];
  undefined1 local_10 [4];
  undefined4 local_c [2];
  
  local_98 = param_1;
  FUN_006ad628(&DAT_006e5094);
  cVar1 = FUN_00476b58(&DAT_00734c90);
  if (cVar1 == '\0') {
    local_9c = (int *)0x0;
    EnterCriticalSection((LPCRITICAL_SECTION)&DAT_00734c5c);
    local_84 = 0xc;
    local_9c = (int *)FUN_0062e938(PTR_PTR_0061f3b8,
                                   CONCAT31((int3)((uint)*(int *)PTR_DAT_0073431c >> 8),1),
                                   *(undefined4 *)(*(int *)PTR_DAT_0073431c + 0x44));
    local_84 = 0x18;
    uVar2 = FUN_0046fa54(local_14);
    local_78 = local_78 + 1;
    uVar3 = FUN_006bf04c(local_10,u_FILE_NAME__006e2e10);
    local_78 = local_78 + 1;
    FUN_006bf100(uVar3,&DAT_00734c90,uVar2);
    puVar6 = local_14;
    uVar2 = FUN_0046fa54(local_1c);
    local_78 = local_78 + 1;
    FUN_006bf04c(local_18,u_vkr_dsn__006e2e26);
    local_78 = local_78 + 1;
    FUN_006bf100(puVar6,local_18,uVar2);
    puVar4 = (undefined4 *)FUN_006bed74(local_20,local_1c);
    local_78 = local_78 + 1;
    FUN_0062c640(local_9c,*puVar4);
    local_78 = local_78 + -1;
    FUN_006bedd4(local_20,2);
    local_78 = local_78 + -1;
    FUN_006bf0b0(local_1c,2);
    local_78 = local_78 + -1;
    FUN_006bf0b0(local_18,2);
    local_78 = local_78 + -1;
    FUN_006bf0b0(local_14,2);
    local_78 = local_78 + -1;
    FUN_006bf0b0(local_10,2);
    local_84 = 0x24;
    FUN_0046fa54(local_c);
    local_78 = local_78 + 1;
    local_84 = 0x30;
    FUN_00476b38(local_98 + 0x6c);
    FUN_006bf1f8();
    local_a0 = (int *)FUN_0062eacc(local_9c);
    (**(code **)(*local_a0 + 0x2c))(local_a0,local_c[0]);
    (**(code **)(*local_9c + 0x1a8))(local_9c,1);
    iVar5 = (**(code **)(*local_9c + 0x17c))();
    if (iVar5 == 0) {
      local_84 = 0x3c;
      puVar4 = (undefined4 *)
               FUN_006bf04c(local_24,&DAT_006e33b6,local_94,0,FUN_0046fb30,1,0,0,0,local_94);
      local_78 = local_78 + 1;
      FUN_0055e6e8(PTR_PTR_00553904,1,*puVar4);
      FUN_006bd4ac();
    }
    local_84 = 0x48;
    puVar4 = (undefined4 *)FUN_006bf04c(local_28,u_FacultName_006e33b8);
    local_78 = local_78 + 1;
    local_a4 = (int *)FUN_00614d88(local_9c,*puVar4);
    uVar2 = FUN_0046fa54(local_2c);
    local_78 = local_78 + 1;
    (**(code **)(*local_a4 + 0x74))(local_a4,uVar2);
    FUN_006bf0d8(local_98 + 8,local_2c);
    local_78 = local_78 + -1;
    FUN_006bf0b0(local_2c,2);
    local_78 = local_78 + -1;
    FUN_006bf0b0(local_28,2);
    FUN_006acef7();
    local_84 = 0x54;
    puVar4 = (undefined4 *)FUN_006bf04c(local_30,u_DepReal_node_006e33ce);
    local_78 = local_78 + 1;
    uVar2 = FUN_00614d88(local_9c,*puVar4);
    FUN_006057c0(uVar2,local_d4,1);
    local_78 = local_78 + -1;
    FUN_006bf0b0(local_30,2);
    iVar5 = FUN_006ad278();
    if (iVar5 != 0) {
      (**(code **)(*local_9c + 0x1a8))(local_9c,0);
      FUN_00476b38(local_98 + 0x6c);
      FUN_006bf1f8();
      local_a8 = (int *)FUN_0062eacc(local_9c);
      (**(code **)(*local_a8 + 0x2c))(local_a8,local_c[0]);
      (**(code **)(*local_9c + 0x1a8))(local_9c,1);
    }
    iVar5 = (**(code **)(*local_9c + 0x17c))();
    if (iVar5 == 0) {
      local_84 = 0x60;
      puVar4 = (undefined4 *)
               FUN_006bf04c(local_34,&DAT_006e39e0,local_94,0,FUN_0046fb30,1,0,0,0,local_94);
      local_78 = local_78 + 1;
      FUN_0055e6e8(PTR_PTR_00553904,1,*puVar4);
      FUN_006bd4ac();
    }
    local_84 = 0x6c;
    puVar4 = (undefined4 *)FUN_006bf04c(local_38,u_StudIo_006e39e2);
    local_78 = local_78 + 1;
    local_ac = (int *)FUN_00614d88(local_9c,*puVar4);
    uVar2 = FUN_0046fa54(local_3c);
    local_78 = local_78 + 1;
    (**(code **)(*local_ac + 0x74))(local_ac,uVar2);
    puVar6 = local_3c;
    uVar2 = FUN_0046fa54(local_40);
    local_78 = local_78 + 1;
    FUN_006bf2b4(puVar6,uVar2);
    FUN_006bf0d8(local_98 + 4,local_40);
    local_78 = local_78 + -1;
    FUN_006bf0b0(local_40,2);
    local_78 = local_78 + -1;
    FUN_006bf0b0(local_3c,2);
    local_78 = local_78 + -1;
    FUN_006bf0b0(local_38,2);
    local_84 = 0x78;
    FUN_006bf04c(local_44,&DAT_006e39f0);
    local_78 = local_78 + 1;
    local_b0 = FUN_006bf2a8(local_98 + 4,local_44);
    local_78 = local_78 + -1;
    FUN_006bf0b0(local_44,2);
    local_84 = 0x30;
    if (local_b0 != 0) {
      FUN_006bf294(local_98 + 4,local_b0 + -1);
    }
    local_84 = 0x84;
    puVar4 = (undefined4 *)FUN_006bf04c(local_48,u_DepName_006e39f4);
    local_78 = local_78 + 1;
    local_b4 = (int *)FUN_00614d88(local_9c,*puVar4);
    uVar2 = FUN_0046fa54(local_4c);
    local_78 = local_78 + 1;
    (**(code **)(*local_b4 + 0x74))(local_b4,uVar2);
    FUN_006bf0d8(local_98 + 0xc,local_4c);
    local_78 = local_78 + -1;
    FUN_006bf0b0(local_4c,2);
    local_78 = local_78 + -1;
    FUN_006bf0b0(local_48,2);
    local_84 = 0x90;
    puVar4 = (undefined4 *)FUN_006bf04c(local_50,u_DepAbbr_006e3a04);
    local_78 = local_78 + 1;
    local_b8 = (int *)FUN_00614d88(local_9c,*puVar4);
    uVar2 = FUN_0046fa54(local_54);
    local_78 = local_78 + 1;
    (**(code **)(*local_b8 + 0x74))(local_b8,uVar2);
    FUN_006bf0d8(local_98 + 0x10,local_54);
    local_78 = local_78 + -1;
    FUN_006bf0b0(local_54,2);
    local_78 = local_78 + -1;
    FUN_006bf0b0(local_50,2);
    local_84 = 0x9c;
    puVar4 = (undefined4 *)FUN_006bf04c(local_58,u_DepVkr_use_006e3a14);
    local_78 = local_78 + 1;
    local_bc = (int *)FUN_00614d88(local_9c,*puVar4);
    uVar2 = (**(code **)(*local_bc + 100))();
    *(undefined4 *)(local_98 + 0x144) = uVar2;
    local_78 = local_78 + -1;
    FUN_006bf0b0(local_58,2);
    local_84 = 0xa8;
    FUN_006bf04c(local_5c,&DAT_006e3a2a);
    local_78 = local_78 + 1;
    cVar1 = FUN_006bf184(local_98 + 0x80,local_5c);
    local_78 = local_78 + -1;
    FUN_006bf0b0(local_5c,2);
    if (cVar1 == '\0') {
      local_84 = 0xb4;
      puVar4 = (undefined4 *)FUN_006bf04c(local_60,u_DepAppendix_006e3a2e);
      local_78 = local_78 + 1;
      local_c0 = (int *)FUN_00614d88(local_9c,*puVar4);
      uVar2 = (**(code **)(*local_c0 + 100))();
      *(undefined4 *)(local_98 + 0x14) = uVar2;
      local_78 = local_78 + -1;
      FUN_006bf0b0(local_60,2);
    }
    else {
      *(undefined4 *)(local_98 + 0x14) = 0;
    }
    local_68 = local_9c;
    if (local_9c != (int *)0x0) {
      local_64 = *local_9c;
      local_84 = 0xd8;
      (**(code **)(*local_9c + -4))(local_9c,3);
      local_84 = 0xc0;
    }
    local_9c = (int *)0x0;
    local_78 = local_78 + -1;
    FUN_006bf0b0(local_c,2);
    if (local_9c != (int *)0x0) {
      local_84 = 0xf0;
      cVar1 = FUN_00613c50(local_9c);
      if (cVar1 != '\0') {
        (**(code **)(*local_9c + 0x1a8))(local_9c,0);
      }
      local_70 = local_9c;
      if (local_9c != (int *)0x0) {
        local_6c = *local_9c;
        local_84 = 0x114;
        (**(code **)(*local_9c + -4))(local_9c,3);
      }
    }
    local_84 = 0;
    LeaveCriticalSection((LPCRITICAL_SECTION)&DAT_00734c5c);
    *in_FS_OFFSET = local_94[0];
  }
  else {
    *in_FS_OFFSET = local_94[0];
  }
  return local_94[0];
}


