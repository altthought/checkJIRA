## checkjira 0.3 
###### Author: Alex Culp

### Purpose
Returns the overlap of:

   - HG tickets assigned to you
   - HG tickets on QE environment

### Installation

```
# install python 3.6+
brew install python3

# install dependencies
python3 -m pip install -r requirements.txt
```

### Use

```
# display testable tickets
python3 check_tickets.py
```

### Extras

- `[--debug, -d]` flag
   - prints all assigned JIRA tickets and all QE Jenkins tickets
- `[--write <filename>, -w <filename>]` flag
   - writes output cleanly to external HTML file with hyperlinks
   - ignored when combined with `--debug` flag

### Limitations

- ticket information must be included in commits
   - `git commit -m 'HG-xxxx <commit description>'`
