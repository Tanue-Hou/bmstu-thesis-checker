// Read-only metadata probe; compile as x86 for the existing Locale Emulator.
using System;
using System.Reflection;
class InspectLocaleLoader {
  static int Main(string[] args) {
    if(args.Length != 1) return 2;
    var assembly=Assembly.LoadFrom(args[0]);
    foreach(var type in assembly.GetTypes()) {
      if(type.FullName.IndexOf("Loader",StringComparison.OrdinalIgnoreCase)<0) continue;
      Console.WriteLine("TYPE " + type.FullName);
      foreach(var member in type.GetMembers(BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Instance|BindingFlags.Static|BindingFlags.DeclaredOnly)) Console.WriteLine(member.MemberType+" "+member);
    }
    return 0;
  }
}
