from langchain_core.prompts import ChatPromptTemplate
# from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_core.messages import AIMessage
from langchain_core.messages import AnyMessage
from typing_extensions import TypedDict
from typing import List, Optional, Annotated, Union, Literal
from app.services.AutoGuiV4 import ToolBox
from operator import add
from langchain_core.messages import HumanMessage
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage, AnyMessage
import json
from uuid import uuid4

SYSTEM_PROMPT = """
You are an advanced desktop automation assistant. Your goal is to accomplish tasks with maximum efficiency by planning ahead and calling multiple tools at once.

**CORE PRINCIPLE: PLAN ALL STEPS, ACT IN A SINGLE TURN**
Your default behavior is to plan a complete, predictable sequence of actions first, and then call all the necessary raw tools sequentially **in a single response**. This is far more efficient than calling one tool at a time.

**EXECUTION STRATEGY: OBSERVE, PLAN SEQUENCE, EXECUTE ALL, VERIFY**
Follow this sequence rigorously:
1.  **OBSERVE**: Use `ShowScreen` ONCE at the beginning to understand the initial state of the desktop.
2.  **PLAN THE ENTIRE SEQUENCE**: Think step-by-step and identify the full list of **raw tool calls** needed to complete the task. For example, to "open calculator and type 3+3", you need `OpenApplication` first, then `WaitAndObserve`, then `KeyboardWriteText`.
3.  **EXECUTE THE SEQUENCE**: Generate the entire list of tool calls in order in your response. The system will run them for you.
4.  **VERIFY**: AFTER the full sequence has been executed by the system, use `ShowScreen` in the *next* turn to confirm the final result.

**EXAMPLE TASK: "open my calculator and type 3 + 3"**

Your first response should be a multi-tool call like this:
```json
{{
  "tool_calls": [
    {{
      "name": "OpenApplication",
      "args": {{ "app_name": "calc" }}
    }},
    {{
      "name": "WaitAndObserve",
      "args": {{ "seconds": 2 }}
    }},
    {{
      "name": "KeyboardWriteText",
      "args": {{ "text": "3+3" }}
    }}
  ]
}}
This allows you to open the app and type the numbers all in one step, without needing to think again in between.

Begin!
"""

class GraphState(TypedDict):
    messages: Annotated[List[AnyMessage], add]

class EnhancedInstructionChain:
    def __init__(self, llm, max_iterations: int = 10):
        self.llm = llm
        self.max_iterations = max_iterations
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        # Create a dictionary to look up tools by name
        self.tool_map = {tool.name: tool for tool in ToolBox}

    def __call__(self, input_str: str):
        """
        Executes the agent loop.
        """
        # 1. Bind tools to the LLM
        llm_with_tools = self.llm.bind_tools(ToolBox)
        
        # 2. Set up the main chain
        chain = self.prompt | llm_with_tools

        # 3. Initialize the state
        messages = [HumanMessage(content=input_str)]
        
        # 4. Start the agent loop
        for i in range(self.max_iterations):
            print(f"--- Turn {i+1} ---")
            
            # 5. Call the LLM
            response = chain.invoke({"messages": messages})
            print(response)
            
            # 6. Add the AI's response to the message history
            messages.append(response)
            
            tool_calls = []
            # 7. CORRECTED LOGIC: Try to extract and parse JSON
            try:
                json_str = response.content[response.content.find('{') : response.content.rfind('}') + 1]
                data = json.loads(json_str)
                tool_calls = data.get("tool_calls", [])

            except (ValueError, json.JSONDecodeError):
                print("--- Final Answer (No valid tool calls found) ---")
                return {
                    "short_answer": "Jobs Done!",
                    "explanation": response.content # Return the final text content
                }

            # 8. Check if the response has tool calls
            if not tool_calls:
                # If tool_calls is empty, the conversation is over
                print("--- Final Answer ---")
                return {
                    "short_answer": "Jobs Done!",
                    "explanation": response.content # Return the final text content
                }

            print(f"Tool calls: {tool_calls}")
            
            import uuid 
            for tool_call in tool_calls:
                if "id" not in tool_call or not tool_call["id"]:
                    tool_call["id"] = str(uuid.uuid4())

            # 9. Execute the requested tool calls
            for tool_call in tool_calls:
                tool_name = tool_call.get("name")
                tool_call_id = tool_call["id"]
                    
                if tool_name in self.tool_map:
                    try:
                        tool_to_call = self.tool_map[tool_name]
                        tool_args = tool_call.get("args", {})
                        observation = tool_to_call.invoke(tool_args)
                        
                        # 10. Add the tool's output to the message history
                        messages.append(
                            ToolMessage(
                                content=str(observation), 
                                tool_call_id=tool_call_id
                            )
                        )
                    except Exception as e:
                        print(f"Error executing tool {tool_name}: {e}")
                        messages.append(
                            ToolMessage(
                                content=f"Error: {e}", 
                                tool_call_id=tool_call.get("id")
                            )
                        )
                else:
                    print(f"Tool {tool_name} not found.")
                    messages.append(
                        ToolMessage(
                            content=f"Error: Tool '{tool_name}' not found.",
                            tool_call_id=tool_call.get("id"),
                        )
                    )

        return {"short_answer": "Max iterations reached.", "explanation": "The agent could not finish the task in time."}

