# Test Suite

The Test Suite is an automated testing tool that helps ensure that the addon functionality is not impacted by future code contributions.

The `tests` folder contains a `TESTING_PROCEDURE` file that describes how to run the Test Suite locally, or add your own tests to it.

It runs a series of pre-defined operations, outputs gcode files that can be compared against reference gcode files to ensure that the results are the same.

Most users will not need to run, access or change any part of the Test Suite, but developers may find it a very handy tool to have. 

With an addon as large and varied as Fabex, it can be easy to accidentally break something that seems unrelated to what you are working on, and the Test Suite will help to point those issues out.

*(see the [Workflows](workflows.md) page for more details)*
