/* ENTRY 00477f50 NAME FUN_00477f50 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_00477f50(int param_1)

{
  char cVar1;
  ushort uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined2 extraout_var;
  uint uVar5;
  undefined2 extraout_var_00;
  undefined4 *puVar6;
  undefined4 *puVar7;
  undefined4 *in_FS_OFFSET;
  byte bVar8;
  longdouble in_ST0;
  longdouble in_ST1;
  longdouble in_ST2;
  longdouble in_ST3;
  longdouble lVar9;
  longdouble lVar10;
  longdouble in_ST4;
  longdouble in_ST5;
  longdouble in_ST6;
  longdouble in_ST7;
  longdouble lVar11;
  undefined1 *puVar12;
  undefined4 local_42c;
  undefined4 local_428;
  float local_424;
  float local_420;
  undefined4 local_41c;
  undefined4 local_418;
  ushort local_414;
  float local_410;
  float local_40c;
  float local_408;
  float local_404;
  float local_400;
  float local_3fc;
  undefined4 local_3f8;
  undefined1 local_3f4;
  undefined1 local_3f3;
  undefined1 local_3f2;
  undefined1 local_3f1;
  uint local_3f0;
  undefined4 local_3ec [9];
  undefined1 local_3c8 [36];
  undefined4 local_3a4 [6];
  float local_38c;
  float local_388;
  ushort local_380 [256];
  undefined4 local_180;
  undefined4 local_17c;
  undefined1 local_178 [8];
  undefined1 local_170 [8];
  undefined1 local_168 [8];
  undefined1 local_160 [8];
  undefined1 *local_158;
  int local_154;
  float local_150;
  undefined1 local_14c [8];
  undefined1 local_144 [8];
  undefined1 local_13c [4];
  float local_138;
  undefined1 local_134 [8];
  float local_12c;
  undefined1 local_128 [8];
  undefined1 local_120 [8];
  undefined1 local_118 [4];
  float local_114;
  undefined1 local_110 [8];
  float local_108;
  undefined1 local_104 [8];
  undefined1 local_fc [8];
  float local_f4;
  float local_f0 [2];
  undefined1 local_e8 [8];
  undefined4 local_e0;
  undefined4 local_dc;
  undefined1 local_d8 [8];
  undefined1 local_d0 [10];
  ushort local_c6;
  int local_c4;
  int local_c0;
  int local_bc;
  uint local_b8;
  undefined4 local_b4;
  undefined4 local_b0;
  undefined1 local_ac [8];
  undefined4 local_a4;
  undefined4 local_a0;
  undefined1 local_9c [8];
  undefined1 local_94 [8];
  undefined4 local_8c;
  undefined4 local_88;
  uint local_84;
  uint local_80;
  int local_7c;
  float local_78;
  float local_74;
  float local_70;
  float local_6c;
  float local_68;
  float local_64;
  float local_60;
  float local_5c;
  float local_58;
  float local_54;
  float local_50;
  float local_4c;
  float local_48;
  char local_41;
  int local_40;
  int local_3c;
  uint local_38;
  int local_34;
  undefined4 local_30;
  undefined2 local_20;
  int local_14;
  undefined1 local_c [4];
  undefined1 local_8 [4];
  
  bVar8 = 0;
  local_34 = param_1;
  FUN_006ad628(&DAT_006dc354);
  if (*(int *)(local_34 + 0x18) == 0) {
    *in_FS_OFFSET = local_30;
    uVar4 = local_30;
  }
  else {
    local_38 = (uint)**(ushort **)(local_34 + 0x18);
    if (*(int *)(local_34 + 0x3c4) == -1) {
      FUN_00696e08();
      *(undefined4 *)(local_34 + 0x18) = 0;
      *(int *)(local_34 + 0x330) = *(int *)(local_34 + 0x330) + local_38;
      *in_FS_OFFSET = local_30;
      uVar4 = local_30;
    }
    else {
      local_40 = FUN_00478d80(*(undefined4 *)(local_34 + 0x24c),*(undefined4 *)(local_34 + 0x3c4));
      local_41 = '\0';
      local_20 = 0xc;
      FUN_0047056c(local_c,s_Cambria_20Math_006db988);
      local_14 = local_14 + 2;
      iVar3 = FUN_00476af8(local_40 + 0x74,local_c);
      local_14 = local_14 + -2;
      FUN_0046e6f8(local_c,2);
      if (iVar3 != 0) {
        local_41 = '\x01';
      }
      local_7c = 0;
      FUN_00478e80(local_3a4);
      if (-1 < *(int *)(local_40 + 0x18)) {
        local_7c = FUN_00478ed0(*(undefined4 *)(local_34 + 0x248),*(undefined4 *)(local_40 + 0x18));
      }
      local_80 = 0;
      local_84 = 1;
      uVar4 = FUN_00478fd0(local_94,0,local_34,*(undefined4 *)(local_34 + 0x3c8),0);
      FUN_004a4130(uVar4,local_34 + 0x4bc,&local_8c);
      FUN_00479008(&local_8c);
      local_64 = (float)in_ST0;
      uVar4 = FUN_00478fd0(local_9c);
      FUN_004a4130(uVar4,local_34 + 0x4bc,&local_a4);
      local_8c = local_a4;
      local_88 = local_a0;
      FUN_00479008(&local_8c);
      local_70 = (float)(in_ST1 / (longdouble)local_64);
      uVar4 = FUN_00478fd0(local_ac);
      FUN_004a4130(uVar4,local_34 + 0x474,&local_b4);
      local_8c = local_b4;
      local_88 = local_b0;
      local_b8 = (uint)(*(int *)(local_34 + 0x3cc) == 3);
      if (*(int *)(local_34 + 0x1ec) == 0) {
        if ((double)local_64 < (double)DAT_006ee118 - _DAT_00478d64) {
          if (local_64 <= (float)(DAT_006ee118 + -3)) {
            local_b8 = local_b8 | 0x80000;
          }
          else {
            local_b8 = local_b8 | 2;
          }
        }
        if ((*(float *)(local_34 + 0x3bc) < _DAT_00478d6c) || (local_70 < _DAT_00478d6c)) {
          if ((_DAT_00478d70 < *(float *)(local_34 + 0x3bc)) || (_DAT_00478d70 < local_70)) {
            local_b8 = local_b8 | 8;
          }
          else {
            local_b8 = local_b8 | 0x100000;
          }
        }
        if ((_DAT_00478d74 < *(float *)(local_34 + 0x3bc)) || (_DAT_00478d74 < local_70)) {
          uVar5 = 0x10;
        }
        else {
          uVar5 = 0;
        }
        local_b8 = local_b8 | uVar5;
      }
      else {
        uVar5 = local_b8 | 0x20000;
        if ((double)local_64 < (double)DAT_006ee118 - _DAT_00478d64) {
          if (local_64 <= (float)(DAT_006ee118 + -3)) {
            uVar5 = local_b8 | 0xa0000;
          }
          else {
            uVar5 = local_b8 | 0x20002;
          }
        }
        local_b8 = uVar5;
        if ((*(float *)(local_34 + 0x3bc) < _DAT_00478d6c) || (local_70 < _DAT_00478d6c)) {
          if ((_DAT_00478d70 < *(float *)(local_34 + 0x3bc)) || (_DAT_00478d70 < local_70)) {
            local_b8 = local_b8 | 8;
          }
          else {
            local_b8 = local_b8 | 0x100000;
          }
        }
        if ((_DAT_00478d74 < *(float *)(local_34 + 0x3bc)) || (_DAT_00478d74 < local_70)) {
          uVar5 = 0x10;
        }
        else {
          uVar5 = 0;
        }
        local_b8 = local_b8 | uVar5;
      }
      if (*(byte *)(local_34 + 0x46f) < 200) {
        if (*(byte *)(local_34 + 0x46f) < 0x33) {
          local_b8 = local_b8 | 0x200000;
        }
        else {
          local_b8 = local_b8 | 0x20;
        }
      }
      local_20 = 0x18;
      lVar9 = in_ST7;
      FUN_0046fa54(local_8);
      local_14 = local_14 + 1;
      local_20 = 0x24;
      for (local_bc = 2; local_bc < (int)(local_38 + 2); local_bc = local_bc + 1) {
        local_380[0] = 0;
        local_80 = local_80 << 8 | (uint)*(byte *)(*(int *)(local_34 + 0x18) + local_bc);
        if (local_7c == 0) {
          if (((*(int *)(local_40 + 0x6c) != 0) && (local_80 < 0x100)) &&
             (*(int *)(*(int *)(local_40 + 0x6c) + local_80 * 4) != 0)) {
            FUN_006ad418();
          }
          if ((local_380[0] == 0) && (*(int *)(local_40 + 0x68) != -1)) {
            local_c4 = FUN_0051a9a8(local_80,*(undefined4 *)(local_40 + 0x68));
            local_20 = 0x24;
            if (local_c4 != 0) {
              FUN_0051ac10(local_c4);
              FUN_006ad418();
            }
          }
LAB_0047857b:
          if (local_41 != '\0') {
            local_c6 = 0x25a1;
            local_20 = 0x24;
            if ((local_80 < 0x28f) || (0x2ae < local_80)) {
              if ((local_80 < 0x2c3) || (0x2e2 < local_80)) {
                if (local_80 == 0x2b5) {
                  local_c6 = 0x401;
                }
                else if (local_80 == 0x2e9) {
                  local_c6 = 0x451;
                }
                else if (local_80 == 3) {
                  local_c6 = 0x20;
                }
                else if ((local_80 < 0x372) || (0x37b < local_80)) {
                  if ((local_80 < 0x723) || (0x73c < local_80)) {
                    if ((0x73c < local_80) && (local_80 < 0x757)) {
                      local_c6 = (short)local_80 - 0x6dc;
                    }
                  }
                  else {
                    local_c6 = (short)local_80 - 0x6e2;
                  }
                }
                else {
                  local_c6 = (short)local_80 - 0x342;
                }
              }
              else {
                local_c6 = (short)local_80 + 0x16d;
              }
            }
            else {
              local_c6 = (short)local_80 + 0x181;
            }
            if (local_c6 == local_80) {
              local_380[0] = 0x25a1;
            }
            else {
              local_380[0] = local_c6;
            }
          }
          local_3c = FUN_006ad400();
          if (local_3c == 0) {
            *(int *)(local_34 + 0x25c) = *(int *)(local_34 + 0x25c) + 1;
            local_80 = 0;
            local_84 = 1;
            lVar10 = in_ST5;
          }
          else {
            if ((((local_84 == 2) && (local_3c == 1)) && (local_380[0] == 0x20)) &&
               (local_41 == '\0')) {
              if (local_80 == 3) {
                *(int *)(local_34 + 600) = *(int *)(local_34 + 600) + 1;
              }
              else {
                local_380[0] = 0x25a1;
                *(int *)(local_34 + 0x25c) = *(int *)(local_34 + 0x25c) + 1;
              }
            }
            else {
              *(int *)(local_34 + 600) = *(int *)(local_34 + 600) + 1;
            }
            uVar2 = FUN_00479038(local_40);
            lVar10 = lVar9;
            uVar4 = FUN_00478fd0(local_d0,uVar2,local_34,0,
                                 (float)uVar2 * *(float *)(local_34 + 0x3c8));
            FUN_004a4130(uVar4,local_40 + 0x1c,local_d8);
            FUN_004a4130(local_d8,local_34 + 0x4bc,&local_e0);
            local_8c = local_e0;
            local_88 = local_dc;
            FUN_00479008(&local_8c);
            local_68 = (float)in_ST2;
            uVar2 = FUN_004a110c(local_40,local_80);
            local_4c = (float)uVar2;
            uVar4 = FUN_00478fd0(local_e8);
            FUN_004a4130(uVar4,local_40 + 0x1c,local_f0);
            local_48 = local_f0[0];
            if ((local_380[0] == 0x20) && (local_84 == 1)) {
              local_50 = (local_f0[0] * *(float *)(local_34 + 0x3c8) + *(float *)(local_34 + 0x3b4)
                         + *(float *)(local_34 + 0x3b8)) * *(float *)(local_34 + 0x3bc);
            }
            else {
              local_50 = (local_f0[0] * *(float *)(local_34 + 0x3c8) + *(float *)(local_34 + 0x3b4))
                         * *(float *)(local_34 + 0x3bc);
            }
            local_f4 = local_f0[0] * *(float *)(local_34 + 0x3c8) * *(float *)(local_34 + 0x3bc);
            local_20 = 0x24;
            uVar4 = FUN_00478fd0(local_fc,local_34,local_34,0,local_f4);
            FUN_004a4130(uVar4,local_34 + 0x4bc,local_104);
            in_ST2 = in_ST6;
            FUN_00479008(local_104);
            local_6c = (float)(in_ST3 / (longdouble)local_3c);
            in_ST6 = lVar10;
            uVar4 = FUN_00478fd0(local_110);
            FUN_004a4130(uVar4,local_40 + 0x1c,local_118);
            local_108 = local_114 * *(float *)(local_34 + 0x3c8);
            lVar11 = in_ST6;
            uVar4 = FUN_00478fd0(local_120);
            FUN_004a4130(uVar4,local_34 + 0x4bc,local_128);
            in_ST3 = in_ST7;
            in_ST7 = lVar11;
            FUN_00479008(local_128);
            local_74 = (float)in_ST4;
            uVar4 = FUN_00478fd0(local_134);
            FUN_004a4130(uVar4,local_40 + 0x1c,local_13c);
            local_12c = local_138 * *(float *)(local_34 + 0x3c8);
            uVar4 = FUN_00478fd0(local_144);
            FUN_004a4130(uVar4,local_34 + 0x4bc,local_14c);
            in_ST4 = lVar9;
            FUN_00479008(local_14c);
            local_78 = (float)in_ST5;
            local_150 = 0.76;
            if (local_74 + local_78 != _DAT_00478d78) {
              local_150 = local_74 / (local_74 + local_78);
            }
            local_54 = *(float *)(local_34 + 0x48c);
            local_58 = *(float *)(local_34 + 0x490);
            uVar4 = FUN_0047904c(local_3c8,local_58,local_54,0,local_50);
            FUN_004790b0(uVar4,local_34 + 0x474,local_3ec);
            puVar6 = local_3ec;
            puVar7 = local_3a4;
            for (iVar3 = 9; iVar3 != 0; iVar3 = iVar3 + -1) {
              *puVar7 = *puVar6;
              puVar6 = puVar6 + (uint)bVar8 * -2 + 1;
              puVar7 = puVar7 + (uint)bVar8 * -2 + 1;
            }
            local_5c = (local_38c - *(float *)(local_34 + 0x48c)) / (float)local_3c;
            local_60 = (local_388 - *(float *)(local_34 + 0x490)) / (float)local_3c;
            puVar6 = local_3a4;
            puVar7 = (undefined4 *)(local_34 + 0x474);
            for (iVar3 = 9; iVar3 != 0; iVar3 = iVar3 + -1) {
              *puVar7 = *puVar6;
              puVar6 = puVar6 + (uint)bVar8 * -2 + 1;
              puVar7 = puVar7 + (uint)bVar8 * -2 + 1;
            }
            local_154 = 0;
            local_20 = 0x24;
            lVar9 = in_ST7;
            if (0 < local_3c) {
              do {
                FUN_004791b4(&local_42c);
                FUN_004791b4(&local_424);
                FUN_004791b4(&local_41c);
                FUN_004791ec(&local_3f4);
                local_20 = 0x24;
                cVar1 = FUN_0051f1d8(CONCAT22(extraout_var,local_380[local_154]));
                if (cVar1 == '\0') {
                  local_414 = local_380[local_154];
                }
                else {
                  local_414 = 0x20;
                }
                local_158 = (undefined1 *)(local_34 + 0x46c);
                local_3f4 = *local_158;
                local_3f3 = *(undefined1 *)(local_34 + 0x46d);
                local_3f2 = *(undefined1 *)(local_34 + 0x46e);
                local_3f1 = *(undefined1 *)(local_34 + 0x46f);
                cVar1 = FUN_004a953c();
                if (cVar1 == '\0') {
                  cVar1 = FUN_004a9508();
                  if (cVar1 == '\0') {
                    uVar5 = (uint)(byte)local_414;
                    uVar4 = FUN_004a94e8();
                    if (((char)uVar4 == '\0') &&
                       (cVar1 = FUN_004a949c(uVar4,CONCAT22(extraout_var_00,local_414),uVar5,
                                             CONCAT22(extraout_var_00,local_414)), cVar1 == '\0')) {
                      *(int *)(local_34 + 0x264) = *(int *)(local_34 + 0x264) + 1;
                    }
                  }
                }
                else {
                  *(int *)(local_34 + 0x260) = *(int *)(local_34 + 0x260) + 1;
                }
                local_42c = *(undefined4 *)(local_34 + 0x4e0);
                local_428 = *(undefined4 *)(local_34 + 0x4e4);
                local_40c = local_6c;
                local_408 = local_64;
                local_404 = local_74;
                local_400 = local_78;
                local_3fc = local_150;
                local_3f8 = 0xffffffff;
                local_424 = local_54;
                local_420 = local_58;
                FUN_00479260(&local_42c,local_170,local_58,0x3fc90fdb);
                FUN_004a40f0(local_170,local_178);
                puVar12 = local_178;
                FUN_004a40f0(&local_42c,local_160,puVar12,local_40c * _DAT_00478d7c);
                FUN_00479218(&local_424,local_160,local_168);
                FUN_00479218(local_168,puVar12,&local_180);
                local_41c = local_180;
                local_418 = local_17c;
                local_54 = local_5c + local_54;
                local_58 = local_60 + local_58;
                local_410 = local_68;
                if (local_414 == 0x20) {
                  local_3f0 = local_b8 & 0xffffffdf;
                }
                else {
                  local_3f0 = local_b8;
                }
                FUN_0048e338(local_34,&local_42c);
                local_154 = local_154 + 1;
              } while (local_154 < local_3c);
            }
            local_80 = 0;
            local_84 = 1;
          }
        }
        else {
          cVar1 = FUN_004758e8(local_7c,local_80,local_84,local_380);
          if (cVar1 != '\0') goto LAB_0047857b;
          local_84 = local_84 + 1;
          if ((2 < local_84) || (lVar10 = in_ST5, local_38 + 1 == local_bc)) {
            if (2 < local_84) {
              local_bc = local_bc + -1;
            }
            local_80 = (uint)*(byte *)(*(int *)(local_34 + 0x18) + local_bc);
            local_84 = 1;
            if (((*(int *)(local_40 + 0x6c) != 0) && (local_80 < 0x100)) &&
               (*(int *)(*(int *)(local_40 + 0x6c) + local_80 * 4) != 0)) {
              FUN_006ad418();
            }
            if ((local_380[0] == 0) && (*(int *)(local_40 + 0x68) != -1)) {
              local_c0 = FUN_0051a9a8(local_80,*(undefined4 *)(local_40 + 0x68));
              local_20 = 0x24;
              if (local_c0 != 0) {
                FUN_0051ac10(local_c0);
                FUN_006ad418();
              }
            }
            goto LAB_0047857b;
          }
        }
        in_ST5 = lVar10;
      }
      FUN_00696e08();
      *(undefined4 *)(local_34 + 0x18) = 0;
      local_14 = local_14 + -1;
      uVar4 = FUN_006bf0b0(local_8,2);
      *in_FS_OFFSET = local_30;
    }
  }
  return uVar4;
}


