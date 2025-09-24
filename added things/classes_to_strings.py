# JEB Python (Jython) script
# Collect string literals per method and export as JSON:
# { 'className': { 'methodSignature': ['s1','s2', ...], ... }, ... }

import json
import os

from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units import IUnit
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit
from com.pnfsoftware.jeb.core.units.code import ICodeItem
from java.util import ArrayList

# Some JEB builds expose Dalvik opcodes/mnemonics via these packages
# We only rely on instruction.getMnemonic() and getParameters()
# to keep compatibility across versions.

DEFAULT_OUT = "strings_by_class_method.json"

class StringsPerMethodExporter(IScript):
    def run(self, ctx):
        prj = ctx.getMainProject()
        if prj is None:
            ctx.print("Open a project first.")
            return

        # Find all DEX units in the project (handles multi-dex)
        dex_units = []
        for unit in prj.getLiveUnits():
            if isinstance(unit, IDexUnit):
                dex_units.append(unit)
        if not dex_units:
            ctx.print("No DEX unit found in the project.")
            return

        # Ask user for output path (falls back to default in project folder)
        outpath = ctx.displayInput("Output JSON path", DEFAULT_OUT)
        if not outpath:
            outpath = DEFAULT_OUT

        result = {}  # class -> method -> list(strings)

        for dex in dex_units:
            # Iterate classes
            for c in dex.getClasses():
                clsname = c.getName(True)  # True = internal style (Lpkg/Class;), or use False for dot
                # Convert to more readable slash-style without leading 'L' and trailing ';'
                if clsname.startswith('L') and clsname.endswith(';'):
                    clskey = clsname[1:-1]  # e.g., com/example/Foo
                else:
                    clskey = clsname

                # Prepare per-class dict
                class_map = result.setdefault(clskey, {})

                # Iterate methods
                for m in c.getMethods():
                    # Skip if no code item (abstract/native)
                    md = m.getData()
                    if md is None:
                        continue
                    code = md.getCodeItem()
                    if code is None:
                        continue

                    strings = set()

                    # Walk instructions and look for const-string(/jumbo)
                    try:
                        insns = code.getInstructions()
                        for insn in insns:
                            mnemonic = insn.getMnemonic()
                            if mnemonic is None:
                                continue
                            mn = mnemonic.lower()
                            if mn.startswith("const-string"):  # matches const-string and const-string/jumbo
                                # Parameters usually: vX, STRING@idx  (2 params)
                                params = insn.getParameters()
                                if params is None or params.size() == 0:
                                    continue
                                # Find the parameter that represents the string pool index/value
                                # Typically param[1] is a DexString reference in recent APIs.
                                s = None
                                if params.size() >= 2:
                                    p = params.get(1)
                                    try:
                                        # Many JEB builds allow .getString() or .getValue() returning an IDexString or raw string
                                        if hasattr(p, "getString") and p.getString() is not None:
                                            sObj = p.getString()
                                            s = sObj.getValue() if hasattr(sObj, "getValue") else str(sObj)
                                        elif hasattr(p, "getValue") and p.getValue() is not None:
                                            v = p.getValue()
                                            # v may already be a Python string (Jython) or a DexString
                                            if hasattr(v, "getValue"):
                                                s = v.getValue()
                                            else:
                                                s = unicode(v)  # Jython safe cast
                                    except Exception as e:
                                        # Fallback: try toString of parameter
                                        try:
                                            s = unicode(p.toString())
                                        except:
                                            pass
                                # If still not found, try any param that looks like a string
                                if s is None:
                                    for j in range(params.size()):
                                        pj = params.get(j)
                                        try:
                                            if hasattr(pj, "getString") and pj.getString() is not None:
                                                sObj = pj.getString()
                                                s = sObj.getValue() if hasattr(sObj, "getValue") else str(sObj)
                                                break
                                            if hasattr(pj, "getValue") and pj.getValue() is not None:
                                                v = pj.getValue()
                                                if isinstance(v, basestring):
                                                    s = v
                                                    break
                                                if hasattr(v, "getValue"):
                                                    s = v.getValue()
                                                    break
                                        except:
                                            pass

                                if s is not None:
                                    strings.add(unicode(s))
                    except Exception as e:
                        # Keep going even if one method fails to decode
                        ctx.print("Warning: failed to scan method %s in %s: %s" %
                                  (safeMethodSig(m), clskey, e))

                    if strings:
                        # Record using the Dalvik short signature for uniqueness, e.g. doFoo(I)V
                        mkey = safeMethodSig(m)
                        # Sort results for determinism
                        class_map[mkey] = sorted(strings)

        # Remove classes that ended up empty (possible if no methods had strings)
        result = {k: v for (k, v) in result.items() if v}

        # Ensure parent folder exists if a path was provided
        parent = os.path.dirname(outpath)
        if parent and not os.path.exists(parent):
            try:
                os.makedirs(parent)
            except Exception as e:
                ctx.print("Could not create output directory: %s" % e)

        # Write JSON (UTF-8, pretty)
        with open(outpath, "w") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        ctx.print("✅ Wrote %d classes to: %s" % (len(result), outpath))


def safeMethodSig(m):
    """
    Build a readable Dalvik-like short signature: e.g., methodName(II)Ljava/lang/String;
    """
    try:
        n = m.getName()
        pr = m.getPrototype()
        if pr is None:
            return n
        params = []
        if pr.getParameterTypes() is not None:
            for t in pr.getParameterTypes():
                params.append(t.getSignature(True))  # dalvik-style
        ret = pr.getReturnType()
        r = ret.getSignature(True) if ret is not None else "V"
        return u"%s(%s)%s" % (n, u"".join(params), r)
    except:
        # Fallback to complete signature provided by JEB
        try:
            return unicode(m.getSignature(True))
        except:
            return unicode(m.toString())
