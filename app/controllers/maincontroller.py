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
    def __init__(self):
        self.llm = gen_ai.gemini()
        self.entry_chain = EntryChain(self.llm)
        self.question_chain = QuestionChain(self.llm)
        self.instruction_chain = EnhancedInstructionChain(self.llm)
        self.board_chain = BoardChain(
            primary_llm=self.llm,
            secondary_llm=self.llm
            )
        # self.board_chain = BoardChain(self.gen_ai.pixtral())
        # self.board_chain = BoardChain(self.gen_ai.mini4o(max_tokens=16000))
        # self.board_chain = BoardChain(self.llm)
        
    def __call__(self, input: str):
        return self.question_chain(input)
    
    def glass_board(self, input: str):
        print("reach glass call")
        return self.board_chain(input)
    
    def glass_board_dev(self, input: str):
        return self.board_chain.custom_call(input)
    
controller = maincontroller()
        
if __name__ == "__main__":
    # print(controller.glass_board("Explain to me where the dr House ?"))
    # print(controller.glass_board_dev("Explain to me where the dice located ?"))
    print(controller("switch tab to my vivaldi and open my gmail"))
