// Read-only metadata/IL inspection. Never invokes inspected methods.
using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using System.Collections.Generic;

class InspectLEProcStartIL {
  static readonly Dictionary<ushort, OpCode> Ops = new Dictionary<ushort, OpCode>();
  static InspectLEProcStartIL() {
    foreach (var f in typeof(OpCodes).GetFields(BindingFlags.Public | BindingFlags.Static))
      if (f.FieldType == typeof(OpCode)) { var op=(OpCode)f.GetValue(null); Ops[(ushort)op.Value]=op; }
  }
  static string TokenText(Module m, int token) {
    try {
      var member=m.ResolveMember(token);
      if (member != null) return member.ToString();
    } catch {}
    try { return "string: " + m.ResolveString(token); } catch {}
    return "token 0x" + token.ToString("x8");
  }
  static int Size(byte[] il, int p, OperandType t) {
    switch(t) {
      case OperandType.InlineNone: return 0;
      case OperandType.ShortInlineBrTarget: case OperandType.ShortInlineI: case OperandType.ShortInlineVar: return 1;
      case OperandType.InlineVar: return 2;
      case OperandType.InlineI8: case OperandType.InlineR: return 8;
      case OperandType.InlineSwitch: return 4 + 4 * BitConverter.ToInt32(il,p);
      default: return 4;
    }
  }
  static string Operand(MethodBase method, byte[] il, int p, OpCode op) {
    var module=method.Module;
    switch(op.OperandType) {
      case OperandType.InlineMethod: case OperandType.InlineField: case OperandType.InlineType:
      case OperandType.InlineTok: case OperandType.InlineString: case OperandType.InlineSig:
        return TokenText(module, BitConverter.ToInt32(il,p));
      case OperandType.ShortInlineI: return ((sbyte)il[p]).ToString();
      case OperandType.InlineI: return BitConverter.ToInt32(il,p).ToString();
      case OperandType.InlineI8: return BitConverter.ToInt64(il,p).ToString();
      case OperandType.ShortInlineVar: return il[p].ToString();
      case OperandType.InlineVar: return BitConverter.ToUInt16(il,p).ToString();
      case OperandType.ShortInlineBrTarget: return "IL_"+(p+1+(sbyte)il[p]).ToString("x4");
      case OperandType.InlineBrTarget: return "IL_"+(p+4+BitConverter.ToInt32(il,p)).ToString("x4");
      case OperandType.ShortInlineR: return BitConverter.ToSingle(il,p).ToString("R");
      case OperandType.InlineR: return BitConverter.ToDouble(il,p).ToString("R");
      case OperandType.InlineSwitch:
        int n=BitConverter.ToInt32(il,p); var labels=new List<string>(); int end=p+4+4*n;
        for(int i=0;i<n;i++) labels.Add("IL_"+(end+BitConverter.ToInt32(il,p+4+4*i)).ToString("x4"));
        return String.Join(",",labels);
      default: return "";
    }
  }
  static void Dump(MethodInfo method) {
    Console.WriteLine("\nMETHOD " + method.DeclaringType.FullName + "." + method.Name + " token=0x" + method.MetadataToken.ToString("x8"));
    var body=method.GetMethodBody(); if(body==null) { Console.WriteLine("<no body>"); return; }
    var il=body.GetILAsByteArray(); int p=0;
    while(p<il.Length) {
      int start=p; ushort code=il[p++]; if(code==0xfe) code=(ushort)(0xfe00|il[p++]);
      OpCode op; if(!Ops.TryGetValue(code,out op)) { Console.WriteLine("IL_"+start.ToString("x4")+" <unknown>"); break; }
      int size=Size(il,p,op.OperandType); string operand=Operand(method,il,p,op);
      Console.WriteLine("IL_"+start.ToString("x4")+"  "+op.Name+(operand==""?"":" "+operand)); p+=size;
    }
  }
  static int Main(string[] args) {
    if(args.Length!=1) return 2;
    var asm=Assembly.LoadFrom(args[0]);
    var type=asm.GetType("LEProc.LoaderWrapper",false);
    if(type==null) { Console.Error.WriteLine("LEProc.LoaderWrapper not found"); return 3; }
    var methods=type.GetMethods(BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Instance|BindingFlags.Static|BindingFlags.DeclaredOnly);
    var start=methods.FirstOrDefault(m=>m.Name=="Start");
    if(start==null) { Console.Error.WriteLine("Start not found"); return 4; }
    Dump(start);
    foreach(var method in methods.Where(m=>m!=start && m.GetMethodBody()!=null)) Dump(method);
    return 0;
  }
}
