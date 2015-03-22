=======
knowhow
=======

.. image:: https://travis-ci.org/eukaryote/knowhow.svg?branch=master
    :target: https://travis-ci.org/eukaryote/knowhow


`knowhow` is a searchable and scriptable knowledge repository for useful
snippets of information that are worth saving for future reference. It consists
of a library for programmatic use, and a commandline script for interactive
use.


Overview
--------

The initial motivation for `knowhow` is to have a way of accessing occasionally
needed reference information from a shell, text editor, or IDE without having
to search the web and try to find again that one resource that gave the
perfect information that you can almost but not quite remember. Instead, you
save what you would to be searchable using a command like::

    » knowhow add --tag 'bash,zsh' '${FOO%bar} evaluates to $FOO with bar stripped from end'


And you can later search for that using a command like::

    » knowhow search bash
    [bash,zsh]: ${FOO%bar} evaluates to $FOO with bar stripped from end

The default search finds snippets that have the text string as a tag or in the
body of the snippet, but you can search only by tag and do more complex
boolean searches too (e.g., 'bash AND zsh' or 'shell AND NOT bash' if you
tagged all shell snippets with 'shell' and only the bash-specific ones with
'bash' also).


Supported Python Versions and Operating Systems
-----------------------------------------------

`knowhow` should work on any operating system and any Python version that
is 2.7 or greater.
