import os
import sys
import subprocess

RECALCULATE_HASHES = True


def concat_hash_files(directory):
    """Concatenate hash files from two directories."""
    fv_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith("__fv.txt"):
                fv_files.append(os.path.join(root, file))  # Only filename, not full path
    print(f"Found {len(fv_files)} files with __fv.txt suffix in {directory}")
    with open(os.path.join(directory, '__fv.txt'), 'w') as outfile:
        for fname in fv_files:
            with open(fname, 'r') as infile:
                outfile.write(f'### file: {fname[:-8]}\n'+infile.read())

hash_clac_cmd = 'file_verification.exe --algorithm MD5 --file '


def get_sha1_list(root_dir):
    if RECALCULATE_HASHES:
        res = subprocess.run([hash_clac_cmd+f'"{root_dir}"'], shell=True)
    with open(os.path.join(root_dir, '__fv.txt'), 'r') as f:
        pass

def intersection_size(list1, list2):
    return len(set(list1) & set(list2))

def main(dir1, dir2):
    concat_hash_files(dir1)
    # print('Intersection:', intersection_size(sha_list1, sha_list2))

# List all files
# Compute all the hashes for the first 8192 bytes of each file
# first try to compare the hashes of files with the same name
# Then try to find intersections according to hierarchy
# This should cover third of the classes

# Things to do:
# compare strings
# compare content of methods without registers and names
# process only classes inside specific package
# Make the filtering modular and ignore files in ignore.txt

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <directory1> <directory2>")
        sys.exit(1)

    dir1, dir2 = sys.argv[1], sys.argv[2]

    if not os.path.isdir(dir1) or not os.path.isdir(dir2):
        print("Both arguments must be valid directories.")
        sys.exit(1)
    main(dir1, dir2)