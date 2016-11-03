# djangofantalega

A fantalega handler written in django

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Install virtualenv and git for your OS.
create a virtual environment

```
virtualenv venv
```

clone the repo with git:

```
git clone https://github.com/bancaldo/djangofantalega djangosite
```

activate the virtualenvironment
# linux:
```
source ven\bin\activate
```
# windows:
```
ven\Scripts\activate
```

### Installing

Install the given requirements (django, django-bootstrap3, xlrd)
```
cd djangosite
pip install -r requirements.txt
```

### Quick start

create the database with command:
```
python manage.py migrate
```
create a superuser to handle the admin:
```
python manage.py createsuperuser
```
create the first migration with our fantalega models and update the database
```
python manage.py makemigrations fantalega
python manage.py migrate
```

## Running test

Some tests for fantalega app are written in fantalega/tests.py
To run test the command is:
```
python manage.py test
```

## Running the server
To run the development server, the command is:
```
python manage.py runserver
```

## Login

go to the [Fantalega home page](http://127.0.0.1:8000/fantalega)
now you can login and go to admin page where you can create a new Season

# Create a new Season
In the Admin page click on Season and create a new one with name in format 'yyyy-yyyy'.
(e.i. 2016-2017)

# Create a new League
In the Admin page click on League and create a new one.
the parameters are:
- name
- budget
- max trades
- rounds
- offset
...

Chose the related season.

# Create the Teams 
In the Admin page click on Team and create the teams.
Choose the league associated and the user who admins the team


When all the teams are created it can starts the auction and
you can create the calendar.

# to do the rest of tutorial.....

## Versioning

I use [Git](https://git-scm.com/) for versioning.

## Author

* **Bancaldo** - *Initial work* - [bancaldo](https://github.com/bancaldo)

## Licenses

Copyright (c) 2016 Bancaldo's Djangofantalega.
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice,
       this list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.

    3. Neither the name of Django nor the names of its contributors may be used
       to endorse or promote products derived from this software without
       specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.