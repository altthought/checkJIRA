## checkJIRA 
###### Author: Alex Culp

## Purpose

QE finds a bug and reports it as `JA-1234` and assigns it to a developer.

A developer working on a new bugfix, `JA-1234`, will create his initial commit like so: 

`git commit -m 'JA-1234: disallow embedded full-screen rickrolls'`

When they're eventually done, and push their fix up, they'll reassign the ticket to QE
for testing. 

However, for projects with multiple-hour long builds, it would be handy for QE to know whether the fix was already pulled
onto a test environment in a previous build, to avoid having to rebuild on strained test hardware.

Or more simply:

This tool returns the overlap of:
   - Jenkins changelogs which contain ticket numbers in commit messages
   - JIRA tickets which match some custom JQL query (i.e. `"project=JA AND assignee=me AND status=Resolved"`)

All JIRA/Jenkins configuration is handled by the `config.json` file.

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

- the ticket must be mentioned in a commit on that feature/bugfix branch
   - i.e. dev performs `git commit -m 'JA-#### <commit description>'`
   - _Note: only needs to be mentioned in a single commit_
