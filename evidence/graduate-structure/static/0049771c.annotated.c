/* ENTRY 0049771c NAME FUN_0049771c */

void FUN_0049771c(int *param_1,int *param_2,int *param_3)

{
  short sVar1;
  char cVar2;
  undefined4 *puVar3;
  int iVar4;
  uint uVar5;
  undefined4 uVar6;
  short *psVar7;
  undefined4 *in_FS_OFFSET;
  undefined1 *puVar8;
  undefined4 uVar9;
  int local_14c;
  int local_148;
  int local_144;
  int local_140;
  int local_13c;
  int local_138;
  int local_134;
  int local_130;
  int local_12c;
  char local_125;
  int local_124;
  int local_120;
  int local_11c;
  int local_118;
  int local_114;
  int local_110;
  int local_10c;
  int *local_108;
  int *local_104;
  int *local_100;
  undefined4 local_fc;
  undefined2 local_ec;
  int local_e0;
  undefined1 local_d8 [4];
  undefined1 local_d4 [4];
  undefined1 local_d0 [4];
  undefined1 local_cc [4];
  undefined1 local_c8 [4];
  undefined1 local_c4 [4];
  undefined1 local_c0 [4];
  undefined1 local_bc [4];
  undefined1 local_b8 [4];
  undefined1 local_b4 [4];
  undefined1 local_b0 [4];
  undefined1 local_ac [4];
  undefined1 local_a8 [4];
  undefined1 local_a4 [4];
  undefined1 local_a0 [4];
  undefined1 local_9c [4];
  undefined1 local_98 [4];
  undefined1 local_94 [4];
  undefined1 local_90 [4];
  undefined1 local_8c [4];
  undefined1 local_88 [4];
  undefined1 local_84 [4];
  undefined1 local_80 [4];
  undefined1 local_7c [4];
  undefined1 local_78 [4];
  undefined1 local_74 [4];
  undefined1 local_70 [4];
  undefined4 local_6c;
  undefined1 local_68 [4];
  undefined1 local_64 [4];
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
  undefined1 local_c [4];
  undefined1 local_8 [4];
  
  local_108 = param_3;
  local_104 = param_2;
  local_100 = param_1;
  FUN_006ad628(&DAT_006e6198);
  local_10c = local_104[0xb];
  if (local_10c == -1) {
    local_10c = local_104[0xc];
  }
  if (local_10c == -1) {
    local_10c = local_104[0x10];
  }
  if (local_10c == -1) {
    *(int *)(*local_104 + 0x16c) = *(int *)(*local_104 + 0x16c) + 1;
    local_ec = 0xc;
    puVar3 = (undefined4 *)FUN_006bf04c(local_8,PTR_DAT_006e1fbc);
    local_e0 = local_e0 + 1;
    (**(code **)(*local_108 + 0x38))(local_108,*puVar3);
    local_e0 = local_e0 + -1;
    FUN_006bf0b0(local_8,2);
    *in_FS_OFFSET = local_fc;
  }
  else {
    local_110 = 0;
    local_114 = 0;
    while( true ) {
      iVar4 = (**(code **)(*DAT_00734c94 + 0x14))();
      if (iVar4 <= local_114) break;
      local_ec = 0x18;
      uVar6 = FUN_0046fa54(local_c);
      local_e0 = local_e0 + 1;
      (**(code **)(*DAT_00734c94 + 0xc))(DAT_00734c94,local_114,uVar6);
      puVar8 = local_c;
      FUN_006bf04c(local_10,&DAT_006e454c /* UTF16 "факультет" */);
      local_e0 = local_e0 + 1;
      iVar4 = FUN_006bf2a8(puVar8,local_10);
      if (iVar4 == 0) {
        uVar6 = FUN_0046fa54(local_14);
        local_e0 = local_e0 + 1;
        (**(code **)(*DAT_00734c94 + 0xc))(DAT_00734c94,local_114,uVar6);
        puVar8 = local_14;
        FUN_006bf04c(local_18,&DAT_006e4560 /* UTF16 "кафедра" */);
        local_e0 = local_e0 + 1;
        iVar4 = FUN_006bf2a8(puVar8,local_18);
        uVar5 = (uint)(iVar4 != 0);
        local_e0 = local_e0 + -1;
        FUN_006bf0b0(local_18,2);
        local_e0 = local_e0 + -1;
        FUN_006bf0b0(local_14,2);
        if (uVar5 != 0) goto LAB_004978c1;
        cVar2 = '\0';
      }
      else {
LAB_004978c1:
        cVar2 = '\x01';
      }
      local_e0 = local_e0 + -1;
      FUN_006bf0b0(local_10,2);
      local_e0 = local_e0 + -1;
      FUN_006bf0b0(local_c,2);
      if (cVar2 != '\0') {
        local_110 = local_114;
        break;
      }
      local_114 = local_114 + 1;
    }
    local_118 = 0;
    local_120 = 0;
    local_124 = 0;
    while( true ) {
      iVar4 = (**(code **)(*DAT_00734c94 + 0x14))();
      if (iVar4 <= local_124) break;
      local_11c = 0;
      if (0 < local_10c) {
        do {
          uVar6 = FUN_0046fa54(local_28);
          local_e0 = local_e0 + 1;
          (**(code **)(*DAT_00734c94 + 0xc))(DAT_00734c94,local_124,uVar6);
          puVar8 = local_28;
          local_ec = 0x24;
          uVar6 = FUN_0046fa54(local_24);
          local_e0 = local_e0 + 1;
          (**(code **)(*local_100 + 0xc))(local_100,local_11c,uVar6);
          cVar2 = FUN_004964fc(local_24,puVar8);
          local_e0 = local_e0 + -1;
          FUN_006bf0b0(local_28,2);
          local_e0 = local_e0 + -1;
          FUN_006bf0b0(local_24,2);
          if (cVar2 != '\0') {
            local_118 = local_118 + 1;
            break;
          }
          local_11c = local_11c + 1;
        } while (local_11c < local_10c);
      }
      local_ec = 0x3c;
      uVar6 = FUN_0046fa54(local_1c);
      local_e0 = local_e0 + 1;
      (**(code **)(*local_100 + 0xc))(local_100,local_11c,uVar6);
      local_ec = 0x48;
      uVar6 = FUN_0046fa54(local_20);
      local_e0 = local_e0 + 1;
      (**(code **)(*DAT_00734c94 + 0xc))(DAT_00734c94,local_124,uVar6);
      local_ec = 0x54;
      FUN_006bf04c(local_2c,&DAT_006e4570);
      local_e0 = local_e0 + 1;
      cVar2 = FUN_006bf184(local_104 + 0x20,local_2c);
      if ((cVar2 == '\0') || (local_11c < local_10c)) {
        cVar2 = '\0';
      }
      else {
        cVar2 = '\x01';
      }
      local_e0 = local_e0 + -1;
      FUN_006bf0b0(local_2c,2);
      if (cVar2 != '\0') {
        local_ec = 0x60;
        uVar6 = FUN_0046fa54(local_30);
        local_e0 = local_e0 + 1;
        (**(code **)(*DAT_00734c94 + 0xc))(DAT_00734c94,local_124,uVar6);
        puVar8 = local_30;
        FUN_006bf04c(local_34,&DAT_006e4574 /* UTF16 "министерство" */);
        local_e0 = local_e0 + 1;
        cVar2 = FUN_006bf184(puVar8,local_34);
        if (cVar2 == '\0') {
          uVar6 = FUN_0046fa54(local_38);
          local_e0 = local_e0 + 1;
          (**(code **)(*DAT_00734c94 + 0xc))(DAT_00734c94,local_124,uVar6);
          puVar8 = local_38;
          FUN_006bf04c(local_3c,&DAT_006e458e /* UTF16 "науки" */);
          local_e0 = local_e0 + 1;
          cVar2 = FUN_006bf184(puVar8,local_3c);
          uVar5 = (uint)(cVar2 != '\0');
          local_e0 = local_e0 + -1;
          FUN_006bf0b0(local_3c,2);
          local_e0 = local_e0 + -1;
          FUN_006bf0b0(local_38,2);
          if (uVar5 != 0) goto LAB_00497d67;
          uVar6 = FUN_0046fa54(local_40);
          local_e0 = local_e0 + 1;
          (**(code **)(*DAT_00734c94 + 0xc))(DAT_00734c94,local_124,uVar6);
          puVar8 = local_40;
          FUN_006bf04c(local_44,&DAT_006e459a /* UTF16 "российской" */);
          local_e0 = local_e0 + 1;
          cVar2 = FUN_006bf184(puVar8,local_44);
          uVar5 = (uint)(cVar2 != '\0');
          local_e0 = local_e0 + -1;
          FUN_006bf0b0(local_44,2);
          local_e0 = local_e0 + -1;
          FUN_006bf0b0(local_40,2);
          if (uVar5 != 0) goto LAB_00497d67;
          uVar6 = FUN_0046fa54(local_48);
          local_e0 = local_e0 + 1;
          (**(code **)(*DAT_00734c94 + 0xc))(DAT_00734c94,local_124,uVar6);
          puVar8 = local_48;
          FUN_006bf04c(local_4c,&DAT_006e45b0 /* UTF16 "федерации" */);
          local_e0 = local_e0 + 1;
          cVar2 = FUN_006bf184(puVar8,local_4c);
          uVar5 = (uint)(cVar2 != '\0');
          local_e0 = local_e0 + -1;
          FUN_006bf0b0(local_4c,2);
          local_e0 = local_e0 + -1;
          FUN_006bf0b0(local_48,2);
          if (uVar5 != 0) goto LAB_00497d67;
          uVar6 = FUN_0046fa54(local_50);
          local_e0 = local_e0 + 1;
          (**(code **)(*DAT_00734c94 + 0xc))(DAT_00734c94,local_124,uVar6);
          puVar8 = local_50;
          FUN_006bf04c(local_54,&DAT_006e45c4 /* UTF16 "тему" */);
          local_e0 = local_e0 + 1;
          cVar2 = FUN_006bf184(puVar8,local_54);
          uVar5 = (uint)(cVar2 != '\0');
          local_e0 = local_e0 + -1;
          FUN_006bf0b0(local_54,2);
          local_e0 = local_e0 + -1;
          FUN_006bf0b0(local_50,2);
          if (uVar5 != 0) goto LAB_00497d67;
          uVar6 = FUN_0046fa54(local_58);
          local_e0 = local_e0 + 1;
          (**(code **)(*DAT_00734c94 + 0xc))(DAT_00734c94,local_124,uVar6);
          puVar8 = local_58;
          FUN_006bf04c(local_5c,&DAT_006e45ce /* UTF16 "нормоконтролер" */);
          local_e0 = local_e0 + 1;
          cVar2 = FUN_006bf184(puVar8,local_5c);
          uVar5 = (uint)(cVar2 != '\0');
          local_e0 = local_e0 + -1;
          FUN_006bf0b0(local_5c,2);
          local_e0 = local_e0 + -1;
          FUN_006bf0b0(local_58,2);
          if (uVar5 != 0) goto LAB_00497d67;
          cVar2 = '\0';
        }
        else {
LAB_00497d67:
          cVar2 = '\x01';
        }
        local_e0 = local_e0 + -1;
        FUN_006bf0b0(local_34,2);
        local_e0 = local_e0 + -1;
        FUN_006bf0b0(local_30,2);
        if (cVar2 != '\0') {
          local_118 = local_118 + 1;
          local_11c = local_10c + -1;
        }
      }
      if ((local_10c <= local_11c) && (local_124 < local_110)) {
        local_ec = 0x6c;
        uVar6 = FUN_0046fa54(local_60);
        local_e0 = local_e0 + 1;
        (**(code **)(*DAT_00734c94 + 0xc))(DAT_00734c94,local_124,uVar6);
        puVar8 = local_60;
        FUN_006bf04c(local_64,&DAT_006e45ec /* UTF16 "факультет" */);
        local_e0 = local_e0 + 1;
        iVar4 = FUN_006bf2a8(puVar8,local_64);
        if (iVar4 == 0) {
LAB_00497e65:
          uVar6 = FUN_0046fa54(&local_6c);
          local_e0 = local_e0 + 1;
          FUN_005be260(*(undefined4 *)PTR_DAT_0073431c,uVar6);
          uVar6 = local_6c;
          uVar9 = FUN_0046fa54(local_70);
          local_e0 = local_e0 + 1;
          FUN_00558e40(uVar6,uVar9);
          puVar8 = local_70;
          uVar6 = FUN_0046fa54(local_74);
          local_e0 = local_e0 + 1;
          FUN_006bf2b4(puVar8,uVar6);
          puVar8 = local_74;
          FUN_006bf04c(local_78,u_testvkr_exe_006e4610);
          local_e0 = local_e0 + 1;
          cVar2 = FUN_006bf184(puVar8,local_78);
          uVar5 = (uint)(cVar2 != '\0');
          local_e0 = local_e0 + -1;
          FUN_006bf0b0(local_78,2);
          local_e0 = local_e0 + -1;
          FUN_006bf0b0(local_74,2);
          local_e0 = local_e0 + -1;
          FUN_006bf0b0(local_70,2);
          local_e0 = local_e0 + -1;
          FUN_006bf0b0(&local_6c,2);
          if (uVar5 != 0) goto LAB_00497f7a;
          FUN_006bf04c(local_7c,&DAT_006e4628);
          local_e0 = local_e0 + 1;
          cVar2 = FUN_006bf184(local_104 + 4,local_7c);
          uVar5 = (uint)(cVar2 != '\0');
          local_e0 = local_e0 + -1;
          FUN_006bf0b0(local_7c,2);
          if (uVar5 != 0) goto LAB_00497f7a;
          cVar2 = '\0';
        }
        else {
          FUN_006bf04c(local_68,&DAT_006e4600 /* UTF16 "кафедра" */);
          local_e0 = local_e0 + 1;
          iVar4 = FUN_006bf2a8(local_104 + 2,local_68);
          uVar5 = (uint)(iVar4 != 0);
          local_e0 = local_e0 + -1;
          FUN_006bf0b0(local_68,2);
          if (uVar5 == 0) goto LAB_00497e65;
LAB_00497f7a:
          cVar2 = '\x01';
        }
        local_e0 = local_e0 + -1;
        FUN_006bf0b0(local_64,2);
        local_e0 = local_e0 + -1;
        FUN_006bf0b0(local_60,2);
        if (cVar2 == '\0') {
          local_120 = local_120 + 1;
        }
      }
      local_e0 = local_e0 + -1;
      FUN_006bf0b0(local_20,2);
      local_e0 = local_e0 + -1;
      FUN_006bf0b0(local_1c,2);
      local_ec = 0;
      local_124 = local_124 + 1;
    }
    FUN_00496fc4(local_100,local_104,local_108);
    if (local_118 < 3) {
      *(int *)(*local_104 + 0x16c) = *(int *)(*local_104 + 0x16c) + 1;
      local_ec = 0x78;
      puVar3 = (undefined4 *)FUN_006bf04c(local_80,PTR_DAT_006e1fc0);
      local_e0 = local_e0 + 1;
      (**(code **)(*local_108 + 0x38))(local_108,*puVar3);
      local_e0 = local_e0 + -1;
      FUN_006bf0b0(local_80,2);
    }
    else {
      if (local_120 != 0) {
        *(int *)(*local_104 + 0x16c) = *(int *)(*local_104 + 0x16c) + 1;
        local_ec = 0x84;
        puVar3 = (undefined4 *)FUN_006bf04c(local_84,PTR_DAT_006e1fc4);
        local_e0 = local_e0 + 1;
        (**(code **)(*local_108 + 0x38))(local_108,*puVar3);
        local_e0 = local_e0 + -1;
        FUN_006bf0b0(local_84,2);
      }
      uVar5 = (**(code **)(*DAT_00734c94 + 0x14))();
      iVar4 = (int)uVar5 >> 1;
      if (iVar4 < 0) {
        iVar4 = iVar4 + (uint)((uVar5 & 1) != 0);
      }
      if (local_118 < iVar4) {
        *(int *)(*local_104 + 0x16c) = *(int *)(*local_104 + 0x16c) + 1;
        local_ec = 0x90;
        puVar3 = (undefined4 *)FUN_006bf04c(local_88,PTR_DAT_006e1fc8);
        local_e0 = local_e0 + 1;
        (**(code **)(*local_108 + 0x38))(local_108,*puVar3);
        local_e0 = local_e0 + -1;
        FUN_006bf0b0(local_88,2);
      }
      else {
        iVar4 = (**(code **)(*DAT_00734c94 + 0x14))();
        if (local_118 < iVar4 + -2) {
          *(int *)(*local_104 + 0x16c) = *(int *)(*local_104 + 0x16c) + 1;
          local_ec = 0x9c;
          puVar3 = (undefined4 *)FUN_006bf04c(local_8c,PTR_DAT_006e1fcc);
          local_e0 = local_e0 + 1;
          (**(code **)(*local_108 + 0x38))(local_108,*puVar3);
          local_e0 = local_e0 + -1;
          FUN_006bf0b0(local_8c,2);
        }
      }
      cVar2 = FUN_00476b58(local_104 + 1);
      if (cVar2 == '\0') {
        local_ec = 0xb4;
        uVar6 = FUN_0046fa54(local_90);
        local_e0 = local_e0 + 1;
        FUN_00496980(local_104 + 1,uVar6);
        local_125 = '\0';
        local_ec = 0xc0;
        FUN_0046fa54(local_94);
        local_e0 = local_e0 + 1;
        local_ec = 0xcc;
        FUN_0046fa54(local_98);
        local_e0 = local_e0 + 1;
        local_ec = 0xd8;
        FUN_006bf04c(local_9c,&DAT_006e462e /* UTF16 "руководитель" */);
        local_e0 = local_e0 + 1;
        FUN_006bf0d8(local_98,local_9c);
        local_e0 = local_e0 + -1;
        FUN_006bf0b0(local_9c,2);
        local_ec = 0xe4;
        FUN_006bf04c(local_a0,&DAT_006e4648);
        local_e0 = local_e0 + 1;
        cVar2 = FUN_006bf184(local_104 + 0x20,local_a0);
        local_e0 = local_e0 + -1;
        FUN_006bf0b0(local_a0,2);
        if (cVar2 == '\0') {
          local_ec = 0xfc;
          FUN_006bf04c(local_a8,&DAT_006e465e /* UTF16 "студент" */);
          local_e0 = local_e0 + 1;
          FUN_006bf0d8(local_94,local_a8);
          local_e0 = local_e0 + -1;
          FUN_006bf0b0(local_a8,2);
        }
        else {
          local_ec = 0xf0;
          FUN_006bf04c(local_a4,&DAT_006e464c /* UTF16 "аспирант" */);
          local_e0 = local_e0 + 1;
          FUN_006bf0d8(local_94,local_a4);
          local_e0 = local_e0 + -1;
          FUN_006bf0b0(local_a4,2);
        }
        local_134 = 0;
        if (0 < local_10c) {
          do {
            local_ec = 0x108;
            uVar6 = FUN_0046fa54(local_ac);
            local_e0 = local_e0 + 1;
            (**(code **)(*local_100 + 0xc))(local_100,local_134,uVar6);
            iVar4 = FUN_006bf2a8(local_ac,local_94);
            cVar2 = iVar4 != 0;
            local_e0 = local_e0 + -1;
            FUN_006bf0b0(local_ac,2);
            if (cVar2 != '\0') {
              local_12c = local_134 + -1;
              break;
            }
            local_134 = local_134 + 1;
          } while (local_134 < local_10c);
        }
        local_138 = local_12c;
        if (local_12c < local_10c) {
          do {
            local_ec = 0x114;
            uVar6 = FUN_0046fa54(local_b0);
            local_e0 = local_e0 + 1;
            (**(code **)(*local_100 + 0xc))(local_100,local_138,uVar6);
            iVar4 = FUN_006bf2a8(local_b0,local_98);
            cVar2 = iVar4 != 0;
            local_e0 = local_e0 + -1;
            FUN_006bf0b0(local_b0,2);
            if (cVar2 != '\0') {
              local_130 = local_138;
              break;
            }
            local_138 = local_138 + 1;
          } while (local_138 < local_10c);
        }
        local_140 = local_12c;
        local_ec = 0xa8;
        if (local_12c < local_130) {
          do {
            local_ec = 0x120;
            uVar6 = FUN_0046fa54(local_b4);
            local_e0 = local_e0 + 1;
            (**(code **)(*local_100 + 0xc))(local_100,local_140,uVar6);
            iVar4 = FUN_006bf2a8(local_b4,local_90);
            cVar2 = iVar4 != 0;
            local_e0 = local_e0 + -1;
            FUN_006bf0b0(local_b4,2);
            if (cVar2 != '\0') {
              local_ec = 0x138;
              uVar6 = FUN_0046fa54(local_b8);
              local_e0 = local_e0 + 1;
              (**(code **)(*local_100 + 0xc))(local_100,local_140,uVar6);
              local_ec = 300;
              local_144 = FUN_00476b14(local_90);
              local_13c = 1;
              while( true ) {
                iVar4 = FUN_00476b14(local_b8);
                if (iVar4 < local_13c + local_144 + -1) break;
                psVar7 = (short *)FUN_0047699c(local_b8,local_13c);
                sVar1 = *psVar7;
                psVar7 = (short *)FUN_0047699c(local_90,1);
                if (sVar1 == *psVar7) {
                  iVar4 = FUN_00476b14(local_b8);
                  if (iVar4 != local_13c + local_144 + -1) {
                    psVar7 = (short *)FUN_0047699c(local_b8,local_13c + local_144);
                    if (*psVar7 != 0x20) {
                      psVar7 = (short *)FUN_0047699c(local_b8,local_13c + local_144);
                      if (*psVar7 != 0x5f) goto LAB_00498675;
                    }
                  }
                  local_ec = 0x144;
                  uVar6 = FUN_0046fa54(local_bc);
                  local_e0 = local_e0 + 1;
                  FUN_006bf458(local_b8,local_13c,local_144,uVar6);
                  cVar2 = FUN_006bf184(local_bc,local_90);
                  uVar5 = (uint)(cVar2 != '\0');
                  local_e0 = local_e0 + -1;
                  FUN_006bf0b0(local_bc,2);
                  if (uVar5 != 0) break;
                }
LAB_00498675:
                local_13c = local_13c + 1;
              }
              iVar4 = FUN_00476b14(local_b8);
              if (local_13c + local_144 + -1 <= iVar4) {
                local_ec = 0x150;
                uVar6 = FUN_0046fa54(local_c0);
                local_e0 = local_e0 + 1;
                FUN_006bf458(local_b8,local_13c,100,uVar6);
                FUN_006bf0d8(local_b8,local_c0);
                local_e0 = local_e0 + -1;
                FUN_006bf0b0(local_c0,2);
                FUN_006bf294(local_b8,local_144);
              }
              cVar2 = FUN_006bf184(local_b8,local_90);
              if (cVar2 != '\0') {
                local_125 = '\x01';
                local_e0 = local_e0 + -1;
                FUN_006bf0b0(local_b8,2);
                break;
              }
              local_e0 = local_e0 + -1;
              FUN_006bf0b0(local_b8,2);
              local_ec = 0xa8;
            }
            local_140 = local_140 + 1;
          } while (local_140 < local_130);
        }
        if (local_125 == '\0') {
          *(int *)(*local_104 + 0x16c) = *(int *)(*local_104 + 0x16c) + 1;
          local_ec = 0x15c;
          puVar3 = (undefined4 *)FUN_006bf04c(local_c4,PTR_DAT_006e1fd0);
          local_e0 = local_e0 + 1;
          (**(code **)(*local_108 + 0x38))(local_108,*puVar3);
          local_e0 = local_e0 + -1;
          FUN_006bf0b0(local_c4,2);
        }
        local_e0 = local_e0 + -1;
        FUN_006bf0b0(local_98,2);
        local_e0 = local_e0 + -1;
        FUN_006bf0b0(local_94,2);
        local_e0 = local_e0 + -1;
        FUN_006bf0b0(local_90,2);
        local_ec = 0;
      }
      local_14c = FUN_00496b20(local_100,local_10c,local_104 + 3,&local_148);
      if ((local_14c == local_148) && (local_148 != 0)) {
        uVar9 = 1;
        local_ec = 0x168;
        FUN_006bf04c(local_c8,&DAT_006e466e);
        local_e0 = local_e0 + 1;
        puVar8 = local_c8;
        uVar6 = FUN_0047cf34(*local_104,*local_104 + 0x174,local_104,puVar8,uVar9);
        FUN_004c17c4(local_104,uVar6,puVar8,uVar9);
        local_e0 = local_e0 + -1;
        FUN_006bf0b0(local_c8,2);
      }
      else if ((0 < local_14c) && (local_14c < local_148)) {
        uVar9 = 1;
        local_ec = 0x174;
        FUN_006bf04c(local_cc,&DAT_006e4670,local_14c,1);
        local_e0 = local_e0 + 1;
        puVar8 = local_cc;
        uVar6 = FUN_0047cf34(*local_104,*local_104 + 0x174);
        FUN_004c17c4(local_104,uVar6,puVar8,uVar9);
        local_e0 = local_e0 + -1;
        FUN_006bf0b0(local_cc,2);
      }
      local_ec = 0x180;
      FUN_006bf04c(local_d0,&DAT_006e4672 /* UTF16 "кафедра" */);
      local_e0 = local_e0 + 1;
      iVar4 = FUN_006bf2a8(local_104 + 2,local_d0);
      cVar2 = iVar4 == 0;
      local_e0 = local_e0 + -1;
      FUN_006bf0b0(local_d0,2);
      if (cVar2 != '\0') {
        local_14c = FUN_00496b20(local_100,local_10c,local_104 + 2,&local_148);
        if ((local_14c == local_148) && (local_148 != 0)) {
          uVar9 = 1;
          local_ec = 0x18c;
          FUN_006bf04c(local_d4,&DAT_006e4682);
          local_e0 = local_e0 + 1;
          puVar8 = local_d4;
          uVar6 = FUN_0047cf34(*local_104,*local_104 + 0x178,local_104,puVar8,uVar9);
          FUN_004c17c4(local_104,uVar6,puVar8,uVar9);
          local_e0 = local_e0 + -1;
          FUN_006bf0b0(local_d4,2);
        }
        else if ((0 < local_14c) && (local_14c < local_148)) {
          uVar9 = 1;
          local_ec = 0x198;
          FUN_006bf04c(local_d8,&DAT_006e4684,local_14c,1);
          local_e0 = local_e0 + 1;
          puVar8 = local_d8;
          uVar6 = FUN_0047cf34(*local_104,*local_104 + 0x178);
          FUN_004c17c4(local_104,uVar6,puVar8,uVar9);
          local_e0 = local_e0 + -1;
          FUN_006bf0b0(local_d8,2);
        }
      }
      if ((local_14c != 0) && (local_120 == 0)) {
        *(int *)(*local_104 + 0x16c) = *(int *)(*local_104 + 0x16c) + 1;
      }
    }
    *in_FS_OFFSET = local_fc;
  }
  return;
}


