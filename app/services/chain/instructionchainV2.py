# fixed_instruction_chain.py
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_react_agent, AgentExecutor
from app.services.AutoGuiV2 import ToolBox
from app.services.AutoGuiV2 import (
    KeyboardHotkey,
    KeyboardWriteText,
    KeyboardPressKey,
)

ENHANCED_SYSTEM_PROMPT = """
You are an advanced desktop automation assistant that can control the user's computer through mouse and keyboard actions. 
You have access to tools that allow you to:
- Take screenshots to see the current state of the screen
- Move and click the mouse at specific coordinates
- Type text and use keyboard shortcuts
- Open applications
- Scroll and navigate through interfaces

CRITICAL TOOL USAGE RULES:
1. Tool names do NOT include parentheses - use "ShowScreen" not "ShowScreen()"
2. Always provide proper Action Input parameters in JSON format
3. For tools with no parameters, use empty dict: {{"tool_input": ""}} 
4. For tools with parameters, provide all required parameters

AVAILABLE TOOLS:
{tools}

TOOL CALLING FORMAT:
Action: ToolName
Action Input: {{"parameter1": value1, "parameter2": value2}}

IMPORTANT GUIDELINES:
1. Always start by taking a screenshot to see the current state of the screen
2. Break down complex tasks into smaller, manageable steps
3. Wait for applications to load before proceeding with the next action
4. Be precise with coordinates - analyze the screenshot carefully before clicking
5. Use appropriate delays between actions to ensure stability
6. If an action fails, take a screenshot to assess the new state and adapt your approach
7. For web-based tasks, remember that pages may take time to load
8. Always verify that your actions were successful by taking a new screenshot

AVAILABLE TOOLS AND THEIR PARAMETERS:
- ShowScreen: No parameters needed
- CursorMove: coordinate_x_cursor_target, coordinate_y_cursor_target, duration (optional)
- CursorMoveAndClick: coordinate_x_cursor_target, coordinate_y_cursor_target, num_of_clicks (optional), secs_between_clicks (optional), button (optional), duration (optional)
- CursorDoubleClick: coordinate_x_cursor_target, coordinate_y_cursor_target, duration (optional)
- CursorRightClick: coordinate_x_cursor_target, coordinate_y_cursor_target, duration (optional)
- CursorDrag: coordinate_x_cursor_target, coordinate_y_cursor_target, num_seconds (optional), button (optional)
- KeyboardWriteText: text_string, interval (optional)
- KeyboardPressKey: key, presses (optional), interval (optional)
- KeyboardHotkey: hotkey_keys (string with '+' separator like 'ctrl+c')
- ScrollScreen: direction (optional), clicks (optional), x (optional), y (optional)
- WaitAndObserve: seconds (optional)

COMMON PATTERNS:
- To navigate web pages: Use clicks, scrolling, and text input
- To handle forms: Click input fields, then type text
- To handle menus: Right-click for context menus, left-click for selections
- To switch between windows: Use KeyboardHotkey with 'alt+tab'

Use the following format for your responses:

Question: the input question you must answer
Thought: you should always think about what to do next
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action in JSON format
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

REMEMBER: 
- Always take a screenshot first to understand the current state
- Use proper JSON format for Action Input
- Be patient with loading times
- Double-check your coordinates before clicking
- Provide clear feedback about what you're doing and why

Begin!

Question: {input}
Thought:{agent_scratchpad}
"""

class EnhancedInstructionChain:
    def __init__(self, llm, max_iterations: int = 15, verbose: bool = True):
        self.llm = llm
        self.max_iterations = max_iterations
        self.verbose = verbose

    def __call__(self, input: str):
        """
        Execute the instruction chain with enhanced error handling and retries.
        
        Args:
            input (str): The user's instruction
            
        Returns:
            dict: The result of the agent execution
        """
        try:
            # KeyboardHotkey({"hotkey_keys": "win+r"})
            # KeyboardWriteText({"text_string": "chrome"})
            # KeyboardPressKey({"key": "enter"})

            # Create the prompt template
            prompt = ChatPromptTemplate.from_template(ENHANCED_SYSTEM_PROMPT)
            
            agent = create_react_agent(
                llm=self.llm, 
                tools=ToolBox, 
                prompt=prompt
            )
            
            agent_executor = AgentExecutor(
                agent=agent, 
                tools=ToolBox,
                max_iterations=self.max_iterations,
                verbose=self.verbose,
                handle_parsing_errors=True,
                return_intermediate_steps=True
            )
            
            # Add some context to help the agent understand the task better
            enhanced_input = self._enhance_input(input)
            
            result = agent_executor.invoke({
                "input": enhanced_input,
                "tool_names": [tool.name for tool in ToolBox]
            })
            
            if self.verbose:
                print("=== EXECUTION COMPLETE ===")
                print(f"Final result: {result.get('output', 'No output')}")
                
            return result
            
        except Exception as e:
            error_msg = f"Error executing instruction chain: {e}"
            print(error_msg)
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
            
        if any(keyword in input.lower() for keyword in ['search', 'find', 'look for']):
            context_additions.append("Use KeyboardHotkey with 'ctrl+f' to open search functionality when available.")
            
        if context_additions:
            enhanced_input = f"{input}\n\nAdditional context: {' '.join(context_additions)}"
        else:
            enhanced_input = input
            
        return enhanced_input

    def get_available_tools(self) -> list:
        """Return list of available tool names for reference."""
        return [tool.name for tool in ToolBox]

    def describe_capabilities(self) -> str:
        """Return a description of the system's capabilities."""
        return """
        This desktop automation system can:
        
        🖱️ Mouse Control:
        - Move cursor to any screen position
        - Left-click, right-click, double-click
        - Drag and drop operations
        - Scroll in any direction
        
        ⌨️ Keyboard Control:
        - Type any text with configurable speed
        - Press individual keys (Enter, Tab, etc.)
        - Execute keyboard shortcuts (Ctrl+C, Alt+Tab, etc.)
        
        🖥️ Application Control:
        - Open applications by name
        - Take screenshots to see current state
        - Wait for applications to load
        - Navigate through interfaces
        
        🌐 Web Automation:
        - Open browsers and navigate to websites
        - Fill forms and click buttons
        - Search for content
        - Handle multiple tabs and windows
        
        📧 Email Tasks:
        - Open email clients or web interfaces
        - Navigate through emails
        - Compose and send messages
        - Search for specific emails
        
        Example commands:
        - "Open Chrome browser and go to Gmail"
        - "Find the email from John and reply to it"
        - "Open Calculator and compute 15 * 23"
        - "Take a screenshot of the current screen"
        - "Open Notepad and write a shopping list"
        """

# Example usage and testing function
def test_instruction_chain(llm, test_instruction: str = "Take a screenshot of the current screen"):
    """
    Test the instruction chain with a simple command.
    
    Args:
        llm: The language model instance
        test_instruction (str): Test instruction to execute
    """
    print(f"Testing instruction: {test_instruction}")
    
    chain = EnhancedInstructionChain(llm, verbose=True)
    result = chain(test_instruction)
    
    print("Test completed!")
    return result

# Integration helper for common tasks
class CommonTasks:
    """Helper class with pre-defined common automation tasks."""
    
    @staticmethod
    def open_gmail_instructions():
        return """
        Open Google Chrome browser, navigate to Gmail.com, and wait for the page to load completely.
        If not already signed in, wait for the sign-in page to appear.
        """
    
    @staticmethod
    def find_email_instructions(sender_name: str):
        return f"""
        In the Gmail interface, use the search box to find emails from {sender_name}.
        Click on the search box, type the sender's name, and press Enter.
        Wait for search results to load.
        """
    
    @staticmethod
    def compose_email_instructions(recipient: str, subject: str, body: str):
        return f"""
        In Gmail, click the Compose button to start a new email.
        Fill in the recipient field with: {recipient}
        Fill in the subject field with: {subject}
        Fill in the email body with: {body}
        """
