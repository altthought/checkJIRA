## checkJIRA 0.4.1
###### Author: Alex Culp

## Purpose
Returns the overlap of:

   - HG tickets assigned to you
   - HG tickets mentioned in Mercury QE changelog

## Installation

```bash
# install python 3.6+
brew install python3

# install dependencies
python3 -m pip install -r requirements.txt
```

## Usage

```bash
# display testable tickets
python3 check_tickets.py
username: <name>
password: <password>

[ Checking: JIRA... ]
[ Checking: http://sjbuild2.marketo.org:8080/job/MercuryFramework-QE/api/json... ]
[ Checking: http://sjbuild2.marketo.org:8080/job/MercuryServer-QE/api/json... ]

[ Ready: ]
   https://resource.marketo.com/jira/browse/HG-7231
   https://resource.marketo.com/jira/browse/HG-7225
   https://resource.marketo.com/jira/browse/HG-6631
```

## Limitations

- the HG ticket must be mentioned in a commit on that feature/bugfix branch
   - `git commit -m 'HG-xxxx <commit description>'`
   - _Note: only needs to be mentioned in a single commit_
