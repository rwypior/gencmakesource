Simply generate CMakeLists.txt files for your project
-----

This script generates CMakeLists.txt files for your CMake project. The only requirement is Python present in your environment.
The script will create CMakeLists.txt file with single `target_sources` directive in it. `target` for `target_sources` will
be found automatically by the script in the closest `CMakeLists.txt` file that contains either `add_executable` or `add_library` 
in the directory structure.

### Single CMakeLists.txt for entire directory tree

```
cd [YOUR-DIRECTORY]
python gencmakesource.py -r
```

### One CMakeLists.txt for each folder in directory tree

```
cd [YOUR-DIRECTORY]
python gencmakesource.py -a
```

### Additional info

```
python gencmakesource.py --help
```
