from config.setting import env
from langchain_google_genai import ChatGoogleGenerativeAI

class GenAiService:

    def gemini(self, model: str = env.gemini_model):
        import os
        os.environ["GOOGLE_API_KEY"] = env.google_api_key
        return ChatGoogleGenerativeAI(model=model)
    
gen_ai = GenAiService()
