import os
import yaml
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


###########################################################################
##                           CONSTANTS
###########################################################################

SRC = Path(__file__).parent
PII_COLUMNS = {"first_name", "last_name", "email", "street_address"}
MAX_RETRIES = 3


###########################################################################
##                       LLM SINGLETON INIT
###########################################################################

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY_PAID"),
)


###########################################################################
##                           FUNCTIONS
###########################################################################

def load_persona() -> dict:
    with open(SRC / "persona" / "persona.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_db_schema() -> str:
    with open(SRC / "database" / "db_schema.md", "r", encoding="utf-8") as f:
        return f.read()


