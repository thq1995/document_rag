
import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

load_dotenv()

class GlobalSettings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    CORS_ORIGINS = os.getenv("FASTAPI_ORIGINS", "*")
    CORS_METHODS = os.getenv("FASTAPI_METHODS", "*")
    CORS_HEADERS = os.getenv("FASTAPI_HEADERS", "*")
    CORS_CREDENTIALS = True
    MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "text-davinci-003")
    NUM_WORKERS = int(os.getenv("FASTAPI_WORKER", 1))
    
    
class Model:
    openai = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.0,
            model_name="gpt-3.5-turbo",
            streaming=True,  # ! important
            callbacks=[StreamingStdOutCallbackHandler()]
    )
        