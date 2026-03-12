from pipeline.orchestrator import KuroAIOrchestrator

if __name__ == "__main__":
    idea = "A dark cyberpunk revenge story set in a neon city"
    app = KuroAIOrchestrator()
    result = app.run(idea)

    print(f"Generated manga: {result['title']}")
    for img in result["images"]:
        print(img["image_path"])
