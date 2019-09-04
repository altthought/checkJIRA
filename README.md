## checkJIRA 
###### Author: Alex Culp

## Purpose

Returns the **overlap** of:
   
   - JIRA project tickets assigned to you
   - JIRA project tickets mentioned as branch names in Jenkins build changelog

## Usage

```
# display testable tickets
python3 check_tickets.py
password: <password>

[ Checking: JIRA... ]
[ Checking: http://build.whoever.org:8080/job/MyJob/api/json... ]
[ Checking: http://build2.whoever.org:8080/job/MyJob/api/json... ]

[ Ready: ]
   https://resource.whoever.com/jira/browse/JA-1121
   https://resource.whoever.com/jira/browse/JA-2232
   https://resource.whoever.com/jira/browse/JA-5911
```

## Limitations

- if Jenkins server uses a self-signed SSL cert you must disable SSL checks
- the HG ticket must be mentioned in a commit on that feature/bugfix branch
   - `git commit -m 'JA-#### <commit description>'`
   - _Note: only needs to be mentioned in a single commit_
