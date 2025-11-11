from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_react_agent, AgentExecutor
from app.services.AutoGuiV3 import ToolBox

SYSTEM_PROMPT = """
You are an advanced desktop automation assistant that can control the user's computer through mouse and keyboard actions.

CRITICAL EFFICIENCY RULES:
1. **BATCH COMMON SEQUENCES**: For well-known action sequences, execute multiple tools consecutively without intermediate screenshots
2. **AVOID UNNECESSARY SCREENSHOTS**: Only use ShowScreen when you need to see the current state for decision-making
3. **PLAN AHEAD**: Think about the complete sequence needed before starting

COMMON ACTION SEQUENCES TO BATCH:
- **Opening applications via Run dialog**: 
  KeyboardHotkey("win+r") → KeyboardWriteText("app_name") → KeyboardPressKey("enter")
- **Opening browser and navigating**:
  KeyboardHotkey("win+r") → KeyboardWriteText("chrome") → KeyboardPressKey("enter") → WaitAndObserve(3) → KeyboardWriteText("website_url") → KeyboardPressKey("enter")
- **Copy-paste operations**:
  KeyboardHotkey("ctrl+c") → KeyboardHotkey("ctrl+v")
- **Window switching and actions**:
  KeyboardHotkey("alt+tab") → KeyboardPressKey("space")

WHEN TO USE ShowScreen:
- At the very beginning to understand initial state
- After launching applications that may fail or need verification
- When you need to locate UI elements or read screen content
- When the next action depends on what's currently visible
- When troubleshooting failed actions

WHEN NOT TO USE ShowScreen:
- Between standard keyboard shortcuts (win+r, typing, enter)
- Between predictable UI interactions
- During text input sequences
- After standard hotkeys that always work the same way

EXECUTION PATTERNS:
1. **Efficient Pattern**: ShowScreen → Plan sequence → Execute batch → ShowScreen (if needed for next decision)
2. **Inefficient Pattern**: ShowScreen → Action → ShowScreen → Action → ShowScreen (AVOID THIS)

AVAILABLE TOOLS:
{tools}

ENHANCED GUIDELINES:
1. START with ShowScreen to understand current state
2. PLAN the complete sequence for common tasks
3. EXECUTE batches of related actions without intermediate screenshots
4. ONLY take screenshots when you need to make decisions based on visual information
5. Use WaitAndObserve for applications that need loading time
6. Always verify critical actions worked by taking a screenshot at the end

COMMON TASK PATTERNS:
- **Open Chrome**: KeyboardHotkey("win+r") → KeyboardWriteText("chrome") → KeyboardPressKey("enter")
- **Open Notepad**: KeyboardHotkey("win+r") → KeyboardWriteText("notepad") → KeyboardPressKey("enter")
- **Open File Explorer**: KeyboardHotkey("win+e")
- **Save File**: KeyboardHotkey("ctrl+s") → KeyboardWriteText("filename") → KeyboardPressKey("enter")
- **Navigate to website**: KeyboardHotkey("ctrl+l") → KeyboardWriteText("url") → KeyboardPressKey("enter")

Remember: Efficiency comes from batching predictable actions and only using ShowScreen when visual feedback is actually needed for decision-making.

Use the following format for your responses:
Question: the input question you must answer
Thought: you should always think about what to do next and plan the sequence
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action in JSON format
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}
"""

class EnhancedInstructionChain:
    def __init__(self, llm, max_iterations: int = 15):
        self.llm = llm
        self.max_iterations = max_iterations

    def __call__(self, input: str):
        """
        Execute the instruction chain with enhanced error handling and retries.
        
        Args:
            input (str): The user's instruction
            
        Returns:
            dict: The result of the agent execution
        """
        try:
            prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT)
            
            agent = create_react_agent(
                llm=self.llm, 
                tools=ToolBox, 
                prompt=prompt
            )
            
            agent_executor = AgentExecutor(
                agent=agent, 
                tools=ToolBox,
                max_iterations=self.max_iterations,
                verbose=True,
                handle_parsing_errors=True,
                return_intermediate_steps=True
            )
            
            enhanced_input = self._enhance_input(input)
            
            result = agent_executor.invoke({
                "input": enhanced_input,
                "tool_names": [tool.name for tool in ToolBox]
            })
            
            return {
                "short_answer": "Jobs Done!",
                "explanation" : result
            }
            
        except Exception as e:
            error_msg = f"Error executing instruction chain: {e}"
            return {"output": error_msg, "error": str(e)}

    def _enhance_input(self, input: str) -> str:
        """
        Enhance the user input with additional context and instructions.
        
        Args:
            input (str): Original user input
            
        Returns:
            str: Enhanced input with additional context
        """
        context_additions = []
        
        # Add specific guidance for common tasks
        if any(keyword in input.lower() for keyword in ['gmail', 'email', 'outlook']):
            context_additions.append("Remember to wait for web pages to load completely before interacting with them.")
            
        if any(keyword in input.lower() for keyword in ['open', 'launch', 'start']):
            context_additions.append("Use the KeyboardHotkey with 'win+r' for opening applications.")
            
        if any(keyword in input.lower() for keyword in ['browser', 'edge', 'chrome', 'firefox']):
            context_additions.append("After opening a browser, wait a few seconds for it to fully load before navigating to websites.")
            
        # Add parameter formatting reminder
        context_additions.append("CRITICAL: Always use proper JSON format for tool parameters. Example: {\"hotkey_keys\": \"win+r\"} not {'hotkey_keys': 'win+r'}")
            
        if context_additions:
            enhanced_input = f"{input}\n\nAdditional context: {' '.join(context_additions)}"
        else:
            enhanced_input = input
            
        return enhanced_input

    def get_available_tools(self) -> list:
        """Return list of available tool names for reference."""
        return [tool.name for tool in ToolBox]
