# Steve - Community Engagement Chatbot

## Introduction

This chat bot was made as part of the GABV Hackathon 2018 held by Vancity in Telus Gardens on 16th and 17th February, 2018

The idea behind the bot is to help foster community engagement via a friendly textual assistant. In this digital age we seem to be bombarded with information. The bot takes care of aggregating and sorting through the data to help you connect well with others.

Can't find a play date for your kids? Talk to Steve, your neighborhood bot. <br>
Don't know where to go party this weekend? Talk to Steve, your neighborhood bot. <br>
Want to meet new people over Brunch? Talk to Steve, your neighborhood bot. <br>

## Technologies Used

Language: Python <br>
Libraries: Flask, pymessenger.bot, NLTK Wordnet, spaCy POS-tagger

The chat bot's primary interface for communication is a Facebook Page where it interacts with users through a chat window.

## Logic

The system uses a rule-based mechanism to detect the intent of the user. This can be found in the steve.py file. <br>
The system communicates with the messenger API through the steve_REST.py where it also tries to determine the closest matching similar actions of other users.

The iPython Notebook is there for you to see how I went about creating Steve and for you to experiment yourself. :)