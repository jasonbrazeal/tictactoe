FROM python:3-alpine

ARG HOST

# Validate --build-arg HOST=<HOST> was passed
RUN : "${HOST:?Build argument HOST needs to be set and non-empty.}"

WORKDIR /app

COPY ./Pipfile /app
COPY ./Pipfile.lock /app

RUN pip install pipenv
RUN pipenv install --system --deploy

COPY ./ /app

EXPOSE 5000

CMD ["pipenv", "run", "gunicorn", "-w", "4", "tictactoe.wsgi:application", "-b", "0.0.0.0:5000", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "DEBUG"]

