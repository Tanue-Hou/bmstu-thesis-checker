/* ENTRY 004db60c NAME FUN_004db60c */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4
FUN_004db60c(undefined4 param_1,undefined4 param_2,undefined4 param_3,float param_4,float param_5)

{
  undefined4 uVar1;
  
  if (param_4 - _DAT_004db64c <= param_5) {
    param_4 = param_4 + _DAT_004db64c;
    if (param_4 < param_5) {
      uVar1 = 0;
    }
    else {
      uVar1 = CONCAT31((int3)(CONCAT22((short)((uint)param_1 >> 0x10),
                                       (ushort)(param_4 < param_5) << 8 |
                                       (ushort)(NAN(param_4) || NAN(param_5)) << 10 |
                                       (ushort)(param_4 == param_5) << 0xe) >> 8),1);
    }
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}


