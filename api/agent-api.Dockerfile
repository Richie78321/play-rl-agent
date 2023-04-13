FROM python:3.11-slim-buster AS base

FROM base AS deps
WORKDIR /app
COPY ./requirements.txt /app
COPY ./tictactoe/ /app/tictactoe/
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt && \
    /opt/venv/bin/pip install --no-cache-dir gunicorn

FROM base AS runner
WORKDIR /app
COPY . /app
COPY --from=deps /opt/venv /opt/venv

# Add the virtual environment to the system PATH
ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 80

CMD ["gunicorn", "-b", "0.0.0.0:80", "--chdir", "agent-api", "app:app"]