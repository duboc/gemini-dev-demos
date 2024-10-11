All the answers are to be provided in {language}
You are analyzing a video recording of a user interacting with the {use_case} mobile application. 
Your task is to describe the video step by step, including timestamps for each action. 
Focus on user interactions, screen transitions, and any notable events in the user interface.

Format your response as a markdown table with the following columns:
| Timestamp | Action | Description | Element Identifier |

For example:
| Timestamp | Action | Description | Element Identifier |
|-----------|--------|-------------|---------------------|
| 0:05 | Tap | User taps on the search bar | id="search_bar" |
| 0:08 | Type | User types "running shoes" | id="search_input" |
| 0:12 | Tap | User taps the search button | id="search_button" |

Provide a comprehensive description of the entire video using this table format.
For the Element Identifier column, use your best guess for appropriate IDs, class names, or XPaths.
