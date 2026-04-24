from PIL import Image, ImageDraw, ImageFont
import math
from typing import List

class MangaRenderer:
    def __init__(self):
        # Fallback to default font if a system font is not easily available
        # In a real scenario, you'd load a specific ttf like "WildWords" or "ComicSans"
        try:
            # Using arial as a safe fallback on windows
            self.font = ImageFont.truetype("arial.ttf", 24)
            self.speaker_font = ImageFont.truetype("arialbd.ttf", 20)
        except IOError:
            self.font = ImageFont.load_default()
            self.speaker_font = ImageFont.load_default()

    def render_pages(self, scenes_data: List[dict], generated_images: List[Image.Image]) -> List[Image.Image]:
        """
        Takes the scenes data (with dialogue) and their corresponding generated images,
        and renders them onto manga pages. For now, we'll combine them sequentially.
        """
        # Simplistic vertical strip rendering for the "manga" format
        # Alternatively, we could compose proper pages, but joining them vertically
        # with dialogue bubbles overlay matches the Webtoon/Manga digital reading style well.
        
        composited_images = []
        
        for scene, img in zip(scenes_data, generated_images):
            # Create a copy so we don't modify the original
            panel = img.copy()
            draw = ImageDraw.Draw(panel)
            
            dialogues = scene.get("dialogue", [])
            
            # Draw speech bubbles
            y_offset = 20
            for dt in dialogues:
                speaker = dt["speaker"]
                text = dt["text"]
                
                # Bubble dimension estimation (Very basic)
                box_width = 300
                text_wrapped = self._wrap_text(text, self.font, box_width - 40)
                
                # Estimate height based on newlines
                lines = text_wrapped.split("\n")
                box_height = max(100, (len(lines) + 2) * 30 + 40)
                
                x_offset = 20
                
                # Draw bubble background (ellipse or rounded rectangle, we'll use a rounded rectangle approximation or a simple rectangle)
                draw.rounded_rectangle(
                    [x_offset, y_offset, x_offset + box_width, y_offset + box_height],
                    radius=20,
                    fill="white",
                    outline="black",
                    width=3
                )
                
                # Draw Speaker Name
                draw.text((x_offset + 20, y_offset + 10), f"{speaker}:", font=self.speaker_font, fill="black")
                
                # Draw Text
                draw.text((x_offset + 20, y_offset + 40), text_wrapped, font=self.font, fill="black", spacing=5)
                
                y_offset += box_height + 20
                
            composited_images.append(panel)
            
        return composited_images
        
    def _wrap_text(self, text, font, max_width):
        """Simple text wrapping utility for PIL"""
        if hasattr(font, 'getbbox'):
            get_width = lambda t: font.getbbox(t)[2]
        else:
            get_width = lambda t: font.getsize(t)[0]

        lines = []
        for word in text.split(" "):
            if not lines:
                lines.append(word)
            else:
                current_line = lines[-1]
                if get_width(current_line + " " + word) <= max_width:
                    lines[-1] = current_line + " " + word
                else:
                    lines.append(word)
        return "\n".join(lines)
