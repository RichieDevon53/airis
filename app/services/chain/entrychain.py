from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableMap, RunnablePassthrough

class EntryOutput(BaseModel):
    is_question: bool = Field(..., description="Indicates if the user input contains a question or query that requires an answer")
    is_instruction: bool = Field(..., description="Indicates if the user input contains a command, request or instruction to perform an action")
    # is_including_screen: bool = Field(..., description="Indicates if the user input is asking for something related to their screen")

class EntryChain:
    def __init__(self, llm):
        self.llm = llm
        self.chain = RunnableMap({
            "option": self.llm.with_structured_output(EntryOutput).with_config(run_name="GenerateEntryChain"),
            "input": RunnablePassthrough()
        })
        
        
if __name__ == "__main__":
    from app.services.GenAIService import gen_ai
    llm = gen_ai.gemini()
    entry_chain = EntryChain(llm)
    print(entry_chain.chain.invoke("buka halaman email saya"))
        
