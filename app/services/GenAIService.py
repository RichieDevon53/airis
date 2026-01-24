from config.setting import env
from langchain_google_genai import ChatGoogleGenerativeAI
from config.credentials import google_credential
class GenAiService:

    def gemini(self, model: str):
        return ChatGoogleGenerativeAI(
            model=model, 
            temperature=0, 
            project=env.GOOGLE_PROJECT_NAME, 
            location=env.GOOGLE_LOCATION_NAME,
            credentials=google_credential(),
            thinking_budget=0,
        )

gen_ai = GenAiService()
