# JEB Python script
# Export class fields and method signatures into JSON:
# { 'Class': { 'fields': {...}, 'methods': {...} } }

import json
import os
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit

DEFAULT_OUT = "classes_meta.json"

class ExportClassMeta(IScript):
    def run(self, ctx):
        prj = ctx.getMainProject()
        if not prj:
            ctx.print("Open a project first.")
            return

        dex_units = [u for u in prj.getLiveUnits() if isinstance(u, IDexUnit)]
        if not dex_units:
            ctx.print("No DEX units in this project.")
            return

        outpath = ctx.displayInput("Output JSON path", DEFAULT_OUT)
        if not outpath:
            outpath = DEFAULT_OUT

        result = {}

        for dex in dex_units:
            for c in dex.getClasses():
                cname = normalizeClassName(c.getName(True))
                class_map = result.setdefault(cname, {"fields": {}, "methods": {}})

                # Fields
                for f in c.getFields():
                    ftype = f.getType().getSignature(True)
                    class_map["fields"][f.getName()] = ftype

                # Methods
                for m in c.getMethods():
                    proto = m.getPrototype()
                    if not proto:
                        continue
                    ret_type = proto.getReturnType().getSignature(True) if proto.getReturnType() else "V"

                    arglist = []
                    params = m.getParameters()  # IDexParameter list
                    if params:
                        for idx, p in enumerate(params):
                            pname = p.getName() if p.getName() else "arg%d" % idx
                            ptype = p.getType().getSignature(True)
                            arglist.append({
                                "arg name": pname,
                                "arg type": ptype
                            })

                    class_map["methods"][m.getName()] = {
                        "return type": ret_type,
                        "args": arglist
                    }

        # Remove classes with no members
        result = {k: v for k, v in result.items() if v["fields"] or v["methods"]}

        with open(outpath, "w") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        ctx.print("✅ Exported %d classes to %s" % (len(result), outpath))


def normalizeClassName(raw):
    # Convert Lcom/example/Foo; → com/example/Foo
    if raw.startswith("L") and raw.endswith(";"):
        return raw[1:-1]
    return raw
