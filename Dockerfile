FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install uv && uv sync --frozen --no-dev

COPY . .

ENV PYTHONPATH=/app
ENV DEBUG=False

CMD ["uv", "run", "python", "main.py", "-n", "3"]
