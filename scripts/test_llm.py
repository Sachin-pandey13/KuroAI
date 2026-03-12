from inference.llm_planner import StoryPlannerLLM

planner = StoryPlannerLLM()
story = planner.generate_story_plan("A lonely cyberpunk boy walking through neon rain")
print(story)
