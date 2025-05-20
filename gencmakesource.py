import sys
import os
import argparse
import re
import textwrap
from pathlib import Path

parser = argparse.ArgumentParser(
    prog="Generate CMakeLists.txt file with target_sources"
)
parser.add_argument("-p", "--path", default=os.getcwd(), help="Directory to process. If empty, set current directory")
parser.add_argument("-t", "--target", help="CMake target. If empty - script attempts to automatically deduce from nearest CMakeLists.txt file")
parser.add_argument("-e", "--targettype", default="executable", help="CMake target type - may be one of: executable, library. Default - executable", choices=['executable', 'library'])
parser.add_argument("-l", "--length", default=120, help="Maximum line length")
parser.add_argument("-x", "--extensions", nargs="+", default=[".h", ".hpp", ".hxx", ".c", ".cpp", ".cxx"], help="File extensions to include, extensions start with dot (.)")
parser.add_argument("-f", "--force", help="Write file even if file with the same name exists", action="store_true")
parser.add_argument("-d", "--dryrun", help="Only print script's actions without executing them", action="store_true")

excl1 = parser.add_mutually_exclusive_group()
excl1.add_argument("-r", "--recursive", help="Include subdirectories in target_sources - creates single CMakeLists.txt file", action="store_true")
excl1.add_argument("-a", "--recursive-each", help="Execute the script for all subdirectories separarely - creates one CMakeLists.txt file in each subdirectory", action="store_true")

args = parser.parse_args()

def findTargetExecutable(source):
    return re.search(r'add_executable\W*\(\W*?(.+?)\W', source)

def findTargetLibrary(source):
    return re.search(r'add_library\W*\(\W*?(.+?)\W', source)

def findTarget(source, type):
    if type == "executable":
        return findTargetExecutable(source)
    elif type == "library":
        return findTargetLibrary(source)
    return None

def getTarget(cmakelists, defaultTarget, targetType):
    if defaultTarget:
        return defaultTarget
    
    if os.path.exists(cmakelists):
        with open(cmakelists) as f:
            contents = f.read()
            match = findTarget(contents, targetType)
            if match:
                return match.group(1)
        
    return None

def getParentCmakelists(path):
    parent = Path(path).parent
    while(parent and os.path.realpath(os.path.dirname(parent)) != os.path.realpath(parent)):
        cmakelists = parent / "CMakeLists.txt"
        if(cmakelists.exists()):
            return cmakelists
        else:
            return getParentCmakelists(parent)
    return None

def findFiles(path, extensions, recursive, prefix=Path()):
    result = []
    for entry in os.listdir(path):
        if os.path.isdir(entry) and recursive:
            result += findFiles(Path(path) / entry, extensions, recursive, prefix / entry)
        else:
            ext = os.path.splitext(entry)[1]
            if ext in extensions:
                result.append(prefix / entry)
    return result

path = os.path.realpath(args.path)
targettype = args.targettype
cmakelistsPath = path
target = None
while target is None:
    cmakelists = getParentCmakelists(cmakelistsPath)

    target = getTarget(cmakelists, args.target, targettype)
    if target is None:
        cmakelistsPath = Path(cmakelistsPath).parent
    else:
        print(f"Found target \"{target}\" in \"{cmakelists}\"")

length = args.length
extensions = args.extensions
recursive = args.recursive
recursiveeach = args.recursive_each
force = args.force
dryrun = args.dryrun

def createCmakeLists(path, extensions, recursive, target, length, force, dryrun):
    files = findFiles(path, extensions, recursive)

    if not files:
        return

    cmakelistsFile = Path(path) / "CMakeLists.txt"

    filesTxt = textwrap.wrap(" ".join([f"\"{file}\"" for file in files]), width=length)
    cmakelistsContent = f"target_sources({target} PRIVATE\n"
    cmakelistsContent += "\t" + "\n\t".join(filesTxt)
    cmakelistsContent += "\n)"

    if dryrun:
        print("===== Dry run =====")
        print(f"Write file {cmakelistsFile} with contents:")
        print(cmakelistsContent)
        return

    if Path.exists(cmakelistsFile):
        if not force:
            print(f"File {cmakelistsFile} already exists")
            return
        else:
            with open(cmakelistsFile, "r") as f:
                c = f.read()
                if c.strip() == cmakelistsContent.strip():
                    print("File was not changed, skipping")
                    return

    with open(cmakelistsFile, "w") as f:
        f.write(cmakelistsContent)

def createCmakeListsRecursive(path, extensions, target, length, force, dryrun):
    createCmakeLists(path, extensions, False, target, length, force, dryrun)
    dirs = (dir for dir in os.listdir(path) if os.path.isdir(os.path.join(path, dir)))
    for dir in dirs:
        p = os.path.join(path, dir)
        createCmakeListsRecursive(p, extensions, target, length, force, dryrun)

if recursiveeach:
    createCmakeListsRecursive(path, extensions, target, length, force, dryrun)
else:
    createCmakeLists(path, extensions, recursive, target, length, force, dryrun)