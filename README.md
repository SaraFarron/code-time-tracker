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

### Installation

### TODO notes
[helps with OAauth 2.0](https://rauth.readthedocs.io/en/latest/)

update db func should check if it already has new data
aiogram has markdown!

### Work in progress notes

get all time/last week data -> update db -> get info from db -> format text
