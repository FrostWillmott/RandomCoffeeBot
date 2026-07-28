# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/FrostWillmott/RandomCoffeeBot/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                |    Stmts |     Miss |   Cover |   Missing |
|------------------------------------ | -------: | -------: | ------: | --------: |
| app/\_\_init\_\_.py                 |        0 |        0 |    100% |           |
| app/bot/\_\_init\_\_.py             |       27 |        0 |    100% |           |
| app/bot/handlers/\_\_init\_\_.py    |        2 |        0 |    100% |           |
| app/bot/handlers/commands.py        |       67 |        0 |    100% |           |
| app/bot/handlers/feedback.py        |      104 |        8 |     92% |40, 53, 67, 114, 123, 169-171 |
| app/bot/handlers/matches.py         |       69 |        4 |     94% |56, 65, 126, 135 |
| app/bot/handlers/reactions.py       |       71 |       17 |     76% |61-75, 100-103, 134-140 |
| app/bot/handlers/registration.py    |       10 |        4 |     60% |     14-28 |
| app/bot/handlers/start.py           |       29 |        0 |    100% |           |
| app/bot/keyboards/\_\_init\_\_.py   |        2 |        0 |    100% |           |
| app/bot/keyboards/inline.py         |        7 |        0 |    100% |           |
| app/bot/middlewares/\_\_init\_\_.py |        3 |        0 |    100% |           |
| app/bot/middlewares/database.py     |       21 |        0 |    100% |           |
| app/bot/middlewares/throttling.py   |       47 |        3 |     94% | 82-83, 97 |
| app/bot/states/\_\_init\_\_.py      |        3 |        0 |    100% |           |
| app/bot/states/feedback.py          |        4 |        0 |    100% |           |
| app/bot/states/registration.py      |        3 |        0 |    100% |           |
| app/config.py                       |       29 |        6 |     79% |     31-39 |
| app/constants.py                    |        9 |        0 |    100% |           |
| app/db/\_\_init\_\_.py              |        0 |        0 |    100% |           |
| app/db/base.py                      |        2 |        0 |    100% |           |
| app/db/session.py                   |        5 |        0 |    100% |           |
| app/main.py                         |       91 |        4 |     96% |58, 117-119 |
| app/models/\_\_init\_\_.py          |        8 |        0 |    100% |           |
| app/models/enums.py                 |       14 |        0 |    100% |           |
| app/models/feedback.py              |       19 |        0 |    100% |           |
| app/models/match.py                 |       30 |        0 |    100% |           |
| app/models/registration.py          |       16 |        0 |    100% |           |
| app/models/session.py               |       19 |        0 |    100% |           |
| app/models/topic.py                 |       21 |        0 |    100% |           |
| app/models/user.py                  |       20 |        0 |    100% |           |
| app/repositories/\_\_init\_\_.py    |        9 |        0 |    100% |           |
| app/repositories/base.py            |       27 |        2 |     93% |     44-45 |
| app/repositories/feedback.py        |       19 |        8 |     58% |30-33, 44-47, 59-67, 79-80 |
| app/repositories/match.py           |       46 |       16 |     65% |33-36, 47-57, 74, 101-104, 117-118, 129-144, 155-164, 176 |
| app/repositories/protocols.py       |       56 |        0 |    100% |           |
| app/repositories/registration.py    |       28 |        8 |     71% |55-58, 85-88, 99-114, 126-127 |
| app/repositories/session.py         |       39 |        8 |     79% |45-54, 143-146, 150-158, 165-173 |
| app/repositories/topic.py           |       17 |        2 |     88% |     46-47 |
| app/repositories/user.py            |       37 |       10 |     73% |44-47, 99-105 |
| app/resources/\_\_init\_\_.py       |        0 |        0 |    100% |           |
| app/resources/messages.py           |        9 |        0 |    100% |           |
| app/scheduler.py                    |      124 |        9 |     93% |76, 107-110, 181-186 |
| app/schemas/\_\_init\_\_.py         |        2 |        0 |    100% |           |
| app/schemas/callbacks.py            |       49 |        0 |    100% |           |
| app/services/\_\_init\_\_.py        |        4 |        0 |    100% |           |
| app/services/announcements.py       |       29 |        3 |     90% |     85-90 |
| app/services/matching.py            |      142 |       19 |     87% |60-61, 140, 173-177, 216, 250-251, 278-281, 309-312 |
| app/services/notifications.py       |      128 |       27 |     79% |66-67, 90-100, 135-147, 196, 225, 240-251 |
| app/services/sessions.py            |       28 |        5 |     82% | 28, 38-41 |
| app/utils/\_\_init\_\_.py           |        2 |        0 |    100% |           |
| app/utils/logging.py                |       13 |        0 |    100% |           |
| app/utils/retry.py                  |       38 |        2 |     95% |   105-109 |
| app/utils/user\_formatting.py       |       14 |        1 |     93% |        28 |
| **TOTAL**                           | **1612** |  **166** | **90%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/FrostWillmott/RandomCoffeeBot/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/FrostWillmott/RandomCoffeeBot/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/FrostWillmott/RandomCoffeeBot/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/FrostWillmott/RandomCoffeeBot/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2FFrostWillmott%2FRandomCoffeeBot%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/FrostWillmott/RandomCoffeeBot/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.