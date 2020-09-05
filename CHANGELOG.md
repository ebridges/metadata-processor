## v1.1.3 (2020-09-05)

### Fix

- update tests by relocation of monitoring initialization

## v1.1.2 (2020-09-05)

### Fix

- sentry init must be outside handler.  https://bit.ly/3lSBZtL

## v1.1.1 (2020-09-04)

### Fix

- switch to binary dist of pycopg to ensure libpq ends up in lambda bundle. update some other deps as well.

## v1.1.0 (2020-09-04)

### Fix

- improve coverage on a couple of edge cases

### Refactor

- dont assert on results of debug logging
- remove two unused "read" functions, and organize functions better.
- list out inequal fields for easier debugging
- move tag names to variables

### Feat

- convert logic for reading metadata to be compatible with pillow

## v1.0.0 (2020-08-29)

### Feat

- ci/cd to generate a deployable lambda bundle
- add additional lambda for handling s3 events.
- expose functionality as a lambda
- implement logic around writing metadata to db
- add command for deleting metadata, but CLI args not correct yet
- Add cli for printing metadata out in different formats to different locations.

### Refactor

- safely get into a leaf of the dictionary
- separate out APIG interaction logic into separate module.
- split out common lambda functionality to common module.
- update sql to handle differences in placeholders between sqlite and pg
- add logging, allow writer to manage context
- adjust metadata field names to agree with target schema in elektrum
- introduce logic for inserting vs updating metadata
- dispense with unneeded tests
- change from "text" to "txt" for brevity
- decouple connection factory from writer
- stick with static initializer to avoid conflicts between constructors
- alter cli to accommodate db interaction, and to include logging
- rename to convention
- shorten var names to make formatting cleaner
- docstring formatting

### Fix

- debugging when using coverage broke breakpoints
- fixes for broken tests
- bring coverage to 93%
- 3.7 does not have the `as_integer_ratio` convenience function.
- ensure that cwd is included in pythonpath, so that application code is visible from tests.
