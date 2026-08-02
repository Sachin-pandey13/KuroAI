import argparse
import base64
import os

from pipeline.orchestrator import KuroAIOrchestrator


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True)
    args = parser.parse_args()

    app = KuroAIOrchestrator()
    result = app.run(args.prompt)

    print(f"\nGenerated manga: {result['title']}\n")

    os.makedirs("outputs", exist_ok=True)

    for i, img in enumerate(result["images"]):

        # remove "data:image/png;base64,"
        if img.startswith("data:image"):
            img = img.split(",", 1)[1]

        image_bytes = base64.b64decode(img)

        path = f"outputs/panel_{i}.png"
        with open(path, "wb") as f:
            f.write(image_bytes)

        print("Saved:", path)


if __name__ == "__main__":
    main()
