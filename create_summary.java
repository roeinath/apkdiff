import soot.*;
import soot.jimple.StringConstant;
import soot.options.Options;
import soot.util.Chain;

import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.Collections;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.TreeSet;
import java.util.Set;

public class ApkLister {
    public static void main(String[] args) {
        if (args.length < 2) {
            System.err.println("Usage: ApkLister <path-to-apk> <output-txt> <Optional: package-prefix>");
            System.exit(1);
        }
        String apk = args[0];
        String outTxt = args[1];
        String packagePrefix = null;
        if (args.length > 2) {
            packagePrefix = args[2]; // e.g., "com.example.app"
        }

        G.reset();

        // Basic Soot options
        Options.v().set_src_prec(Options.src_prec_apk);
        Options.v().set_android_jars("D:\\AndroidSDK\\platforms"); // your SDK platforms dir
        Options.v().set_process_dir(Collections.singletonList(apk));
        Options.v().set_allow_phantom_refs(true);
        Options.v().set_process_multiple_dex(true);
        Options.v().set_whole_program(true);
        Options.v().set_output_format(Options.output_format_none);

        // Load classes
        Scene.v().loadNecessaryClasses();

        MessageDigest md5Digest = null;
        try{
            md5Digest = MessageDigest.getInstance("MD5");
        } catch (NoSuchAlgorithmException e) {
            System.err.println("MD5 algorithm not found.");
            System.exit(1);
        }
        

        try (PrintWriter pw = new PrintWriter(new FileWriter(outTxt))) {
            for (SootClass cls : Scene.v().getApplicationClasses()) {
                if (packagePrefix != null && !cls.getName().startsWith(packagePrefix)) {
                    continue; // Skip classes not in the specified package
                }
                pw.println("CLASS " + cls.getName());
                for (SootMethod m : cls.getMethods()) {
                    //printHash(pw, m, md5Digest);
                    printStrings(pw, m);
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    public static void printHash(PrintWriter pw, SootMethod m, MessageDigest md5Digest){
        String hash = "";
        if (m.isConcrete()) {
            try {
                Body body = m.retrieveActiveBody();
                String bodyStr = body.toString(); // Jimple representation
                hash = md5Digest.digest(bodyStr.getBytes())
                        .toString(); // Convert to hex string
                pw.println(bodyStr);
            } catch (Exception e) {
                // Method might have no body or fail to retrieve
                hash = "NO_BODY";
            }
        } else {
            hash = "ABSTRACT_OR_NATIVE";
        }
        pw.println("  METHOD " + m.getSignature() + " MD5=" + hash);
    }

    public static void printStrings(PrintWriter pw, SootMethod m){
        Set<String> stringsInMethod = new TreeSet<>(); // TreeSet for sorted order

        if (m.isConcrete()) {
            try {
                Body body = m.retrieveActiveBody();
                Chain<Unit> units = body.getUnits();

                for (Unit u : units) {
                    for (ValueBox vb : u.getUseAndDefBoxes()) {
                        Value val = vb.getValue();
                        if (val instanceof StringConstant) {
                            stringsInMethod.add(((StringConstant) val).value);
                        }
                    }
                }
            } catch (Exception e) {
                // ignore methods without body
            }
        }

        pw.println("  METHOD " + m.getSignature());
        for (String s : stringsInMethod) {
            pw.println("    STRING: \"" + s + "\"");
        }
    }
}
