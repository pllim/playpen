#!/usr/bin/env python

d = {}
packagename = "astropy"
left_file = "old_deps_main.txt"
right_file = "old_deps_pr.txt"


with open(left_file, "r") as fin:
    for line in fin:
        pkgdef = line.split("\n")[0].split("==")
        name = pkgdef[0].replace("_", "-").lower()
        if name.startswith(f"{packagename} @"):
            continue
        ver = pkgdef[1]
        d[name] = [ver, None]


with open(right_file, "r") as fin:
    for line in fin:
        pkgdef = line.split("\n")[0].split("==")
        name = pkgdef[0].replace("_", "-").lower()
        if name.startswith(f"{packagename} @"):
            continue
        ver = pkgdef[1]
        if name in d:
            d[name][1] = ver
        else:
            d[name] = [None, ver]


for key in sorted(d):
    val = d[key]
    if val[0] != val[1]:
        print("*", key, val[0], "->", val[1])
