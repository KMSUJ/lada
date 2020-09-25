![Tests](https://github.com/KMSUJ/lada/workflows/Tests/badge.svg)

# Local setup

```
$ virtualenv -p python3 env
$ . ./env/bin/activate
(env) $ pip install -r requirements.txt
(env) $ flask db init
(env) $ flask db migrate
(env) $ flask db upgrade
(env) $ flask run
```

# Test

```
$ virtualenv -p python3 env
$ . ./env/bin/activate
(env) $ pip install -r requirements.txt
(env) $ pip install pytest
(env) $ pytest
```

# Demo

1. Enable `demo` feature flag in config.py

2. Seed fellow database using [http://localhost:5000/fellow/seeddb](http://localhost:5000/fellow/seeddb)

3. To start the election see [http://localhost:5000/dike/panel](http://localhost:5000/dike/panel)

4. You can register candidates:

  - manually on [http://localhost:5000/dike/register](http://localhost:5000/dike/register). You have to be logged in as commitee member. You will have to provide your password in the registration form.

  - automatically using [http://localhost:5000/dike/seedregister](http://localhost:5000/dike/seedregister)

5. You can start voting now on [http://localhost:5000/dike/panel](http://localhost:5000/dike/panel)

6. Ballots can be filled:

  - manually on [http://localhost:5000/dike/ballot](http://localhost:5000/dike/ballot)

  - automatically using [http://localhost:5000/dike/seedvote](http://localhost:5000/dike/seedvote)

7. Voting can be finished on [http://localhost:5000/dike/panel](http://localhost:5000/dike/panel)

8. Election can be finalized on [http://localhost:5000/dike/reckoning](http://localhost:5000/dike/reckoning)
