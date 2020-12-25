# FE Arena (backend)

A project attempting to re-implement, and grow beyond, the Fire Emblem GBA Link Arena.

TODO add a more formal description of the API, for the benefit of frontend.

For the time being, the `feaapi/urls.py`, the docstrings for the method they
refer to, and the two schema files 
(`feaapi/api/teambuilder/schemas.py` and `feaapi/api/arena/schemas.py`) should
be sufficient for anyone trying to build around this API.

This is not anywhere near a complete project. Be warned.

#### Build Instructions

Requires Python 3 (built in 3.8, but previous versions may work)

1. Clone this repository, and navigate to the top level on a command line
2. In the `FEArena` folder inside the repository, add a file named 
  `secret_data.json`, containing the key `SECRET_KEY`, which should be
  a long alphanumeric string.
3. `python manage.py makemigrations` to set the database schema
4. `python manage.py migrate` to *apply* the database schema to the database
5. `python manage.py loaddata fixtures/fe7/*.json` to load base data FE7 (the
  only game with data implemented as yet)
  
Currently the app uses Django's default SQLite3 database configuration. If one
is not present in the directory, it should create one automatically. I will
probably change this eventually.

#### Run Instructions

`python manage.py runserver` to run on port 8000 (or add `0.0.0.0:{port}` as
  an additional argument to run on the port of your choice)
  
## TODO list

In no particular order

- A front-end to complement this backend
    - should duplicate most of the functionality/calcs, and rely on the backend to
      validate
- Adding unit/class/etc. data for FE6 and FE8
    - and the corresponding skill implementations as necessary
- Adding EXP mechanics for Fates
- Adding support mechanics for other games
- Adding more teambuilder functionality
    - Item/boost usage restricted to what's actually obtainable ingame
    - maybe a point-buy system, for balance
- Adding a 'Skirmish' mode, in addition to the current 'Arena' mode,
  which will function similarly to the FEDS / FE14 wi-fi battles
- A chat feature
- Individualized challenges based on active users
- Miscellaneous bugfixes, including fixing EXP formulas

If you come up with anything else you'd like to see, or find any problems with
currently-implemented functionality that you don't wish to fix yourself in a
pull request, please feel free to leave a GitHub issue.

### Contributing

Feel free to submit pull requests (with full, extensive documentation of both what
you're trying to do and why). For more information, feel free to contact the primary
maintainer on reddit (/u/GreenCloakGuy) or Discord (Superbird#2755)
