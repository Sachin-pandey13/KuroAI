<div align="center">
  <img src="https://raw.githubusercontent.com/Sachin-pandey13/KuroAI/main/frontend/public/icons.svg" alt="KuroAI Logo" width="120" />
  <h1>KuroAI : Generative Manga Microservices Pipeline</h1>
  <p><em>An enterprise-grade, AI-driven storytelling platform serving as a comprehensive MVP demonstrating full-stack engineering, microservices architecture, and LLM integration.</em></p>

  <!-- Badges -->
  <p>
    <img src="https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white" alt="Java" />
    <img src="https://img.shields.io/badge/Spring_Boot-6DB33F?style=for-the-badge&logo=spring-boot&logoColor=white" alt="Spring Boot" />
    <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
    <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" />
    <img src="https://img.shields.io/badge/Stable_Diffusion-8A2BE2?style=for-the-badge&logo=ai&logoColor=white" alt="AI/ML" />
  </p>
</div>

---

## 🎯 Project Overview & MVP Objective
**KuroAI** is a robust, highly scalable web application that transforms textual narratives into breathtaking visual manga panels using Large Language Models (LLMs) and Stable Diffusion. 

This repository serves as a **Minimum Viable Product (MVP)** showcasing production-ready software engineering principles. It was meticulously designed to demonstrate expertise across modern technology stacks, specifically aligning with full-stack enterprise development requirements:
- **Backend Engineering**: Robust REST APIs built with **Java and Spring Boot**, featuring secure JWT authentication and JPA-driven database management.
- **Frontend Development**: A dynamic, highly interactive **React.js** application leveraging modern hooks, TypeScript, and Framer Motion for a premium user experience.
- **Microservices Architecture**: A decoupled system where a Spring Boot API Gateway securely proxies heavy computational tasks to an isolated Python (FastAPI) AI generation service.
- **AI/ML Integration**: Practical implementation of LLMs for autonomous narrative parsing and Image generation models for asset creation.

---

## 🏗️ Architecture & Technical Stack

KuroAI operates on a resilient multi-stage architecture designed to handle large datasets and heavy compute operations:

### 1. The Core Backend (Java & Spring Boot)
- **Role**: API Gateway, Authentication Provider, and Business Logic Handler.
- **Tech**: Java 17, Spring Boot 3, Spring Security, Spring Data JPA.
- **Features**:
  - Stateless **JWT-based Authentication** system (`AuthTokenFilter`, `JwtUtils`).
  - Secure REST API endpoints with cross-origin resource sharing (CORS) configurations.
  - Object-Oriented design utilizing Data Transfer Objects (DTOs), payload validation, and clean controller/service/repository layers.

### 2. The AI Generation Service (Python & FastAPI)
- **Role**: Specialized microservice for handling LLM and ML model executions.
- **Tech**: Python 3.9+, FastAPI, Uvicorn.
- **Features**:
  - `KuroAIOrchestrator`: Parses user prompts, orchestrates LLM scene planning, and executes Stable Diffusion rendering.
  - Designed to be horizontally scalable independent of the main Spring Boot gateway.

### 3. The Frontend Client (React & TypeScript)
- **Role**: The immersive, user-facing application.
- **Tech**: React.js, TypeScript, Vite, Framer Motion.
- **Features**:
  - Highly modularized component structure prioritizing reusability.
  - Interactive Canvas for the "Template Builder" to manipulate generated assets.
  - Dynamic, scroll-linked animations and modern glassmorphism aesthetics.

---

## 🚀 Future Roadmap for Production-Level Scale

To transition KuroAI from an MVP to a highly scalable, enterprise-grade DevSecOps platform, the following architectural enhancements are planned:

1. **DevSecOps CI/CD Pipelines**
   - Implement **GitHub Actions / Jenkins** for automated testing, linting, and continuous deployment.
   - Integrate static application security testing (SAST) to ensure code robustness.
2. **Metadata-Aware Version Control for Assets**
   - Build a unique versioning system allowing users to branch, merge, and rollback specific edits to their generated manga panels and stories.
3. **Event-Driven AI Processing (Kafka/RabbitMQ)**
   - Decouple the AI generation from synchronous REST calls. Implement a message broker to queue heavy generation tasks, significantly improving application resilience and scalability under heavy load.
4. **Distributed Caching (Redis)**
   - Cache frequently used LLM prompts and generated image datasets to optimize performance and reduce compute costs.
5. **OAuth2 & Role-Based Access Control (RBAC)**
   - Enhance the Spring Security layer to support enterprise identity providers (SSO) and granular role management.

---

## 🛠️ Quick Start Guide

### 1. Spring Boot Backend Setup
Ensure Java 17 is installed. The backend uses an H2 in-memory database for zero-config local testing.
```bash
cd backend
./mvnw spring-boot:run
```

### 2. Python AI Service Setup
Ensure Python 3.9+ is installed.
```bash
cd api
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. React Frontend Setup
Ensure Node.js v18+ is installed.
```bash
cd frontend
npm install
npm run dev
```
Navigate to `http://localhost:5173` to experience KuroAI.

---
<div align="center">
  <i>Engineered to demonstrate scalable, secure, and modern software development practices.</i><br>
  Built by <b>Sachin Pandey</b>
</div>
