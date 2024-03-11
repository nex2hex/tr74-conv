```
$ make build
$ make shell
$ uvicorn app.main:app --host 0.0.0.0 --port 80 --reload
```

use `isort . && black .` command for code formatting