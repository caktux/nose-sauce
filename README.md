nose-sauce
==========
Creates a sauce.log file with the test's name, session ID and result on a single line, split by `|`

#### Installation ####
Add this to your tests
```
        # Add Sauce sessionId for nose-sauce
        self.sessionId = self.driver.session_id
```

#### Usage ####
```
nosetests --with-sauce
```
