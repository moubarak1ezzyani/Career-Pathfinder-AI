import os
from dotenv import load_dotenv

# variables
load_dotenv()
"postgresql://user:password@localhost:5432/mydb"
DB_USER=os.getenv("DB_USER_env")
DB_PASSWORD=os.getenv("DB_PASSWORD_env")
DB_HOST=os.getenv("DB_HOST_env")
DB_PORT=os.getenv("DB_PORT_env")
DB_NAME=os.getenv("DB_NAME_env")
DB_URL=f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
