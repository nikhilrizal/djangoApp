FROM python:3.10 as build-env

ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app

# Add Pipfiles to image and install them
COPY . /app

# Install Pipenv and run
RUN pip install pipenv --no-cache-dir
RUN pipenv install --system --deploy --ignore-pipfile

# Add Django entrypoint script to docker
COPY ./scripts/entrypoint.sh /entrypoint.sh
RUN chmod u+x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]



