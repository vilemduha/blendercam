Workflows & Actions
===================
Fabex uses a system called Github Actions to automatically perform a series of tasks:
- Building and Testing the latest code changes
- Creating New Releases with updated version numbers
- Building a Documentation website based on docstrings in the code
- Formatting code submissions with the Black formatter

In the root folder of the repository, there is a folder called `.github`, and inside that is a folder called `workflows`.

This folder contains a series of `.yaml` or `.yml` files that describe what will trigger the workflow to start (e.g.: push, pull request etc), and which workflow file to run (e.g.: `build_and_test.yaml`)

Build and Test
==============
`build_and_test.yaml` allows you to specify which version of Blender to build and test against, along with various other options.

It will be triggered by a push or pull request and it will then:
- checkout the repository and create the addon file
- either download a new version of Blender, or restore the version downloaded from the previous workflow run
- install the addon and run the Test Suite
- upload the addon file that it created along with a log of the test results

Create New Release
==================
`create_release.yaml` allows you to specify the addon version that you want to create.

The maintainer can decide whether the changes constitute a MAJOR, MINOR or PATCH release:
- MAJOR - usually means many breaking changes
- MINOR - a new feature, or changes that won't break compatibility with previous version
- PATCH - a typo, or bugfix

With MAJOR, MINOR and PATCH corresponding with the version numbers 1.5.12:
- MAJOR - 1
- MINOR - .5
- PATCH - .12

Docs Pages
==========
`docs_pages.yml` will build a complete documentation website based on the files in the `docs` folder.

Using the sphinx/Google docstring format allow this action to pull comments out of the code, and format them the same way as the Blender or Shapely docs.
This helps ensure that any changes made to the code are also made to the documentation, which helps avoid situations where a programmer has renamed a function or Class in the code, but forgotten to update the docs.

In order for this system to work, docstrings have to follow a specific format: `Google Style Python Docstrings <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html>`

NOTE:

Although the addon uses Sphinx to build the docs, it was decided that Google-style strings would be used in the code for readability, that would then be converted automatically to Sphinx format using the Napoleon extension.
