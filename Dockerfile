FROM python:3.10.4 as base

# Based on https://sourcery.ai/blog/python-docker/
FROM base AS python-deps
ARG GIT_SHA=local

# Install pipenv
RUN pip install pipenv

# Install Dependencies
RUN echo "GIT_SHA=${GIT_SHA}"

COPY Pipfile .
COPY Pipfile.lock .
ENV PIPENV_VENV_IN_PROJECT=1
RUN if [ "$GIT_SHA" = "local" ]; then pipenv install --dev; else pipenv install --deploy; fi

FROM base AS runtime

# Install application into container
RUN mkdir /app
WORKDIR /app
COPY ./src .

# Copy virtual env from python-deps stage
COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

# Create and switch to a new user
RUN useradd --create-home appuser
USER appuser

# Flask config
ENV PORT=5000
EXPOSE $PORT

#Sentry GITSHA
ENV GIT_SHA=$GIT_SHA

CMD ["flask", "run", "--host=0.0.0.0"]