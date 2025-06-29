# bit-to-bit-goit-pythonweb-hw-08
Python FastAPI

# Run Docker container
docker run --name contacts-postgres -p 5432:5432 -e POSTGRES_PASSWORD=password -d postgres

# Run migrations
alembic revision --autogenerate -m 'Init'
alembic upgrade head

# Run poetry env
poetry shell

# Run app
poetry run main.py

