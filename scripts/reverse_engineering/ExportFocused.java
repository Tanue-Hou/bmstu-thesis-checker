// @category TestVkr
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.data.*;
import ghidra.program.model.symbol.SourceType;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.io.*;

public class ExportFocused extends GhidraScript {
    public void run() throws Exception {
        Path out = Paths.get(getScriptArgs()[0]);
        Files.createDirectories(out);
        String[] addresses = {"0041ae88", "0041aebe", "004374e3", "004af82c", "004d0694", "004d0a08"};
        DecompInterface decompiler = new DecompInterface();
        decompiler.openProgram(currentProgram);
        try (BufferedWriter status = Files.newBufferedWriter(out.resolve("focused-status.tsv"), StandardCharsets.UTF_8)) {
            status.write("address\tstatus\terror\n");
            for (String address : addresses) {
                Function f = getFunctionAt(toAddr(address));
                if (f == null) {status.write(address+"\tmissing\t\n"); continue;}
                if (address.equals("0041ae88") || address.equals("0041aebe") || address.equals("004374e3")) {
                    // x87 ST0 return is observed in disassembly. Preserve it instead of inferred void.
                    ParameterImpl[] parameters;
                    if (address.equals("004374e3")) {
                        parameters = new ParameterImpl[] {
                            new ParameterImpl("nmsedec", IntegerDataType.dataType, 4, currentProgram),
                            new ParameterImpl("compno", IntegerDataType.dataType, 8, currentProgram),
                            new ParameterImpl("level", IntegerDataType.dataType, 12, currentProgram),
                            new ParameterImpl("orient", IntegerDataType.dataType, 16, currentProgram),
                            new ParameterImpl("bpno", IntegerDataType.dataType, 20, currentProgram),
                            new ParameterImpl("qmfbid", IntegerDataType.dataType, 24, currentProgram),
                            new ParameterImpl("stepsize", DoubleDataType.dataType, 28, currentProgram),
                            new ParameterImpl("numcomps", IntegerDataType.dataType, 36, currentProgram),
                            new ParameterImpl("mct_norms", new PointerDataType(DoubleDataType.dataType,4), 40, currentProgram),
                            new ParameterImpl("mct_numcomps", IntegerDataType.dataType, 44, currentProgram)
                        };
                    } else {
                        parameters = new ParameterImpl[] {
                            new ParameterImpl("level", IntegerDataType.dataType, 4, currentProgram),
                            new ParameterImpl("orient", IntegerDataType.dataType, 8, currentProgram)
                        };
                    }
                    // Borland's default prototype inferred a hidden return pointer;
                    // assembly explicitly returns the value in x87 ST0 instead.
                    f.updateFunction("__cdecl",
                        new ReturnParameterImpl(Float10DataType.dataType, currentProgram.getRegister("ST0"), currentProgram),
                        Function.FunctionUpdateType.CUSTOM_STORAGE, true, SourceType.USER_DEFINED, parameters);
                }
                decompiler.flushCache();
                DecompileResults r = decompiler.decompileFunction(f, 90, monitor);
                String error = r.getErrorMessage().replace('\t',' ').replace('\n',' ');
                if (r.decompileCompleted() && r.getDecompiledFunction() != null) {
                    Files.writeString(out.resolve(address+".c"), "/* RECOVERED PSEUDOCODE, not original source; " + address + " */\n"+r.getDecompiledFunction().getC(), StandardCharsets.UTF_8);
                    status.write(address+"\tdecompiled\t"+error+"\n");
                } else { status.write(address+"\tfailed_or_timeout\t"+error+"\n"); }
                try (BufferedWriter assembly = Files.newBufferedWriter(out.resolve(address+".assembly.txt"), StandardCharsets.UTF_8)) {
                    InstructionIterator ins = currentProgram.getListing().getInstructions(f.getBody(), true);
                    while(ins.hasNext()) {Instruction i = ins.next();assembly.write(i.getAddress()+" "+i.toString()+"\n");}
                }
                status.flush();
                println("FOCUSED_COMPLETE " + address);
            }
        } finally { decompiler.dispose(); }
    }
}
