import os
import re

__all__ = ["find_all_specs", "find_spec_lines", "find_step_modules"]


def find_all_specs(repo_path, this_type_only=None, debug=False):
    d_specs = {}
    spec_files = find_step_modules(repo_path)
    for f in spec_files:
        s = find_spec_lines(f, this_type_only=this_type_only, debug=debug)
        if s:
            d_specs[f] = s

    if debug:
        if len(d_specs) < 1:
            print("\nNo specs found!")
        else:
            for key, vals in d_specs.items():
                print(f"\n*** {os.path.basename(key)}")
                for v in vals:
                    print(f"    {v}")

    return d_specs


def find_spec_lines(filename, this_type_only=None, debug=False):
    """Find JWST step specs in given step Python module."""
    found_start = False
    start_text = 'spec = """'
    end_text = '"""'
    spec_lines = []
    patt = r"\w*\s*=\s*(\w*)\(.*"

    if debug:
        print(f"*** Processing {filename}")

    with open(filename) as fin:
        for line in fin:
            if not found_start and start_text in line:
                if debug:
                    print(f"Found start: {line}")
                found_start = True
                continue
            if found_start:
                if end_text in line:
                    if debug:
                        print(f"Found end: {line}")
                    break
                spec_txt = line.strip()
                if this_type_only:
                    match = re.match(patt, spec_txt)
                    if not match:
                        if debug:
                            print(f"re.match failed: {spec_txt}")
                        continue
                    typ = match.group(1)
                    if typ == this_type_only:
                        if debug:
                            print(f"Found wanted type: {typ}")
                        spec_lines.append(spec_txt)
                    elif debug:
                        print(f"Ignoring unwanted type: {typ}\n    {spec_txt}")
                else:
                    spec_lines.append(spec_txt)

    if debug and not found_start:
        print(f"Never found: {start_text}")

    return spec_lines


def find_step_modules(repo_path):
    """Find JWST step modules in the given repo checkout path."""
    step_modules = []
    for root, _, files in os.walk(repo_path):
        for f in files:
            if f.endswith("step.py") and not f.startswith("test"):
                step_modules.append(os.path.join(root, f))
    return sorted(step_modules)
