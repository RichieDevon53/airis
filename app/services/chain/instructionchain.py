from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_react_agent, AgentExecutor
from app.utils.prepareimage import prepare_images
from app.services.AutoGui import ToolBox

SYSTEM_PROMPT="""
You are helpfull assistant, receiving instruction request from the user.
You will be navigating though user windows explorer and complete the task
Plan you execution action to acheive instrucion request using available tools
{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}
"""

class InstructionChain:
    def __init__(self, llm):
        self.llm = llm

    def __call__(self, input: str):
        # agent = create_react_agent(
        #     llm=self.llm, 
        #     tools=ToolBox, 
        #     prompt=InstructionChain.get_prompt()
        # )
        # agent_executor = AgentExecutor(agent=agent, tools=ToolBox)
        # res = agent_executor.invoke({"input": input})
        # print(res)
        # return res
        KeyboardHotkey({"hotkey_keys": "win+r"})
        KeyboardWriteText({"text_string": "chrome"})
        KeyboardPressKey({"key": "enter"})

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
                        prepare_images()
                    ]
                ),
            ]
        )
