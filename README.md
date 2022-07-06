## Code Time Tracker
A Telegram bot, that gathers data from wakatime API and calculates total time spent on coding

### Expected behavior
* User starts a conversation with bot - sends him an API key
* Bot checks key with simple request to wakatime
* If everything is good - stores key in db encrypted via hash
* Every week bot sends a message with analytics how user performed last week, last month and all time
* Every user should have a separated table in db in order to make it possible to many users to use it
* Expected tech stack - aiogram, SQLAlchemy
* Hosting

### I18n

#### Install (if deleted)
```
pybabel extract --input-dirs=. -o ./locales/time_tracker.pot
pybabel init -i locales/time_tracker.pot -d locales -D time_tracker -l en
pybabel init -i locales/time_tracker.pot -d locales -D time_tracker -l ru
```
Translate everything in .po files
```
pybabel compile -d locales -D time_tracker
```
#### Update translations and keys
```
pybabel extract --input-dirs=. -o ./locales/time_tracker.pot
pybabel update -d locales -D time_tracker -i locales/time_tracker.pot
```
Translate everything in .po files
```
pybabel compile -d locales -D time_tracker
```

### TODO notes
[helps with OAauth 2.0](https://rauth.readthedocs.io/en/latest/)

Make a scheduled task!

### Work in progress notes

