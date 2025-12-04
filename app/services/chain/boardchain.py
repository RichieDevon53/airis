from app.utils.prepareimage import prepare_images
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel, Field
from transformers import pipeline
from typing import List
from PIL import Image
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

class ObjectListOutput(BaseModel):
    objects: List[str] = Field(description="List of detected object names")

FIND_OBJECT_PROMPT = """
You are an Image Analysis Specialist agent that converts user requests into precise object detection queries. Your job is to analyze what the user wants to highlight in an image and output a single, perfectly formatted search string that will be used with an object detection model (OWL-ViT).

### CRITICAL RULES:
1. **ALWAYS** use this exact format: "the [object] in the screenshot"
2. **NEVER** output multiple queries or explanations - only the search string
3. **REMOVE** any quotes, brackets, or special characters from the user's request
4. **KEEP** colors, sizes, and descriptive words that help identify the object
5. **IF** the user mentions multiple objects, pick the MOST IMPORTANT one based on context

### QUERY FORMULA (MEMORIZE THIS):
✅ PERFECT: "the [exact object description] in the screenshot"
❌ BAD: "[object]" or "the [object]" or "[object] in image"

### EXAMPLES:
User: "Can you highlight the mushroom on the left?"
Output: "the mushroom on the left in the screenshot"

User: "the blue submit button"
Output: "the blue submit button in the screenshot"

User: "find the clock that's different"
Output: "the clock that's different in the screenshot"

User: "this butterfly"
Output: "the butterfly in the screenshot"

User: "highlight 'Submit' text"
Output: "the Submit text in the screenshot"

User: "the red icon vs green icon"
Output: "the red icon in the screenshot"  (pick most important)

User: "what's wrong here?"
Output: "the error in the screenshot"  (infer the most likely object)

### SPECIAL CASES:
- For text: "the [text content] text in the screenshot"  
  Example: "the Save text in the screenshot"
- For differences: "the [object] that is different in the screenshot"
- For buttons: "the [button text] button in the screenshot"
- If unsure: "the main object in the screenshot"

### OUTPUT FORMAT:
- ONLY output the search string
- NO quotes, NO punctuation at end, NO explanations
- EXACTLY one line of text

You are an expert at understanding user intent and converting it to perfect detection queries. Every query you generate must follow the formula exactly.
"""

SYSTEM_PROMPT = """
You are an educational AI that creates interactive {module} overlays to explain and highlight specific parts of screenshots.

Your task is to:
1. Analyze the provided screenshot image pixel by pixel, the user's question, AND any provided object detection data
2. Identify the specific pixel coordinates and areas the user is asking about using BOTH visual analysis AND object detection coordinates
3. Create a full-screen {module} overlay that matches the exact canvas size: {canvas_size}
4. Make the background of overlay translucent
5. Add visual annotations with precise pixel positioning based on screenshot analysis AND object detection data
6. Include clear, educational explanations positioned appropriately

CRITICAL REQUIREMENTS:
- The {module} window MUST be exactly {canvas_size} pixels (full canvas size)
- DO NOT crop or resize the overlay - use the full canvas dimensions
- Use object detection coordinates when available to ensure pixel-perfect accuracy
- The background image should fill the entire canvas without cropping
- All annotations must be positioned using precise pixel coordinates from analysis OR object detection data
- Make sure every text has a solid background as a contrast

OBJECT DETECTION DATA INTEGRATION:
{coordinates_info}

Priority rules for object detection data:
1. HIGH CONFIDENCE (≥0.7): Trust coordinates completely, use exact bbox/center
2. MEDIUM CONFIDENCE (0.4-0.69): Use coordinates as primary reference but verify with visual analysis
3. LOW CONFIDENCE (<0.4): Use only as secondary reference, rely primarily on visual analysis
4. For multiple detections of same object: Select highest confidence OR use ensemble average if similar confidence

Guidelines for creating the overlay:
- Set {module} window size to exactly {canvas_size}
- Load and scale background image to fill entire canvas: {module}.transform.scale(background, {canvas_size})
- The overlay should be semi-transparent so the original screenshot shows through
- When object detection data is available:
  * Use bbox coordinates for highlighting entire objects
  * Use center coordinates for placing annotation pointers and text
  * Consider object area to determine appropriate annotation size
- When NO object detection data is available, perform detailed visual analysis to estimate coordinates
- Use contrasting colors for annotations to ensure visibility against the screenshot background
- Position text and explanations in areas that don't obscure important screenshot content
- Always save the overlay as png in "temp\\overlay.png"
- Do not open image using Image.open() in this code, just save it

Coordinate Analysis Instructions:
- FIRST check if object detection data is provided for the requested elements
- IF object detection data exists:
  * Use the highest confidence detection for each unique object
  * Calculate center points: center_x = (x1 + x2) / 2, center_y = (y1 + y2) / 2
  * Use bbox for rectangular highlights, center for circular markers and text placement
- IF NO object detection data exists:
  * Carefully examine the screenshot to identify exact locations of elements
  * Estimate pixel coordinates based on screenshot dimensions and element positions
  * For {canvas_size} canvas, calculate positions as percentages and convert to pixels
  * Consider typical UI layouts and element positioning when determining coordinates
- ALWAYS verify object detection coordinates make sense with the screenshot content
- Ensure annotations point to the correct locations in the screenshot

Annotation positioning:
- For objects with detection data: Use bbox[0], bbox[1], bbox[2], bbox[3] for rectangle coordinates
- For text placement: Use center[0], center[1] as reference point, offset text to avoid overlap
- For arrows/pointers: Draw from text position to object center or edge
- Consider object size when determining annotation size and text placement
- Position explanatory text in clear areas adjacent to detected objects
- Use relative positioning calculations based on canvas size when detection data is unavailable

The {module} code should:
1. Create a high definition window exactly {canvas_size} pixels
2. Load and scale the background to fill the entire canvas
3. Process object detection data if provided, otherwise perform visual coordinate analysis
4. Draw annotations at calculated pixel positions (prefer detection data when available)
5. Provide educational explanations positioned appropriately near detected objects
6. Run until user closes the window

IMPORTANT: The final overlay must cover the entire canvas without cropping. Prioritize object detection coordinates when confidence is high (≥0.7), otherwise combine with visual analysis for maximum accuracy. Always validate that detected coordinates make sense within the screenshot context.
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
            BoardChain.get_base_prompt(FIND_OBJECT_PROMPT)
            | self.secondary_llm.with_structured_output(ObjectListOutput)
            | RunnableLambda(lambda x: {"input": input, "coordinates_info": self._find_coordinates_info(x.objects), "canvas_size": str(pyautogui.size()), "module": "Pillow (PIL)"})  # Format output for next prompt
            | BoardChain.get_base_prompt() 
            | self.secondary_llm
            | {"input": RunnableLambda(lambda x: self._parsing_python_and_exec_overlay(x.content, executing=False))}
            | BoardChain.get_base_prompt(SYSTEM_PROMPT_OPTIMIZE_CODE, with_image=False)
            | self.secondary_llm
            | RunnableLambda(lambda x: self._parsing_python_and_exec_overlay(x.content, executing=True))
        )
        res = self.chain.invoke(
            {
            "input": input, 
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
    def _find_coordinates_info(objects: List[str]):
        detector = pipeline('zero-shot-object-detection', model='IDEA-Research/grounding-dino-base', use_fast=True)
        image = Image.open("local/temp.png").convert('RGB')
        string_result = ""
        for obj in objects:
            results = detector(
                image,
                candidate_labels=[obj],  # The object the user is asking about
                threshold=0.1  # Lower threshold for UI elements
            )
            
            for result in results:
                bbox = result['box']
                coords = (
                    int(bbox['xmin']), 
                    int(bbox['ymin']), 
                    int(bbox['xmax']), 
                    int(bbox['ymax'])
                )
                if result['score'] > 0.2:
                    string_result += f"Object: {result['label']}, Confidence: {result['score']}, Coords: {coords}\n"
                
        if string_result:
            print("Coordinates Info:\n", string_result)
            return string_result
        return "No coordinates found."

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
