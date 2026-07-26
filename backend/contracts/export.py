from typing import List, Optional
from pydantic import BaseModel, Field

class PanelExportSlot(BaseModel):
    panel_number: int = Field(description="Sequential panel number on the page")
    image_asset_path: str = Field(description="File path or URL to rendered panel image asset")
    shot_type: str = Field(description="Shot type framing description")
    speech_bubbles: List[dict] = Field(default_factory=list, description="Overlay speech bubble text and styling specs")

class PageExportBundle(BaseModel):
    page_number: int = Field(description="Page index within chapter")
    grid_style: str = Field(description="Layout grid style")
    panels: List[PanelExportSlot] = Field(default_factory=list, description="Ordered panel export slots")

class ExportManifest(BaseModel):
    project_id: str = Field(description="Associated project ID")
    title: str = Field(description="Manga title")
    total_pages: int = Field(description="Total page count")
    pages: List[PageExportBundle] = Field(default_factory=list, description="Pages compiled in export bundle")
    export_format: str = Field(default="PDF_MANIFEST", description="Target export format (HTML, SVG, PDF)")
    output_pdf_path: str = Field(description="File path to compiled PDF/HTML manifest bundle")
