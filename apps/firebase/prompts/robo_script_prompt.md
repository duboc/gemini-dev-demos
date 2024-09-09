All the answers are to be provided in {language}
You are analyzing a video recording of a user interacting with the {use_case} mobile application. Your task is to generate a Robo script for Firebase Test Lab that reproduces the steps shown in the video. The script should be in JSON format and follow the Firebase Test Lab Robo Script specifications.

Use the following video description as a reference for the user interactions:
{video_description}

Focus on the following key areas:
1. Identifying and describing each user action (taps, swipes, text input)
2. Specifying the exact elements interacted with (using resource IDs or text when available)
3. Determining the correct order of actions
4. Including any necessary waits or assertions

Deliverable:
Firebase Test Lab Robo Script (JSON format):
- Each action should be represented as a separate object in the JSON array
- Include the type of action (e.g., "click", "text", "swipe")
- Specify the target element using resource ID, text, or coordinates as appropriate
- Add comments to explain the purpose of each action

Generate a Robo script that accurately reproduces the user interactions from the video description. Use appropriate event types, element descriptors, and other attributes as needed. If you're unsure about specific resource IDs, use descriptive placeholders.

Provide a brief summary of the script's coverage and any potential areas that may require manual testing or additional instrumentation.