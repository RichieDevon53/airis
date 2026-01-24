from app.services.GenAIService import gen_ai
from app.services.chain.questionchain import QuestionChain
class maincontroller:
    def __init__(self):
        self.question_chain = QuestionChain(gen_ai.gemini(model="gemini-2.5-flash-lite"))
        
    def __call__(self, input: str):
        return self.question_chain(input)
    
    def glass_board(self, input: str):
        pass
    
    def glass_board_dev(self, input: str):
        pass
    
controller = maincontroller()
        