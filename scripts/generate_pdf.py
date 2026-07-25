# scripts/generate_pdf.py
import sys
import os
from fpdf import FPDF

class KuroAIPDF(FPDF):
    def header(self):
        # Top header on every page except the first page
        if self.page_no() > 1:
            self.set_font("helvetica", "I", 8)
            self.set_text_color(100, 110, 120)
            self.cell(0, 8, "KuroAI - Generative Manga Microservices Pipeline", 0, 0, "L")
            self.cell(0, 8, "Technical Documentation", 0, 1, "R")
            self.set_draw_color(220, 225, 230)
            self.set_line_width(0.5)
            self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
            self.ln(10)

    def footer(self):
        # Footer on every page except the first page
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font("helvetica", "I", 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")
            
            # Subtle branding on the right of footer
            self.set_x(-50)
            self.cell(0, 10, "Built by Sachin Pandey", 0, 0, "R")

def create_kuroai_pdf(output_path):
    pdf = KuroAIPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # ----------------------------------------------------
    # PAGE 1: COVER PAGE
    # ----------------------------------------------------
    pdf.add_page()
    
    # Decorative Top Accent Bar (Navy Blue)
    pdf.set_fill_color(18, 30, 49) # Deep Dark Navy
    pdf.rect(0, 0, pdf.w, 15, "F")
    
    # Bottom Accent Bar
    pdf.rect(0, pdf.h - 15, pdf.w, 15, "F")
    
    pdf.ln(40)
    
    # Title Block
    pdf.set_font("helvetica", "B", 36)
    pdf.set_text_color(18, 30, 49)
    pdf.cell(0, 15, "KuroAI", 0, 1, "C")
    
    # Subtitle
    pdf.set_font("helvetica", "B", 16)
    pdf.set_text_color(100, 110, 120)
    pdf.cell(0, 10, "Generative Manga Microservices Pipeline", 0, 1, "C")
    
    pdf.ln(15)
    
    # Horizontal separator line
    pdf.set_draw_color(180, 190, 200)
    pdf.set_line_width(1.0)
    pdf.line(40, pdf.get_y(), pdf.w - 40, pdf.get_y())
    
    pdf.ln(20)
    
    # Short description
    pdf.set_font("helvetica", "", 11)
    pdf.set_text_color(60, 60, 60)
    desc = ("An enterprise-grade, AI-driven storytelling platform serving as a "
            "comprehensive MVP demonstrating full-stack engineering, microservices "
            "architecture, LLM scene planning, and Stable Diffusion panel rendering.")
    pdf.multi_cell(0, 6, desc, align="C")
    
    pdf.ln(60)
    
    # Metadata Block
    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(18, 30, 49)
    pdf.cell(0, 6, "Author: Sachin Pandey", 0, 1, "C")
    pdf.set_font("helvetica", "", 9)
    pdf.set_text_color(100, 110, 120)
    pdf.cell(0, 6, "Platform Architect & Full-Stack Engineer", 0, 1, "C")
    pdf.cell(0, 6, "Date: May 2026", 0, 1, "C")
    pdf.cell(0, 6, "Version: 1.0.0 (MVP)", 0, 1, "C")
    
    # ----------------------------------------------------
    # PAGE 2: TABLE OF CONTENTS & GOALS
    # ----------------------------------------------------
    pdf.add_page()
    
    # Heading Helper
    def write_h1(text):
        pdf.set_font("helvetica", "B", 16)
        pdf.set_text_color(18, 30, 49)
        pdf.cell(0, 10, text, 0, 1, "L")
        # Line underneath
        pdf.set_draw_color(18, 30, 49)
        pdf.set_line_width(0.8)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
        pdf.ln(5)

    def write_h2(text):
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(40, 50, 70)
        pdf.cell(0, 8, text, 0, 1, "L")
        pdf.ln(2)

    def write_paragraph(text):
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 5, text)
        pdf.ln(4)

    def write_bullet(title, text):
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(50, 50, 50)
        pdf.cell(5, 5, chr(149), 0, 0)
        pdf.cell(40, 5, title, 0, 0)
        pdf.set_font("helvetica", "", 10)
        # Calculate remaining width
        remaining_w = pdf.w - pdf.l_margin - pdf.r_margin - 45
        pdf.multi_cell(remaining_w, 5, text)
        pdf.ln(2)

    write_h1("1. Project Overview & Objectives")
    
    write_paragraph(
        "KuroAI is a robust, highly scalable web application that transforms textual narratives "
        "into breathtaking visual manga panels using Large Language Models (LLMs) and Stable Diffusion. "
        "This repository serves as a Minimum Viable Product (MVP) showcasing production-ready software "
        "engineering principles. It was designed to demonstrate expertise across modern technology "
        "stacks, specifically aligning with full-stack enterprise development requirements."
    )
    
    write_h2("Core Project Objectives:")
    
    write_bullet("AI Storytelling:", "Seamlessly map user-defined creative premises to multi-panel manga storyboard layouts.")
    write_bullet("Visual Consistency:", "Enforce strict character feature details (hair style, eyes, outfits) and artistic linework style across multiple generated frames.")
    write_bullet("Service Decoupling:", "Establish isolated API service zones, ensuring frontend presentation, backend business logic, and heavy compute AI pipelines are decoupled.")
    write_bullet("Extensibility:", "Design clean adapters for LLMs (Ollama/Mistral) and diffusion systems, facilitating future vendor swaps or model upgrades.")
    
    pdf.ln(5)
    
    # ----------------------------------------------------
    # SYSTEM ARCHITECTURE & TECH STACK
    # ----------------------------------------------------
    write_h1("2. System Architecture & Tech Stack")
    
    write_paragraph(
        "KuroAI runs on a modern, decoupled microservices model. Instead of binding heavy machine "
        "learning calculations directly to the application layer, all generative tasks are routed through "
        "a secure python-based microservice."
    )
    
    write_h2("Component Breakdown:")
    
    write_bullet("React & TS Client:", "Modern frontend designed with Vite. Implements Framer Motion and custom CSS variables for premium visual responsiveness and interactive canvas tools.")
    write_bullet("Spring Boot Backend:", "Serves as the gateway layer. Implements stateless JWT authentication, secures endpoints, and proxies generation payload calls to the python AI microservice.")
    write_bullet("FastAPI Service:", "Dedicated Python service running the AI orchestration engine. Integrates Hugging Face's Diffusers pipeline and local LLM clients.")
    
    pdf.ln(5)
    
    # Table of Tech Stack
    pdf.set_fill_color(240, 243, 246)
    pdf.set_text_color(18, 30, 49)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(50, 8, " Service Layer", 1, 0, "L", fill=True)
    pdf.cell(55, 8, " Technology Stack", 1, 0, "L", fill=True)
    pdf.cell(80, 8, " Key Features", 1, 1, "L", fill=True)
    
    pdf.set_font("helvetica", "", 9)
    pdf.set_text_color(50, 50, 50)
    
    # Row 1
    pdf.cell(50, 8, " Frontend Presenter", 1, 0, "L")
    pdf.cell(55, 8, " React.js, TypeScript, Vite, Framer Motion", 1, 0, "L")
    pdf.cell(80, 8, " Interactive canvas panel, glassmorphism UI", 1, 1, "L")
    
    # Row 2
    pdf.cell(50, 8, " Security & Gateway Backend", 1, 0, "L")
    pdf.cell(55, 8, " Java 17, Spring Boot 3, JPA, H2", 1, 0, "L")
    pdf.cell(80, 8, " JWT filters, endpoint proxying, schema validation", 1, 1, "L")
    
    # Row 3
    pdf.cell(50, 8, " AI Generation Service", 1, 0, "L")
    pdf.cell(55, 8, " Python 3.9+, FastAPI, Uvicorn", 1, 0, "L")
    pdf.cell(80, 8, " Local model load, CUDA memory optimization", 1, 1, "L")

    # ----------------------------------------------------
    # PAGE 3: UNDER THE HOOD: THE AI PIPELINE
    # ----------------------------------------------------
    pdf.add_page()
    
    write_h1("3. Under the Hood: The AI Generation Pipeline")
    
    write_paragraph(
        "The core generation request triggers a deterministic multi-stage sequence orchestrated "
        "by Python's KuroAIOrchestrator class:"
    )
    
    write_h2("Stage 1: Storyboard Planning")
    write_paragraph(
        "The system forwards the user's core story prompt to a StoryPlannerLLM instance. This class "
        "interfaces with Ollama (running the mistral model) to parse and output a structured JSON schema. "
        "The schema defines four consecutive scenes, each containing action sequences, speaker dialogues, "
        "appropriate visual lighting moods, and camera angles."
    )
    
    write_h2("Stage 2: Style & Composition Control")
    write_paragraph(
        "Rather than using unstructured prompts, the SceneDecomposer merges the output storyboard scenes "
        "with design specifications detailed in configs/visual_style.yaml. This system injects "
        "high-quality negative prompt anchors (distorted anatomy, bad proportions) and positive artistic anchors "
        "(high-contrast black-and-white manga, clean lineart, heavy dramatic shading)."
    )
    
    write_h2("Stage 3: Enforcing Character Consistency")
    write_paragraph(
        "To ensure that the characters remain consistent across panels, the CharacterManager assigns a "
        "deterministic integer seed generated from the character's name hash. When generating scenes containing "
        "the character (e.g., Akira the Hero), the StabilityImageAdapter forces the Stable Diffusion generator "
        "to use this fixed seed. This produces matching facial ratios, hairstyles, and outfits under different setups."
    )
    
    write_h2("Stage 4: Rendering & Layout Synthesis")
    write_paragraph(
        "Once the Stable Diffusion pipeline generates the individual panel images, the MangaRenderer utilizes "
        "the Pillow library to dynamically overlay speech bubbles and nameplates based on the storyboard's "
        "dialogue array. The PageComposer subsequently assigns panel sizing (wide, standard, tall) for "
        "perfect canvas layouts on the web client."
    )

    # ----------------------------------------------------
    # PAGE 4: FUTURE ROADMAP
    # ----------------------------------------------------
    pdf.add_page()
    
    write_h1("4. Future Production-Level Scale Roadmap")
    
    write_paragraph(
        "To scale KuroAI into an enterprise SaaS hosting thousands of active users, the platform "
        "architecture is prepared to incorporate the following production features:"
    )
    
    write_bullet("DevSecOps CI/CD Pipelines:", "Implement automated testing and formatting checks via GitHub Actions, combined with static analysis security testing (SAST) to secure code layers.")
    
    write_bullet("Event-Driven AI Queue (Kafka):", "Decouple HTTP POST requests from model run cycles. Using Kafka or RabbitMQ, jobs are queued instantly and executed asynchronously, improving throughput.")
    
    write_bullet("Distributed Caching (Redis):", "Cache popular model prompts and images to dramatically lower GPU computation expenses and page load delays.")
    
    write_bullet("Metadata Versioning Control:", "A specialized Git-like versioning backend allowing creators to branch, edit, and rollback panel manipulations and dialogue lines securely.")
    
    write_bullet("Federated Single Sign-On (SSO):", "Incorporate Spring Security OAuth2 configurations to handle Google, GitHub, and Enterprise Active Directory identity integrations.")
    
    pdf.ln(15)
    
    # Professional Closing Block
    pdf.set_fill_color(245, 245, 245)
    pdf.set_draw_color(180, 190, 200)
    pdf.rect(15, pdf.get_y(), 180, 30, "FD")
    
    pdf.set_y(pdf.get_y() + 5)
    pdf.set_x(20)
    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(18, 30, 49)
    pdf.cell(0, 5, "KuroAI Architectural Blueprint Summary Document", 0, 1, "L")
    
    pdf.set_x(20)
    pdf.set_font("helvetica", "I", 9)
    pdf.set_text_color(100, 110, 120)
    pdf.cell(0, 5, "Engineered to demonstrate modern AI/ML pipelines and decoupled microservices.", 0, 1, "L")
    pdf.set_x(20)
    pdf.cell(0, 5, "Contact & Support: Sachin Pandey | KuroAI Platform Engineering", 0, 1, "L")
    
    # Save the output file
    pdf.output(output_path)
    print(f"Successfully generated KuroAI PDF documentation at: {output_path}")

if __name__ == "__main__":
    out_dir = "docs"
    os.makedirs(out_dir, exist_ok=True)
    pdf_path = os.path.join(out_dir, "KuroAI_Documentation.pdf")
    create_kuroai_pdf(pdf_path)
