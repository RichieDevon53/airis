from config.setting import env
from langchain_google_genai import ChatGoogleGenerativeAI

class GenAiService:

    def gemini(self, model: str = env.gemini_model):
        import os
        os.environ["GOOGLE_API_KEY"] = "AIzaSyBZxAarV2rqR_934ekw-YkOICxDCA5-fTc"
        return ChatGoogleGenerativeAI(model=model)
    
gen_ai = GenAiService()
