# bsadmin

## Overview
This is the project for Banner Rotation System management. This is an admin 
interface for configuring banners to shows on the different pages of a website.
bsadmin exposes API endpoint for listing all currently active banners that can
be used by [bsendpoint](https://github.com/abramovd/bsendpoint) service to serve
HTTP requests from different pages and show the best suited banners based on 
the configuration. 

## Tech

- Python 3.7
- Django

## Build

Repo contains Dockerfile and docker-compose.yml  
There is no need for database or any other writable storage.

Dependencies are handled with `pip-tools`

### Configuration

App is using starlette config module (https://www.starlette.io/config/)  
All configuration happens via `.env` file or environment variables.

#### Supported environment variables:


### Using docker compose
```
docker-compose up
```

## Dev setup

As application has no needs for database and is only using packages from public PyPi it's very easy to setup locally for development.

### Setup virtualenv
```
cd bsadmin
python3 -m venv .venv
source .venv/bin/activate
pip install pip-tools
pip-compile requirements/test-requirements.in
```

