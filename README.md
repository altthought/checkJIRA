## checkJIRA 
###### Author: Alex Culp

## Purpose
Returns the **overlap** of:

   - HG tickets assigned to you
   - HG tickets mentioned in Mercury QE changelog

Note, you could trivially repurpose this tool to be overlap of:
   
   - JIRA project tickets assigned to you
   - JIRA project tickets mentioned as branch names in Jenkins build changelog

## Installation

```
# we're all adults here, use python3
brew install python3

# install dependencies (really just requests)
python3 -m pip install -r requirements.txt
```

## Usage

```
# display testable tickets
python3 check_tickets.py
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

- if Jenkins server uses a self-signed SSL cert you must disable SSL checks
- the HG ticket must be mentioned in a commit on that feature/bugfix branch
   - `git commit -m 'HG-#### <commit description>'`
   - _Note: only needs to be mentioned in a single commit_
