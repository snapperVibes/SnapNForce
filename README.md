# SnapNForce
## Server Setup
### Prerequisites:
  - Python 3.10 or higher.
  - pip

### Clone the repository
```console
foo@bar:~$ git clone https://github.com/SnapperVibes/SnapNForce.git
```

### Install Poetry
SnapNForce manages dependencies and virtual environments using [Poetry](https://github.com/python-poetry/poetry).
You can install Poetry using pip.
```console
foo@bar:~$ pip install poetry
foo@bar:~$ poetry --version
Poetry version 1.1.13
```
##### Optional: Change default location of virtual environments
By default, Poetry stores created virtual environments in a hidden folder.
My personal preference is to have the environment created within the current directory.
This way deleting environments is as easy as deleting the .venv folder.
You can [tell Poetry to create the virtual environments in the project](https://python-poetry.org/docs/configuration/#virtualenvsin-project) using
```console
foo@bar:~$ poetry config virtualenvs.in-project true
```
### Create the virtual environment and install dependencies
```console
foo@bar:~$ cd SnapNForce
foo@bar:~/SnapNForce$ poetry install
```
You should notice that a directory named ".venv" was created.
### Activate the virtual environment
```console
foo@bar:~/SnapNForce$ poetry shell
(.venv) foo@bar:~/SnapNForce$
```
You'll know you are in the virtual environment when the console's prompt is prefixed with `(.venv)`

### Configure application login
SnapNForce uses the user `sylvia`.
Set sylvia's login details in the [.pgpass password file](https://www.postgresql.org/docs/14/libpq-pgpass.html).

### Start the server
```console
(.venv) foo@bar:~/SnapNForce$ python main.py
INFO:     Started server process [8226]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```















