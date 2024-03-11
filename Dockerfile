# https://fastapi.tiangolo.com/deployment/docker/
FROM python:3.12
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
COPY ./requirements_dev.txt /code/requirements_dev.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt -r /code/requirements_dev.txt
CMD ["/bin/bash"]