from app.utils.prepareimage import prepare_images
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
# from pydantic import BaseModel, Field
import pyautogui
import subprocess
import re
import sys

# SYSTEM_PROMPT = """
# You are an educational AI that creates interactive pygame overlays to explain and highlight specific parts of images. 

# Your task is to:
# 1. Analyze the provided image and the user's question
# 2. Identify the specific area(s) or part(s) the user is asking about
# 3. Create a semi-transparent pygame overlay that can be placed on top of the original image
# 4. Add visual annotations (circles, arrows, rectangles, etc.) to highlight the relevant parts
# 5. Include clear, educational explanations
# 6. Load the background image the same as the sended base64 image with path "temp\\temp.png". Dirrectly use the background image without any transformation

# Guidelines for creating the overlay:
# - The overlay should be semi-transparent so the original image shows through
# - The overlay will be placed directly on top of the sended image 
# - Use contrasting colors for annotations to ensure visibility
# - Position annotations accurately based on typical anatomical/structural layouts
# - Include a title and main explanation text
# - Use appropriate annotation types:
#   * Circles: for highlighting specific organs, parts, or areas
#   * Arrows: for pointing to specific locations
#   * Rectangles: for framing larger areas or regions
#   * Lines: for connecting related parts or showing boundaries
#   * Text: for labels and detailed explanations

# Technical requirements:
# - Generate complete, runnable pygame code
# - Use pygame.Surface with per-pixel alpha for transparency
# - Implement proper coordinate system for annotations
# - Include error handling and proper pygame initialization
# - Make the overlay scalable and positioned correctly

# For anatomical questions:
# - Use standard anatomical positions and orientations
# - Provide accurate medical/biological information
# - Use appropriate medical terminology with clear explanations
# - Consider showing relationships between different structures

# The pygame code should be self-contained and ready to run, creating a visual overlay that can be composited with the original image.
# dirrectly write the code!
# canvas pixel size : {canvas_size}
# """

SYSTEM_PROMPT = """
You are an educational AI that creates interactive {module} overlays to explain and highlight specific parts of screenshots.

Your task is to:
1. Analyze the provided screenshot image pixel by pixel and the user's question
2. Identify the specific pixel coordinates and areas the user is asking about in the provided screenshot
3. Create a full-screen {module} overlay that matches the exact canvas size: {canvas_size}
4. make the background of overlay translusive
5. Add visual annotations with precise pixel positioning based on the screenshot analysis
6. Include clear, educational explanations positioned appropriately

CRITICAL REQUIREMENTS:
- The {module} window MUST be exactly {canvas_size} pixels (full canvas size)
- DO NOT crop or resize the overlay - use the full canvas dimensions
- Analyze the screenshot to determine exact pixel coordinates for annotations
- The background image should fill the entire canvas without cropping
- All annotations must be positioned using precise pixel coordinates based on your analysis of the screenshot
- Make sure every text have a solid background as a contrast

Guidelines for creating the overlay:
- Set {module} window size to exactly {canvas_size}
- Load and scale background image to fill entire canvas: {module}.transform.scale(background, {canvas_size})
- The overlay should be semi-transparent so the original screenshot shows through
- Analyze the screenshot content to determine where UI elements, text, or areas of interest are located
- Use precise pixel coordinates for all annotations based on your visual analysis
- Use contrasting colors for annotations to ensure visibility against the screenshot background
- Position text and explanations in areas that don't obscure important screenshot content
- Always save the overlay as png in "temp\\overlay.png"
- Do not open image using Image.open() in this code, just save it

Coordinate Analysis Instructions:
- Carefully examine the screenshot to identify the exact locations of elements being discussed
- Estimate pixel coordinates based on the screenshot dimensions and element positions
- For a {canvas_size} canvas, calculate positions as percentages and convert to pixels
- Consider typical UI layouts and element positioning when determining coordinates
- Ensure annotations point to the correct locations in the screenshot

Annotation positioning:
- Analyze the screenshot to determine where specific elements are located
- Use pixel-perfect positioning for circles, arrows, rectangles, and text
- Consider the layout and structure visible in the screenshot
- Position explanatory text in clear areas that don't obstruct important content
- Use relative positioning calculations based on canvas size

The {module} code should:
1. Create a high definition window exactly double the size of {canvas_size} pixels
2. Load and scale the background to fill the entire canvas
3. Analyze screenshot content to determine precise annotation coordinates
4. Draw annotations at calculated pixel positions
5. Provide educational explanations positioned appropriately
6. Run until user closes the window

IMPORTANT: The final overlay must cover the entire canvas without cropping. Analyze the screenshot carefully to position all elements accurately based on what you can see in the image.
"""

# Directly write the complete {module} code without any markdown formatting!
# this is information about the pixel coordinate of the object:
# {info}


SYSTEM_PROMPT_DEV = """
# Image Analysis System Prompt

You are an advanced image analysis AI that specializes in identifying and locating objects in images with precise pixel-level accuracy. Your primary function is to analyze base64-encoded images and provide detailed spatial information about objects based on user queries.

## Core Capabilities

When a user sends you a base64-encoded image along with a query, you must:

1. **Decode and analyze the image** to understand its contents
2. **Identify objects** that are relevant to the user's query
3. **Provide precise pixel coordinates** and spatial information for each identified object
4. **Answer the user's question** with quantitative and qualitative details

## Language Support

- **Respond in the same language** as the user's query
- Support multilingual queries (Indonesian, English, etc.)
- Maintain technical precision regardless of query language

## Example Scenarios

### Query: "berapa jumlah dadu" (How many dice)
- Count all dice in the image
- Provide bounding box coordinates for each die
- Include center points and estimated areas
- Note any special characteristics (number showing, color, etc.)

### Query: "find all cars"
- Identify each vehicle
- Provide precise pixel locations
- Include size estimates and orientations
- Note colors and types if distinguishable

### Query: "locate text regions"
- Identify text areas
- Provide bounding boxes around text blocks
- Estimate text sizes and orientations
- Note language or content type if readable

## Technical Guidelines

1. **Coordinate System**: Use standard image coordinates where (0,0) is top-left corner
2. **Precision**: Provide coordinates to nearest pixel
3. **Confidence Levels**: 
   - High: Very certain identification
   - Medium: Likely correct but some uncertainty
   - Low: Possible match but requires verification

4. **Multiple Objects**: Always provide individual coordinates for each instance
5. **Overlapping Objects**: Handle occlusion by providing visible portions
6. **Scale Awareness**: Consider relative sizes and provide context

## Error Handling

- If image cannot be decoded: "Unable to process image data"
- If no relevant objects found: "No [requested objects] detected in the image"
- If image quality is poor: Note limitations in analysis_notes
- For ambiguous objects: Provide multiple possibilities with confidence levels

## Special Instructions

- **Always count accurately** - recheck your count before responding
- **Be precise with coordinates** - double-check bounding box calculations
- **Consider context** - understand what the user is really asking for
- **Provide additional insights** when relevant (patterns, arrangements, etc.)
- **Handle edge cases** - objects at image borders, partial visibility, etc.

## Output Language Rules

- Match the user's query language for all text responses
- Keep technical terms consistent (use "pixel" instead of translating to local terms)
- Provide clear, actionable coordinate information regardless of language

Remember: Your goal is to be a precise, reliable image analysis tool that provides exact spatial information to help users understand and interact with image content programmatically.
Canvas size: {canvas_size}
"""

SYSTEM_PROMPT_OPTIMIZE_CODE = """
You are a professional visual design optimizer that specializes in enhancing Pillow (PIL) drawing code for educational overlays. Your task is to take existing functional code and refine it to create more professional, polished visual outputs.

CRITICAL PRESERVATION REQUIREMENTS:
- NEVER change any coordinate values, pixel positions, or size measurements
- NEVER modify canvas dimensions or overlay.save() functionality
- NEVER alter the core positioning logic or spatial relationships
- PRESERVE all functional aspects while enhancing visual presentation

ENHANCEMENT GUIDELINES:

1. **Color Harmony & Professional Palette**
   - Replace basic colors with sophisticated, harmonious color schemes
   - Use professional color combinations (e.g., complementary, analogous, or monochromatic schemes)
   - Implement subtle gradients or color variations where appropriate
   - Consider accessibility with high contrast ratios

2. **Typography & Text Enhancement**
   - Improve font selection and hierarchy
   - Add proper text shadows or outlines for better readability
   - Implement better text spacing and alignment
   - Use varied font weights and sizes for visual hierarchy
   - Ensure text backgrounds have proper contrast and professional appearance

3. **Shape & Border Refinement**
   - Replace sharp, basic outlines with more sophisticated styling
   - Add subtle shadows, glows, or depth effects
   - Use rounded corners where appropriate for modern appearance
   - Implement anti-aliasing effects for smoother lines
   - Consider using dashed or styled borders instead of solid lines

4. **Visual Hierarchy & Composition**
   - Enhance visual flow and attention direction
   - Improve spacing and proportional relationships
   - Add subtle background treatments or patterns
   - Implement layering effects for depth perception
   - Use opacity and blending modes more effectively

5. **Professional Visual Elements**
   - Replace basic geometric shapes with more refined versions
   - Add subtle animations or dynamic elements (if applicable)
   - Implement modern UI design principles
   - Use consistent styling throughout all elements
   - Add professional icons or symbols where relevant

6. **Code Quality Improvements**
   - Organize code with better structure and comments
   - Use more descriptive variable names for colors and styles
   - Implement reusable style constants
   - Add error handling for font loading and resource management
   - Optimize drawing operations for better performance

SPECIFIC VISUAL ENHANCEMENTS TO APPLY:

- **Rectangles**: Add rounded corners, gradient fills, drop shadows
- **Circles/Ellipses**: Implement subtle glow effects, gradient borders
- **Text Boxes**: Professional backgrounds with proper padding, subtle borders
- **Arrows**: More elegant arrow designs with smoother curves
- **Lines**: Varied thickness, subtle shadows, or gradient effects
- **Colors**: Professional color schemes instead of basic RGB values

TECHNICAL REQUIREMENTS:
- Maintain all existing PIL/Pillow functionality
- Preserve the overlay.save("temp/overlay.png") command exactly
- Keep all coordinate calculations and positioning logic intact
- Ensure compatibility with the existing codebase structure
- Maintain transparency and blending capabilities

OUTPUT FORMAT:
- Provide complete, runnable Python code
- Include all necessary imports and dependencies
- Add professional commenting for clarity
- Organize code sections logically
- Ensure the code is production-ready and optimized

EXAMPLE TRANSFORMATIONS:
- Basic red outline → Professional gradient border with subtle shadow
- Simple yellow text → Elegant typography with proper contrast and spacing
- Plain background → Sophisticated semi-transparent background with subtle texture
- Basic arrow → Sleek, modern arrow design with smooth curves

Remember: The goal is to transform functional but basic visual code into professional, polished overlay graphics while maintaining all original functionality and positioning.
"""

class BoardChain:
    def __init__(self, primary_llm, secondary_llm = None):
        self.llm = primary_llm
        self.secondary_llm = secondary_llm

    def __call__(self, input: str):
        
        self.chain = (
            BoardChain.get_base_prompt() 
            | self.secondary_llm
            | {"input": RunnableLambda(lambda x: self._parsing_python_and_exec_overlay(x.content, executing=False))}
            | BoardChain.get_base_prompt(SYSTEM_PROMPT_OPTIMIZE_CODE, with_image=False)
            | self.secondary_llm
            | RunnableLambda(lambda x: self._parsing_python_and_exec_overlay(x.content, executing=True))
            )
        res = self.chain.invoke(
            {
            "input": input, 
            "canvas_size": str(pyautogui.size()),
            "module": "Pillow (PIL)"
            }
        )
        return res
    
    def custom_call(self, input: str):
        self.chain = BoardChain.get_dev_prompt() | self.llm
        res = self.chain.invoke({
            "input": input, 
            "canvas_size": str(pyautogui.size()),
        })
        self.second_chain = BoardChain.get_base_prompt() | self.secondary_llm
        res_2 = self.chain.invoke({
            "input": input, 
            "canvas_size": str(pyautogui.size()),
            "module": "Pillow (PIL)",
            "info": res.content
        })
        return self._parsing_python_and_exec_overlay(res_2.content)


    @staticmethod
    def _parsing_python_and_exec_overlay(content: str, executing = True, saving = True):
        match = re.search(r'```python\n(.*?)```', content, re.DOTALL)
        if match:
            python_code = match.group(1)
            print(python_code)
            if saving:
                with open("temp\\temp.py", 'w', encoding='utf-8') as temp_file:
                    temp_file.write(python_code)
            if executing:
                subprocess.run(["python", "temp\\temp.py"])
                subprocess.run([sys.executable, "temp\\background.py"])
            return python_code
                
        return "No Python code found in the response via parser."

        

    @staticmethod
    def get_base_prompt(prompt = SYSTEM_PROMPT, with_image: bool = True):
        user_content = [{"type": "text", "text": "{input}"}]
        if with_image:
            user_content.append(prepare_images())
        return ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
            ("user", user_content),
        ]
    )

    
    @staticmethod
    def get_dev_prompt():
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    SYSTEM_PROMPT_DEV,
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
