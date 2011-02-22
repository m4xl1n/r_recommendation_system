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

def memorize(training_filename):
    seen = {}

    i = 0
    for line in file(training_filename, "r"):
        if i == 0:
            i += 1
            continue
        
        pieces = line.rstrip().split(",")
        
        package = pieces[0]
        user = pieces[9].replace("\"", "")
        installed = pieces[10]
        
        seen[(package, user)] = installed
                     
        i += 1

    return seen

if __name__ == "__main__":
    training_filename = "../../data/training_data.csv"
    testing_filename = "../../data/test_data.csv"

    seen = memorize(training_filename)

    f = file("seen_pairs.csv", "w")
    i = 0    
    for line in file(testing_filename, "r"):
        if i == 0:
            f.write("Package,User,Installed\n")
            i += 1
            continue
        
        pieces = line.rstrip().split(",")
        package = pieces[0]
        user = pieces[9].replace("\"", "")
        installed = pieces[10]

        if (package, user) in seen: 
            installed = seen[(package, user)]

        f.write("%s\n" % ",".join([package, user, installed]))

    f.close()
