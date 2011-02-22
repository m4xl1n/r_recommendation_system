#!/usr/bin/env python
#
#    Copyright 2011 Max Lin
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import re

def is_unreliable_dependency(pkg, depend):
    if depend == '"R"':
        return True
    if pkg == '"rocc"' and depend != '"ROCR"':
        return True
    if pkg == '"pscl"' and depend == '"gam"':
        return True
    if pkg == '"maxLik"' and depend == '"miscTools"':
        return True
    if pkg == '"gplots"' and depend == '"gtools"':
        return True
    if pkg == '"fBasics"' and depend == '"timeSeries"':
        return True
    if pkg == '"fBasics"' and depend == '"timeDate"':
        return True
    if pkg == '"fpc"' and depend == '"flexmix"':
        return True
    if pkg == '"BSDA"' and depend == '"e1071"':
        return True
    if pkg == '"earth"' and depend == '"plotrix"':
        return True
    if pkg == '"testthat"' and depend == '"stringr"':
        return True
    if pkg == '"ROCR"' and depend == '"gplots"':
        return True
    if pkg == '"mlogit"' and depend == '"statmod"':
        return True
    if pkg == '"RcmdrPlugin.survival"' and depend == '"date"':
        return True
    if pkg == '"sqldf"' and depend == '"RSQLite.extfuns"':
        return True
    if pkg == '"FactoMineR"' and depend == '"cluster"':
        return True

    return False

def clean_depends(depends_filename):
    depends = file(depends_filename).read()

    # Join broken lines
    depend1 = re.sub(r'\n([^"])', r'\1', depends)

    depend2 = ""
    i = 0
    for line in depend1.split("\n"):
        if i == 0:
            depend2 += line
            i += 1
            continue

        if line == "":
            continue

        pieces = line.rstrip().split(",")

        # Remove version strings
        depend2 += "%s,%s\n" % (pieces[0], re.sub(r'[ ]*\(.+\)', '', pieces[1]))
    
    return depend2

def parse_depends(content):
    depends = {}
    i = 0
    for line in content.split("\n"):
        if i == 0:
            i += 1
            continue

        if line == "":
            continue

        pkg, depend = line.rstrip().split(",")
        if pkg not in depends:
            depends[pkg] = set()

        if not is_unreliable_dependency(pkg, depend):
            depends[pkg].add(depend)

    return depends

def memorize(depend_map, training_filename):
    # for each user (key), remember their installed and dependent packages
    user_depends = {}

    i = 0
    for line in file(training_filename):
        if i == 0:
            i += 1
            continue

        pieces = line.rstrip().split(",")

        user = pieces[9].replace("\"", "")
        pkg = pieces[0]
        installed = pieces[10]

        if user not in user_depends:
            user_depends[user] = set()

        if installed == "1":
            user_depends[user].add(pkg)
            if pkg in depends_map:
                user_depends[user].update(depends_map[pkg])

    # remember the secondary dependent packages
    for k in range(2):
        for user in user_depends.keys():
            extra = set()
            for pkg in user_depends[user]:
                if pkg in depends_map:
                    for p in depends_map[pkg]:
                        if p not in user_depends[user]:
                            extra.add(p)
            user_depends[user].update(extra)

    return user_depends

if __name__ == "__main__":
    depends_filename = "../../data/depends.csv"
    training_filename = "../../data/training_data.csv"
    test_filename = "../../data//test_data.csv"

    depends_map = parse_depends(clean_depends(depends_filename))
    user_depends = memorize(depends_map, training_filename)

    f = file("depends.csv", "w")

    i = 0
    for line in file(test_filename):
        if i == 0:
            i += 1
            f.write("Package,User,Installed\n")
            continue

        pieces = line.rstrip().split(",")
        pkg = pieces[0]
        user = pieces[9].replace("\"", "")

        if pkg in user_depends[user]:
            installed = "1"
        else:
            installed = "NA"

        f.write("%s,%s,%s\n" % (pkg, user, installed))
    f.close()
