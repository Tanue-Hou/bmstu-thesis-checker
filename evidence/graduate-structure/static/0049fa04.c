/* ENTRY 0049fa04 NAME FUN_0049fa04 */

undefined4 FUN_0049fa04(ushort param_1)

{
  if ((param_1 == 0x401) || (param_1 == 0x451)) {
    return 1;
  }
  if (param_1 < 0x410) {
    return 0;
  }
  if (0x44f < param_1) {
    return 0;
  }
  return 1;
}


