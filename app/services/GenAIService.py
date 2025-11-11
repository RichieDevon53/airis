from config.setting import env
from config.credentials import google_credential
from langchain_google_vertexai import ChatVertexAI, HarmBlockThreshold, HarmCategory
from langchain_aws import ChatBedrock
from langchain_openai import AzureChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

import boto3

class GenAiService:
    # def gemini(self, model: str = env.gemini_model):
    #     credentials = google_credential()
    #     safety_settings = {
    #           HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_NONE,
    #           HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    #           HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    #           HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    #           HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE
    #         }
    #     llm = ChatVertexAI(
    #         model_name=model, 
    #         temperature=0, 
    #         safety_settings=safety_settings, 
    #         project=env.project_name, 
    #         location=env.location_name,
    #         credentials=credentials
    #     )
    #     return llm
    
    def gemini(self, model: str = env.gemini_model):
        import os
        os.environ["GOOGLE_API_KEY"] = "AIzaSyBZxAarV2rqR_934ekw-YkOICxDCA5-fTc"
        return ChatGoogleGenerativeAI(model=model)

    def claude(
        self,
        model: str = env.claude_sonnet_model,
        temperature: float = 0.0,
        max_tokens: int = None,
        region_name: str = env.claude_region
    ) -> ChatBedrock:
        session = boto3.Session(
            aws_access_key_id=env.aws_access_key_id,
            aws_secret_access_key=env.aws_secret_access_key,
            region_name=region_name
        )

        return ChatBedrock(
            model_id = model,
            model_kwargs=dict(
                temperature=temperature,
                max_tokens=max_tokens
                ),
            client=session.client('bedrock-runtime'),
        )
    
    def pixtral(
        self,
        model: str = env.mistral_pixtral_model,
        **kwargs
    ) -> ChatBedrock:
        return self.claude(model=model, **kwargs)
    
    def getModelBedrock(
        self,
        region_name: str = env.claude_region
    ):
        session = boto3.Session(
            aws_access_key_id=env.aws_access_key_id,
            aws_secret_access_key=env.aws_secret_access_key,
            region_name=region_name
        )

        bedrock = session.client('bedrock')
        return [model["modelId"] for model in bedrock.list_foundation_models()['modelSummaries']]

    def mini4o(
        self,
        model: str = env.gpt_4o_mini,
        max_tokens: int = None,
        api_key: str = env.azure_api_key_gpt4o_mini,
        azure_endpoint: str = env.azure_endpoint_gpt4o_mini,
        temperature: float = 0.0,
        api_version: str = env.azure_api_version,
    ) -> AzureChatOpenAI:
        return AzureChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint,
            max_tokens=max_tokens
        )
    
gen_ai = GenAiService()

if __name__ == "__main__":
    print(gen_ai.getModelBedrock())
    print(gen_ai.pixtral().invoke("hello"))
    