```
$ make build
$ make shell
$ uvicorn app.main:app --host 0.0.0.0 --port 80 --reload
```
Use `isort . && black .` command for code formatting.

## Upload image to server and run it
on dev:
1. `make build_prod`
2. `docker save conv_prod | ssh -C user@example.com docker load`

on prod:
1. `docker create --name conv_prod -p 8080:80 -it conv_prod`
2. Stop running container with `docker stop conv_prod && docker rm conv_prod`. Then start a new one with `docker start conv_prod`
3. Check runing image with `docker ps -a` and logs with `docker logs conv_prod`