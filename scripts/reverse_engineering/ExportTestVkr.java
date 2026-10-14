// Export recovered pseudocode, function boundaries and callers. Not original source.
// @category TestVkr
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

public class ExportTestVkr extends GhidraScript {
    public void run() throws Exception {
        Path out = Paths.get(getScriptArgs()[0]);
        Files.createDirectories(out);
        DecompInterface decompiler = new DecompInterface();
        decompiler.openProgram(currentProgram);
        int count = 0, success = 0, failed = 0;
        long deadline = System.currentTimeMillis() + 600000;
        try (BufferedWriter code = Files.newBufferedWriter(out.resolve("recovered_pseudocode.c"), StandardCharsets.UTF_8);
             BufferedWriter index = Files.newBufferedWriter(out.resolve("functions.tsv"), StandardCharsets.UTF_8);
             BufferedWriter calls = Files.newBufferedWriter(out.resolve("calls.tsv"), StandardCharsets.UTF_8);
             BufferedWriter strings = Files.newBufferedWriter(out.resolve("defined_strings.tsv"), StandardCharsets.UTF_8)) {
            code.write("/* Ghidra recovered pseudocode; NOT original source. Target: " + currentProgram.getExecutableSHA256() + " */\n");
            index.write("address\tname\tbody_bytes\tstatus\terror\n");
            calls.write("caller\tcallee\n");
            strings.write("address\tvalue\treference_from\n");
            FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);
            while (functions.hasNext() && !monitor.isCancelled()) {
                Function f = functions.next();
                for (Function callee : f.getCalledFunctions(monitor))
                    calls.write(f.getEntryPoint()+"\t"+callee.getEntryPoint()+"\n");
                String status = "not_attempted_budget", error = "";
                if (System.currentTimeMillis() < deadline && !f.isExternal()) {
                    DecompileResults result = decompiler.decompileFunction(f, 5, monitor);
                    if (result.decompileCompleted() && result.getDecompiledFunction() != null) {
                        status = "decompiled";
                        code.write("\n/* ENTRY " + f.getEntryPoint() + " NAME " + f.getName() + " */\n");
                        code.write(result.getDecompiledFunction().getC());
                        success++;
                    } else {
                        status = "failed_or_timeout";
                        error = result.getErrorMessage().replace('\n', ' ').replace('\t', ' ');
                        failed++;
                    }
                }
                index.write(f.getEntryPoint()+"\t"+f.getName()+"\t"+f.getBody().getNumAddresses()+"\t"+status+"\t"+error+"\n");
                count++;
                if (count % 200 == 0) { println("EXPORT_PROGRESS " + count + " success=" + success); code.flush(); index.flush(); }
            }
            DataIterator data = currentProgram.getListing().getDefinedData(true);
            while (data.hasNext()) {
                Data d = data.next();
                if (!d.hasStringValue()) continue;
                String value = String.valueOf(d.getValue()).replace('\t',' ').replace('\n',' ');
                ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(d.getAddress());
                boolean found = false;
                while (refs.hasNext()) { found = true; strings.write(d.getAddress()+"\t"+value+"\t"+refs.next().getFromAddress()+"\n"); }
                if (!found) strings.write(d.getAddress()+"\t"+value+"\t\n");
            }
        } finally { decompiler.dispose(); }
        String summary = "target_sha256=" + currentProgram.getExecutableSHA256()+"\nfunctions="+count+"\ndecompiled="+success+"\nfailed="+failed+"\nlimitations=Recovered C-like pseudocode; compiler runtime included; function discovery and indirect calls incomplete; per-function timeout 5 seconds; export deadline 600 seconds.\n";
        Files.writeString(out.resolve("coverage.txt"), summary, StandardCharsets.UTF_8);
        println("EXPORT_COMPLETE " + summary);
    }
}
