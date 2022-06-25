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
