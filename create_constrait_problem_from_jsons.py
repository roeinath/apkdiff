# #!/usr/bin/env python3
# import argparse
# import json
# import sys
# from pathlib import Path


# def pair_matching_keys(dict1, dict2):
#     """Return list of (list, list) tuples for keys present in both dicts."""
#     return [(dict1[key], dict2[key]) for key in dict1.keys() & dict2.keys()]


# def main():
#     parser = argparse.ArgumentParser(
#         description="Compare two JSON dicts (version 1 and version 2) and return paired lists for matching keys."
#     )
#     parser.add_argument("version1", type=Path, help="Path to version 1 JSON file")
#     parser.add_argument("version2", type=Path, help="Path to version 2 JSON file")

#     args = parser.parse_args()

#     try:
#         dict1 = json.loads(args.version1.read_text(encoding='utf-8'))
#         dict2 = json.loads(args.version2.read_text(encoding='utf-8'))
#     except Exception as e:
#         print(f"Error reading JSON files: {e}", file=sys.stderr)
#         sys.exit(1)
#     print(len(dict1), len(dict2), len(dict1.keys() & dict2.keys()))
#     if not isinstance(dict1, dict) or not isinstance(dict2, dict):
#         print("Both JSON files must contain top-level objects (dicts).", file=sys.stderr)
#         sys.exit(1)

#     result = pair_matching_keys(dict1, dict2)

#     with open('constraints.json', 'w', encoding='utf-8') as f:
#         json.dump(result, f)

# if __name__ == "__main__":
#     main()
#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

def pair_matching_keys(dict1, dict2):
    """Return list of (list, list) tuples for keys present in both dicts."""
    return [(dict1[key], dict2[key]) for key in dict1.keys() & dict2.keys()]

def main():
    parser = argparse.ArgumentParser(
        description="Compare two JSON dicts (version 1 and version 2) and return paired lists for matching keys."
    )
    parser.add_argument("version1", type=Path, help="Path to version 1 JSON file")
    parser.add_argument("version2", type=Path, help="Path to version 2 JSON file")
    parser.add_argument(
        "output",
        type=Path,
        help="Path to output JSON file where paired lists will be saved"
    )

    args = parser.parse_args()

    try:
        dict1 = json.loads(args.version1.read_text(encoding='utf-8'))
        dict2 = json.loads(args.version2.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"Error reading JSON files: {e}", file=sys.stderr)
        sys.exit(1)

    print(len(dict1), len(dict2), len(dict1.keys() & dict2.keys()))

    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        print("Both JSON files must contain top-level objects (dicts).", file=sys.stderr)
        sys.exit(1)

    result = pair_matching_keys(dict1, dict2)

    with args.output.open('w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)

    print(f"Paired lists saved to {args.output}")

if __name__ == "__main__":
    main()
