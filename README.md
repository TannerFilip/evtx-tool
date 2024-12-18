# evtx-tool

`evtx-tool` is a Python utility designed to manage, rename, list, and archive Windows Event Log (EVTX) files. It supports operations such as renaming EVTX files based on their event type and host name, listing EVTX files within a directory, and archiving them into a compressed tarball.

## Features

- **Rename EVTX files**: Renames event log files to a standardized format (`HOSTNAME-LOGTYPE.evtx`).
- **List EVTX files**: Lists all the EVTX files in a specified directory.
- **Archive EVTX files**: Archives all found EVTX files into a compressed tarball.

## Requirements

* Homebrew package: `magic` 
* `evtx`: https://pypi.org/project/evtx/
* `python-magic`: https://pypi.org/project/python-magic/
* `pathvalidate`: https://pypi.org/project/pathvalidate/

To install:

`brew install libmagic`

`pip install -r requirements.txt`