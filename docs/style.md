# Style Guide

As a **Blender** extension, **Fabex** follows the guidelines laid out by the **Blender Foundation**:

[Blender Code Best Practices](https://docs.blender.org/api/current/info_best_practice.html)

[Extension Guidelines](https://docs.blender.org/manual/en/latest/advanced/extensions/getting_started.html#how-to-create-extensions)

In short, **Blender** uses a modified version of the [pep8](https://peps.python.org/pep-0008/) standard, meaning:

- Classes are `NamedLikeThis` - no spaces, all words capitalized
- Functions, modules, variables, etc are `named_like_this` - spaces replaced with underscores, no capital letters
- No `*` imports - e.g. `from module import *` should be rewritten to specify exactly what is being imported - `from module import Class, function, variable as other_name` etc.

**Fabex** extends the default line-length to 100 to allow some of the longer equations to remain on a single line.

An auto-formatter, **Black**, has been implemented to ensure code consistency across contributions.
It will ensure that your spacing, indentation etc are in line with the project guidelines.

Most Code Editors/IDEs are able to integrate the **Black** formatter, so you can format your code while you work.

## Project Structure

**Fabex** is a huge addon, with many different functions, added by many different contributors over the course of 12 years of development!

In order to avoid conflicts, bugs and import errors a hierarchy has been established:

- First, `utilities` are at the lowest level - they depend on external libraries (e.g.: `bpy`, `shapely`, `numpy` etc) and are used to power the other classes and functions
- Second, are all the files in the main addon folder (e.g.: `cam_chunk`, `gcode_path`, `strategy`) and they use external libraries, as well as `utilities` to power Blender's functions
- Third, `properties`, `operators` and `ui` are **Blender** classes that use `utilites` and the main files to integrate **Fabex** functions into **Blender**

The rest of the files can be considered references:

- `post_processors` and `presets` will be loaded based on user selections in **Blender**
- `tests` contains automated testing functions related to Github Workflows (see the Testing page for more details)
- `wheels` conatins the pre-built Python binaries that power the external dependencies `shapely` and `opencamlib` - they are loaded automatically by **Blender**