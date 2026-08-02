import argparse
import base64
import os
import sys

try:
    from pipeline.orchestrator import KuroAIOrchestrator
except ImportError:
    KuroAIOrchestrator = None  # type: ignore[assignment, misc]


def main():
    if KuroAIOrchestrator is None:
        print("Error: Legacy pipeline.orchestrator module is unavailable in this environment.")
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True)
    args = parser.parse_args()

    app = KuroAIOrchestrator()
    result = app.run(args.prompt)

    print("Pipeline Output:")
    print("Script:", result["script"])
    print("Pages generated:", len(result["pages"]))
    print("Saved image files:")

    os.makedirs("outputs", exist_ok=True)

    for idx, img_b64 in enumerate(result["images"]):
        out_path = f"outputs/panel_{idx+1}.png"
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(img_b64))
        print(f" - {out_path}")


if __name__ == "__main__":
    main()
