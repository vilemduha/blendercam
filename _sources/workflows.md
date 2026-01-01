# Workflows & Actions

Fabex uses a system called Github Actions to automatically perform a series of tasks:

- Building and Testing the latest code changes
- Creating New Releases with updated version numbers
- Building a Documentation website based on docstrings in the code
- Formatting code submissions with the Black formatter

In the root folder of the repository, there is a folder called `.github`, and inside that is a folder called `workflows`.

This folder contains a series of `.yaml` or `.yml` (either will work) files that describe what will trigger the workflow to start (e.g.: push, pull request etc), and which workflow file to run (e.g.: `build_and_test.yaml`)

## Build and Test

`build_and_test.yaml` allows you to specify which version of Blender to build and test against, along with various other options.

It will be triggered by a push or pull request and it will then:

- checkout the repository and create the addon file
- either download a new version of Blender, or restore the version downloaded from the previous workflow run
- install the addon and run the Test Suite
- upload the addon file that it created along with a log of the test results

## Create New Release

`create_release.yaml` allows you to specify the addon version that you want to create.

The maintainer can decide whether the changes constitute a MAJOR, MINOR or PATCH release (e.g.: `v1.5.12`):

- MAJOR - usually means many breaking changes - the **`1`** in `1.5.12`
- MINOR - a new feature, or changes that won't break compatibility with previous version - the **`.5`** in `1.5.12`
- PATCH - a typo, or bugfix - the **`.12`** in `1.5.12`

## Black Formatter

`black.yml` will format code submissions on pull request using the [Black Formatter](https://black.readthedocs.io/en/stable/index.html) with the configuration found in the `pyproject.toml` file.

Other than extending the line length to 100 characters, the default Black config is unchanged.

## Docs Pages

`docs_pages.yml` will build a complete documentation website based on the files in the `docs` folder by first building documentation from docstring comments in the code, then building a Github Pages site using the generated docs and any other files you wish to include.

Using the Sphinx/Google docstring format allows this action to create a searchable reference, just like the [**Blender**](https://docs.blender.org/api/current/index.html) or [**Shapely**](https://shapely.readthedocs.io/en/stable/index.html) API docs.

This also helps ensure that any changes made to the code are also made to the documentation, to avoid situations where a programmer has renamed a function or Class in the code, but forgotten to update the docs.

In order for this system to work, docstrings have to follow a specific format: [Google Style Python Docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)

Docs can be written in [**Markdown**](https://www.markdownguide.org/) thanks to [MyST Parser](https://myst-parser.readthedocs.io/en/latest/), or the original [reStructured Text](https://docutils.sourceforge.io/rst.html).

```{note}
Although the addon uses Sphinx to build the docs, it was decided that Google-style strings would be used in the code for readability, that would then be converted automatically to Sphinx format using the Napoleon extension.
```