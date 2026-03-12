from typing import List


class PageComposer:
    def __init__(self, panels_per_page: int = 3):
        self.panels_per_page = panels_per_page

    def compose(self, scene_prompts: List[dict]) -> List[dict]:
        pages = []
        page_number = 1
        panel_number = 1

        for scene in scene_prompts:
            layout = self._choose_layout(panel_number)

            pages.append({
                "page": page_number,
                "panel": panel_number,
                "prompt": scene["positive_prompt"],
                "layout": layout,
                "style_anchor": scene["style_anchor"]
            })

            panel_number += 1
            if panel_number > self.panels_per_page:
                panel_number = 1
                page_number += 1

        return pages

    def _choose_layout(self, panel_number: int) -> str:
        if panel_number == 1:
            return "wide"
        elif panel_number == self.panels_per_page:
            return "tall"
        return "standard"
