FROM python:3-alpine AS base

RUN apk update && apk add --no-cache build-base postgresql-dev postgresql-libs tzdata

RUN adduser -S bsadmin

ADD requirements /bsadmin/requirements

WORKDIR /bsadmin

RUN pip config set global.index-url "https://pypi.python.org/simple"
RUN pip install dumb-init==1.2.2
RUN pip install -r requirements/requirements.txt

FROM base as app
ADD . /app

FROM app AS release

ENV PYTHONUNBUFFERED=1 PYTHONHASHSEED=random PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

EXPOSE 8000

FROM release AS dev-base
RUN apk add --no-cache bash

FROM dev-base as test-base
RUN pip install -r requirements/test-requirements.txt --no-deps

FROM test-base As local
USER bsadmin
CMD  ["django-admin", "runserver", "0.0.0.0:8000"]

FROM release As production
USER bsadmin
ENTRYPOINT ["/usr/local/bin/dumb-init", "--"]
CMD ["sh", "-c", "gunicorn -b 0.0.0.0:8000 bsadmin.wsgi"]
