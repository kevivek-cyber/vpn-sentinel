FROM python:3.9-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

RUN useradd -m -u 1000 user
USER user

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

COPY --chown=user . $HOME/app

# Hugging Face Spaces expects 7860; Render (and most PaaS) inject their own $PORT
# and will fail health checks with "No open ports detected" if it's ignored.
# Shell form so $PORT is expanded at runtime, defaulting to 7860 when unset.
CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-7860}
