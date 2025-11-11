from app.services.GenAIService import gen_ai
from app.services.chain.entrychain import EntryChain
from app.services.chain.questionchain import QuestionChain
# from app.services.chain.instructionchain import InstructionChain
# from app.services.chain.instructionchainV2 import EnhancedInstructionChain
# from app.services.chain.instructionchainV3 import EnhancedInstructionChain
from app.services.chain.instructionchainV4 import EnhancedInstructionChain
from app.services.chain.boardchain import BoardChain
from app.utils.screenshot import screenshot
from config.setting import env
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough

class maincontroller:
    def __init__(self, gen_ai):
        self.gen_ai = gen_ai
        self.llm = self.gen_ai.gemini()
        self.entry_chain = EntryChain(self.llm)
        self.question_chain = QuestionChain(self.llm)
        self.instruction_chain = EnhancedInstructionChain(self.llm)
        self.board_chain = BoardChain(
            primary_llm=self.gen_ai.gemini(model=env.gemini_pro_model),
            secondary_llm=self.gen_ai.claude(max_tokens=4096)
            )
        # self.board_chain = BoardChain(self.gen_ai.pixtral())
        # self.board_chain = BoardChain(self.gen_ai.mini4o(max_tokens=16000))
        # self.board_chain = BoardChain(self.llm)
        
    def __call__(self, input: str):
        main_chain = (self.entry_chain.chain 
        | {
            "output" : {
                "question": RunnableLambda(lambda x: self.question_chain(x["input"]) if x["option"].is_question else None),
                "instruction": RunnableLambda(lambda x: self.instruction_chain(x["input"]) if x["option"].is_instruction else None)
                },
            "original": RunnablePassthrough()
            }
        )
        return main_chain.invoke(input)
    
    def glass_board(self, input: str):
        return self.board_chain(input)
    
    def glass_board_dev(self, input: str):
        return self.board_chain.custom_call(input)
    
    

controller = maincontroller(gen_ai)
        
if __name__ == "__main__":
    # print(controller.glass_board("Explain to me where the dr House ?"))
    # print(controller.glass_board_dev("Explain to me where the dice located ?"))
    print(controller("switch tab to my vivaldi and open my gmail"))
