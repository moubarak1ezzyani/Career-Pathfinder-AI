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


# --- security 
SECRET_KEY=os.getenv("SECRET_KEY_env")
ALGO=os.getenv("ALGO_env")
TOKEN_EXPIRE=os.getenv("TOKEN_EXPIRE_env")

# paths
cv_me_standard=os.getenv("cv_me_standard_env")
