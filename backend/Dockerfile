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


# mount --bind /home/nik/Downloads/backendt /app
# /home/nik/Downloads/backend 7dfb537b20ca



# docker run -v ./:/app -p 80:80 7dfb537b20ca -e SECRET_KEY=7d925a43732b1e516370a8581446ed86f46b17453c64ba33151b0c57138f49c1
