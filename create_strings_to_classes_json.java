import soot.*;
import soot.jimple.StringConstant;
import soot.options.Options;
import soot.util.Chain;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import java.io.FileWriter;
import java.io.IOException;
import java.util.*;

public class ApkStringsToJson {
    public static void main(String[] args) {
        if (args.length != 3) {
            System.err.println("Usage: ApkStringsToJson <path-to-apk> <output-json> <package-prefix>");
            System.exit(1);
        }
        String apk = args[0];
        String outJson = args[1];
        String packagePrefix = args[2]; // e.g., "com.example"

        G.reset();

        Options.v().set_src_prec(Options.src_prec_apk);
        Options.v().set_android_jars("D:\\AndroidSDK\\platforms");
        Options.v().set_process_dir(Collections.singletonList(apk));
        Options.v().set_allow_phantom_refs(true);
        Options.v().set_process_multiple_dex(true);
        Options.v().set_whole_program(true);
        Options.v().set_output_format(Options.output_format_none);

        Scene.v().loadNecessaryClasses();

        // Map<StringConstant, Set<ClassName>>
        Map<String, Set<String>> stringToClasses = new TreeMap<>();
        int total_classes = 0;
        int classes_with_strings = 0;
        for (SootClass cls : Scene.v().getApplicationClasses()) {
            if (!cls.getName().startsWith(packagePrefix)) {
                continue;
            }
            Boolean isFirst = true;
            total_classes += 1;
            for (SootMethod m : cls.getMethods()) {
                if (m.isConcrete()) {
                    try {
                        Body body = m.retrieveActiveBody();
                        Chain<Unit> units = body.getUnits();

                        for (Unit u : units) {
                            for (ValueBox vb : u.getUseAndDefBoxes()) {
                                Value val = vb.getValue();
                                if (val instanceof StringConstant) {
                                    String s = ((StringConstant) val).value;
                                    if (!s.equals("")){
                                        stringToClasses
                                            .computeIfAbsent(s, k -> new TreeSet<>())
                                            .add(cls.getName());  
                                        if (isFirst) {
                                            classes_with_strings += 1;
                                            isFirst = false;
                                        } 
                                    }
                                }
                            }
                        }
                    } catch (Exception e) {
                        // ignore methods without body
                    }
                }
            }
        }

        // Use Gson to pretty-print JSON
        Gson gson = new GsonBuilder().setPrettyPrinting().create();

        try (FileWriter writer = new FileWriter(outJson)) {
            gson.toJson(stringToClasses, writer);
        } catch (IOException e) {
            e.printStackTrace();
        }

        System.out.println("### Found string literals from " + classes_with_strings + " classes. (There are " + total_classes + " classes total)");
    }
}
