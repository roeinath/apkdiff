import subprocess
import sys
import json
import os

def analyze_apk(apk_path):
    # Example: call your run_pipeline.py for a single APK (customize as needed)
    # Here, just return the filename for demo
    return {'analyzed_apk': os.path.basename(apk_path)}

def compare_apks(apk1_path, apk2_path):
    # Example: call your run_pipeline.py or compare_tools.py for two APKs
    # Here, just return the filenames for demo
    return {'compared_apks': [os.path.basename(apk1_path), os.path.basename(apk2_path)]}
