# Local setup

```
$ virtualenv -p python3 env
$ . ./env/bin/activate
(env) $ pip install -r requirements.txt
(env) $ flask db init
(env) $ flask db migrate -m "init"
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
