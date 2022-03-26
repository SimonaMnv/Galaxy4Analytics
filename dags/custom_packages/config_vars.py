import os

config = {
    "ENV": "dev",
    "project_root": os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "database_url": os.environ.get("DATABASE_URL")
}
