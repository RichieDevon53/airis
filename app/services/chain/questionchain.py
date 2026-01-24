from app.utils.prepareimage import prepare_images
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

class QuestionOutput(BaseModel):
    short_answer: str = Field(..., description="The short answer (max 5 words) to the user's question based on the provided image, maximum of 64 character.")
    explanation: str = Field(..., description="the explanation of the short answer maximumn of 256 characters.")
    
SYSTEM_PROMPT="""
You are personal assistant, never say the first person perspective from your side
Never metion there is the image sended.
Answer directly any question based on the image sended
"""

class QuestionChain:
    def __init__(self, llm):
        self.llm = llm
        
    def __call__(self, input: str):
        self.chain = QuestionChain.get_prompt() | self.llm.with_structured_output(QuestionOutput)
        self.chain.with_config(run_name="GenerateAnswer")
        res = self.chain.invoke({"input": input})
        return res.model_dump() 

    @staticmethod
    def get_prompt():
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    SYSTEM_PROMPT,
                ),
                (
                    "user",
                    [
                        {"type": "text", "text": "{input}"},
                        prepare_images(quality=50)
                    ]
                ),
            ]
        )
