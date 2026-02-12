import os
from dotenv import load_dotenv

# variables
load_dotenv()
"postgresql://user:password@localhost:5432/mydb"
db_user=os.getenv("db_user_env")
db_password=os.getenv("db_password_env")
db_host=os.getenv("db_host_env")
db_port=os.getenv("db_port_env")
db_name=os.getenv("db_name_env")
db_url=f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"