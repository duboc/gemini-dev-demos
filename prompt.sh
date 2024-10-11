#!/bin/bash

mkdir -p prompts

# Create video_description_prompt.md
cat << EOF > prompts/video_description_prompt.md
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
EOF

# Create appium_script_prompt.md
cat << EOF > prompts/appium_script_prompt.md
All the answers are to be provided in {language}
You are analyzing a video recording of a user interacting with the {use_case} mobile application. Your task is to generate an Appium script in Python that reproduces the steps shown in the video.

Use the following video description as a reference for the user interactions:
{st.session_state['video_description']}

Focus on the following key areas:
1. Setting up the Appium driver with appropriate capabilities
2. Implementing each user action (taps, swipes, text input) using Appium commands
3. Using appropriate locator strategies (id, xpath, accessibility id) based on the Element Identifier column
4. Adding appropriate waits and assertions to ensure reliable test execution
5. Handling any potential errors or exceptions

Deliverable:
Appium Python Script:
- Start with importing necessary libraries and setting up the Appium driver
- Implement each action from the video description using appropriate Appium commands
- Add comments to explain the purpose of each action
- Include error handling and cleanup (quitting the driver) at the end of the script

Here's an example structure for the Appium script:

\`\`\`python
from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up desired capabilities
desired_caps = {
    'platformName': 'Android',
    'deviceName': 'Android Emulator',
    'app': '/path/to/your/app.apk',
    # Add other necessary capabilities
}

# Initialize the Appium driver
driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

try:
    # Implement user actions here
    # Example:
    # Find and click on the search bar
    search_bar = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((MobileBy.ID, "search_bar"))
    )
    search_bar.click()
    
    # Type "running shoes" into the search input
    search_input = driver.find_element(MobileBy.ID, "search_input")
    search_input.send_keys("running shoes")
    
    # Click the search button
    search_button = driver.find_element(MobileBy.ID, "search_button")
    search_button.click()
    
    # Add more actions based on the video description
    
except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Quit the driver
    driver.quit()
\`\`\`

Generate an Appium script that accurately reproduces the user interactions from the video description. Use appropriate Appium commands, locator strategies, and error handling.

Provide a brief summary of the script's coverage and any potential areas that may require manual testing or additional instrumentation.
EOF

echo "Prompts have been split into separate files in the 'prompts' directory."