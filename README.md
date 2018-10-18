# WhatsApp Business API Setup Debugger

User Guide: https://developers.facebook.com/docs/whatsapp/guides/wadebug

WADebug is a command-line tool to help find any potential issues with WhatsApp
Business API setup, and to make requesting for help from WhatsApp support more effective.

To run, simply type `wadebug` on command-ine and check the diagnostic.
It will guide on some problems and provide guidance if you need additional
support.

# Usage

To execute all actions:
    `$ wadebug`

To execute one specific action
    `$ wadebug partial check_network`

# Installation

## For users:
`$ pip3 install wadebug`

## For developers:

This tool uses `tox` to test both Python 2.7 and 3.6. `tox` will create
virtual environments to run tests for both. Install tox on your system's Python.
All other dependencies with go into virtualenvs.

1. Install tox on your system using pip `pip install tox`, you may need to run the command in `sudo`
2. After installing tox, run `tox` in the root directory. Tests should run and pass.
3. Run `source .tox/py3/bin/activate` to enable one of the virtualenvs. Dependencies will be installed automatically.
4. Run `pip install --editable .` to enable `wadebug` in all directories that would reflect your changes.


# Testing

To execute all unit tests, from project's root folder directory run:
```
$ tox
```
Warning: do NOT run `tox` from a virtualenv as it will fail.

`tox` will run tests in Python 2 and 3.

To run tests in Python 3 for faster feedback, run either `$ pytest` from within the virtualenv or `$ tox -epy3` out of it.

To run tests in a particular module:
    ```source .tox/py3/bin/activate # to enable virtualenv on Bash
    $ pytest wadebug/wa_actions/tests/test_check_webapp_port.py -v```

(`-v` turns on verbose mode, which shows every test case in the module)


# Dependencies

* This tool uses https://docker-py.readthedocs.io for interacting with Docker
* It uses `click` to build the command-line interface

More details can be found at `setup.py` file.

# Architecture
The module `wa_actions.implementations` is the heart of the tool. Each action
is a Python class with one static method called `_run`. This method describes the
action to perform.

The idea is that a developer can implement a new `action` to investigate a
potential problem with the deployment without knowing anything about `wadebug` architecture.

Three sample actions can be seem on `wadebug/wa_actions/implementations/dummy_action.py` to understand how they are created.
On `wadebug/wa_actions/implementations/check_webapp_port.py` the implementation of a real action can be found.

## License

WADebug is [MIT licensed](./LICENSE).
