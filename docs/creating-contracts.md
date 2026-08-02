# Creating Contracts

Contracts reside in `backend/contracts` and define immutable Pydantic models.

Rules:
1. May NOT import from `engine/`, `agents/`, or `inference/`.
2. Must inherit from Pydantic `BaseModel`.
