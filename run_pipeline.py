# import subprocess
# import sys
# import os
# import argparse

# def run_command(cmd):
#     """Run a single command and print its output live."""
#     print(f"\n>>> Running: {' '.join(cmd)}")
#     process = subprocess.Popen(
#         cmd,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.STDOUT,
#         text=True
#     )

#     # Print output line by line
#     for line in process.stdout:
#         print(line, end='')

#     process.wait()
#     if process.returncode != 0:
#         print(f"❌ Command failed with exit code {process.returncode}")
#         sys.exit(process.returncode)

# def main():
#     parser = argparse.ArgumentParser(description="Run APK comparison pipeline.")
#     parser.add_argument("apk1", help="First APK file")
#     parser.add_argument("package1", help="Package name for first APK")
#     parser.add_argument("apk2", help="Second APK file")
#     parser.add_argument("package2", help="Package name for second APK")
#     parser.add_argument("--force", action="store_true",
#                         help="If set, re-generate the JSONs even if they exist")

#     args = parser.parse_args()

#     apk1, package1, apk2, package2 = args.apk1, args.package1, args.apk2, args.package2
#     force = args.force

#     # Derive base names
#     base1 = os.path.splitext(os.path.basename(apk1))[0]
#     base2 = os.path.splitext(os.path.basename(apk2))[0]

#     # JSON artifacts
#     json1 = f"{base1}.json"
#     json2 = f"{base2}.json"
#     constraints_json = f"constraints_{base1}_vs_{base2}.json"
#     matches_json = f"matches_{base1}_vs_{base2}.json"

#     # Step 1: generate json1
#     if force or not os.path.exists(json1):
#         run_command([
#             "java", "-cp", "soot-4.6.0-jar-with-dependencies.jar",
#             "create_strings_to_classes_json.java",
#             apk1, json1, package1
#         ])
#     else:
#         print(f"✅ Skipping {json1}, already exists.")

#     # Step 2: generate json2
#     if force or not os.path.exists(json2):
#         run_command([
#             "java", "-cp", "soot-4.6.0-jar-with-dependencies.jar",
#             "create_strings_to_classes_json.java",
#             apk2, json2, package2
#         ])
#     else:
#         print(f"✅ Skipping {json2}, already exists.")

#     # Step 3: generate constraints
#     run_command([
#         "python", "create_constrait_problem_from_jsons.py",
#         json1, json2, constraints_json
#     ])

#     # Step 4: solve matches
#     run_command([
#         "python", "solve_class_matches_between_versions.py",
#         constraints_json, matches_json
#     ])

#     print("\n✅ Pipeline finished successfully!")
#     print("Artifacts generated:")
#     print(f"- {json1}")
#     print(f"- {json2}")
#     print(f"- {constraints_json}")
#     print(f"- {matches_json}")

# if __name__ == "__main__":
#     main()
import subprocess
import sys
import os
import argparse
import logging

# Configure logging
logger = logging.getLogger("pipeline")
logger.setLevel(logging.DEBUG)

# File handler: all DEBUG+ go to file
file_handler = logging.FileHandler("pipeline.log", mode="w", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Stream handler: only INFO+ to stdout
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
stream_formatter = logging.Formatter("%(message)s")
stream_handler.setFormatter(stream_formatter)
logger.addHandler(stream_handler)

def run_command(cmd):
    """Run a single command and print its output live."""
    logger.debug("Running command: %s", " ".join(cmd))
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    # Print command output line by line as INFO
    for line in process.stdout:
        logger.info(line.rstrip())

    process.wait()
    if process.returncode != 0:
        logger.info(f"Command failed with exit code {process.returncode}")
        sys.exit(process.returncode)

def main():
    parser = argparse.ArgumentParser(description="Run APK comparison pipeline.")
    parser.add_argument("apk1", help="First APK file")
    parser.add_argument("package1", help="Package name for first APK")
    parser.add_argument("apk2", help="Second APK file")
    parser.add_argument("package2", help="Package name for second APK")
    parser.add_argument("--force", action="store_true",
                        help="If set, re-generate the JSONs even if they exist")

    args = parser.parse_args()
    apk1, package1, apk2, package2 = args.apk1, args.package1, args.apk2, args.package2
    force = args.force

    # Derive base names
    base1 = os.path.splitext(os.path.basename(apk1))[0]
    base2 = os.path.splitext(os.path.basename(apk2))[0]

    # JSON artifacts
    json1 = f"{base1}.json"
    json2 = f"{base2}.json"
    constraints_json = f"constraints_{base1}_vs_{base2}.json"
    matches_json = f"matches_{base1}_vs_{base2}.json"

    # Step 1: generate json1
    if force or not os.path.exists(json1):
        run_command([
            "java", "-cp", "soot-4.6.0-jar-with-dependencies.jar",
            "create_strings_to_classes_json.java",
            apk1, json1, package1
        ])
    else:
        logger.info(f"Skipping {json1}, already exists.")

    # Step 2: generate json2
    if force or not os.path.exists(json2):
        run_command([
            "java", "-cp", "soot-4.6.0-jar-with-dependencies.jar",
            "create_strings_to_classes_json.java",
            apk2, json2, package2
        ])
    else:
        logger.info(f"Skipping {json2}, already exists.")

    # Step 3: generate constraints
    run_command([
        "python", "create_constrait_problem_from_jsons.py",
        json1, json2, constraints_json
    ])

    # Step 4: solve matches
    run_command([
        "python", "solve_class_matches_between_versions.py",
        constraints_json, matches_json
    ])

    logger.info("\nPipeline finished successfully!")
    logger.info("Artifacts generated:")
    logger.info(f"- {json1}")
    logger.info(f"- {json2}")
    logger.info(f"- {constraints_json}")
    logger.info(f"- {matches_json}")

if __name__ == "__main__":
    main()
