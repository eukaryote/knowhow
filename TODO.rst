To Do
-----

 - update tox/travis confs for newer python versions
 - use pylint and its pytest plugin instead of just pep8
 - update setup.py classifiers
 - vendor deps to avoid conflicts while still ensuring specific versions that have been tested (?), and perhaps change fix to use pickle2
 - add coverage info to tests
 - change 'tags' subcommand to 'tag', with '-l' for list and other options such as renaming
 - optionally include id in results (default or not?)
 - load should read line by line, assuming standard dump format, to handle large files
 - filehandles for reading should handle binary or text mode
