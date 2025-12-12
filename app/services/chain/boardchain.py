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

FIND_OBJECTS_PROMPT = """
You are an Image Analysis Specialist that converts user requests into precise object detection queries. Output a JSON array of simplified object names for detection.

### CORE RULES:
1. **OUTPUT FORMAT**: Minified JSON array of strings (e.g., `["object1","object2"]`)
2. **SIMPLIFY NAMES**:
   - REMOVE: "the", "a", "an", "in the screenshot", quotes, brackets
   - KEEP: Colors, sizes, positions, text content, and key descriptors
   - NATURAL LANGUAGE: Use prepositions like "with", "on", "next to" for relationships
3. **MULTIPLE OBJECTS**:
   - Split combined requests ("X and Y" → separate entries)
   - Treat color/position variants as distinct objects
   - For comparisons ("vs", "different"), include all variants
4. **SPECIAL CASES**:
   - Text elements: `[text content] text` (e.g., "Submit text")
   - Buttons: `[button text] button` (e.g., "Cancel button")
   - Ambiguous requests: "main object" or "error indicator"

### NATURAL LANGUAGE FORMULA:
✅ GOOD: "green sprout with red hat", "left mushroom", "error message"
❌ BAD: "the green sprout", "mushroom in screenshot", "a button"

### OUTPUT REQUIREMENTS:
- ONLY output minified JSON array
- NO prefixes/suffixes, NO explanations
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
- Always use the exact coordinates provided by object detection
- <<NEW>> BEFORE USING ANY COORDINATES: Calculate scaling factors between original screenshot dimensions and {canvas_size}:
      scale_x = canvas_size[0] / original_image_width
      scale_y = canvas_size[1] / original_image_height
  THEN scale EVERY detection coordinate: (x * scale_x, y * scale_y)
- <<NEW>> HARD CLAMP all coordinates to [0, canvas_size] bounds after scaling

Guidelines for creating the overlay:
- Set {module} window size to exactly {canvas_size}
- Load background image WITHOUT RESIZING to preserve original dimensions
- <<ENHANCED>> Background rendering protocol:
    1. Create transparent canvas at {canvas_size}
    2. Calculate aspect ratio preservation:
        target_ratio = canvas_size[0] / canvas_size[1]
        img_ratio = original_width / original_height
    3. IF |target_ratio - img_ratio| > 0.05:
          - Resize screenshot to fit canvas while preserving aspect ratio (letterboxing)
          - Recalculate coordinate offsets using letterbox padding
    4. Paste background centered on canvas with translucent overlay (alpha=180)
- When object detection data is available:
  * Use ONLY detections with confidence ≥0.7
  * <<NEW>> Scale bbox coordinates FIRST using factors from CRITICAL REQUIREMENTS
  * Calculate center points from SCALED coordinates: 
        center_x = (scaled_x1 + scaled_x2) / 2
        center_y = (scaled_y1 + scaled_y2) / 2
  * Use bbox for rectangular highlights, center for circular markers and text placement
- When NO object detection data is available, perform detailed visual analysis to estimate coordinates
- Use contrasting colors for annotations (text BG: #0F0F0F with 220 alpha, text: #FFFFFF)
- Position text in clear areas using scaled coordinates as anchors
- Always save the overlay as png in "temp\\overlay.png"
- Do not open image using Image.open() in this code, just save it

Coordinate Analysis Instructions:
- FIRST check if object detection data is provided for the requested elements
- IF object detection data exists:
  * Filter to keep ONLY detections with confidence ≥0.7
  * <<MANDATORY>> Extract original screenshot dimensions BEFORE scaling coordinates
  * Calculate scaling factors: 
        scale_x = canvas_size[0] / original_width
        scale_y = canvas_size[1] / original_height
  * Scale ALL coordinates: 
        [x1, y1, x2, y2] = [coord * scale_x/scale_y appropriately]
  * Recalculate center from scaled bbox
  * CLAMP values: max(0, min(canvas_size[0], x)), max(0, min(canvas_size[1], y))
  * Validate: If scaled bbox area < 0.1% of canvas, discard detection
- IF NO object detection data exists:
  * Estimate positions as percentages of original image dimensions
  * Convert to canvas pixels using scaling factors above
- ALWAYS verify scaled coordinates align with visual content in screenshot

Object detection data:
{coordinates_info}

Annotation positioning (SCALED COORDINATES ONLY):
- Bounding boxes: Use scaled_bbox[0], scaled_bbox[1], scaled_bbox[2], scaled_bbox[3]
- Text placement: 
      text_x = max(10, min(canvas_size[0]-200, scaled_center_x - 100))
      text_y = scaled_bbox[1] - 30  # Above object
  IF text_y < 20: text_y = scaled_bbox[3] + 10  # Below if top overflow
- Arrows: Draw line from (text_x+90, text_y+15) to (scaled_center_x, scaled_center_y)
- Text background: Solid rectangle (text_x-5, text_y-5, text_x+200, text_y+40)

The {module} code should:
1. Create transparent RGBA canvas at EXACT {canvas_size}
2. Load original screenshot to get dimensions (DO NOT RESIZE YET)
3. <<NEW>> Calculate scaling factors and letterbox parameters FIRST
4. Process object detection data using scaled/clamped coordinates
5. Draw annotations ONLY using scaled coordinates
6. Save ONLY to "temp\\overlay.png" with no display operations

IMPORTANT: 
- Prioritize scaled object detection coordinates when confidence ≥0.7
- NEVER use raw detection coordinates without scaling
- Letterbox background image if aspect ratios differ >5%
- All text MUST have solid background rectangles
- Final output must be exactly {canvas_size} pixels
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
            BoardChain.get_base_prompt(FIND_OBJECTS_PROMPT)
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
        print("Objects to find:", objects)
        for obj in objects:
            results = detector(
                image,
                candidate_labels=[obj],  # The object the user is asking about
                threshold=0.1  # Lower threshold for UI elements
            )
            
            if results:  # Check if any results were found for this object
                # Find the result with the highest score for this object
                best_result = max(results, key=lambda x: x['score'])
                
                bbox = best_result['box']
                coords = (
                    int(bbox['xmin']), 
                    int(bbox['ymin']), 
                    int(bbox['xmax']), 
                    int(bbox['ymax'])
                )
                
                # Add the best result regardless of score (but only if it exists)
                string_result += f"{best_result['label']} | {coords}\n"
                
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
