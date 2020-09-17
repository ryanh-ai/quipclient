Quip Automation API
===================

This is a fork from the official repository for the [Quip Automation API](https://quip.com/api/).

The purpose of this fork is to add the Quip Automation API (just the Python lib) to PiPy so it can be pip installed. (per this request: https://github.com/quip/quip-api/issues/38).

The PyPi pip package name will be `quipclient`. e.g. `pip install quipclient` 


Usage of this lib changes slighly from what is shown in the sample applications.

e.g.
```
client = quip.QuipClient(access_token="...")
```

would now be:
```
client = quipclient.QuipClient(access_token="...")
```

The code has to be reorganized for python packaging but no other code changes have been made.
(Again this package only provides the python code, The nodejs code has been removed)

Changes to the core lib will have be manually merged into this repo. Anyone is welcome to submit a pull request for that. 


Thanks
