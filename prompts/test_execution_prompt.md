You are an expert in mobile app testing and Google Cloud Platform. Your task is to generate a comprehensive bash script that will run the Firebase Test Lab Robo test using the gcloud CLI. The script should use the previously generated Robo script and be flexible to allow for customization of various test parameters.

Consider the following aspects when generating the script:
1. The script should accept command-line arguments for customization (e.g., APK path, device model, Android version, locale, orientation).
2. Include error checking and validation for the input parameters.
3. Provide clear comments explaining each step of the script.
4. Include options for running the test on multiple device configurations.
5. Add functionality to save the test results in a specified directory.
6. Implement logging to track the progress and any potential issues during test execution.
7. Incorporate the provided Robo script into the test execution command.

Use the following information as context for generating the script:
- App under test: {use_case}
- Generated Robo script (to be saved as robo_script.json):
```json
{robo_script}
```

Generate a bash script that incorporates these requirements, uses the provided Robo script, and provides a robust solution for running Firebase Test Lab Robo tests. Include a step to save the Robo script to a file before executing the test.


To run the generated Robo script using the gcloud CLI, follow these steps:

Save the generated JSON script to a file (e.g., robo_script.json).
Make sure you have the latest version of the gcloud CLI installed and configured.
Run the following command in your terminal:
gcloud firebase test android run \
    --type robo \
    --app path/to/your/app.apk \
    --robo-script path/to/robo_script.json \
    --device model=MODEL_ID,version=VERSION_ID,locale=LOCALE,orientation=ORIENTATION

Replace the placeholders with your specific values:

path/to/your/app.apk: The path to your Android app's APK file.
path/to/robo_script.json: The path to the saved Robo script JSON file.
MODEL_ID: The device model you want to test on (e.g., "Pixel2").
VERSION_ID: The Android version to test on (e.g., "28").
LOCALE: The locale to use for testing (e.g., "en_US").
ORIENTATION: The screen orientation for testing ("portrait" or "landscape").
You can add multiple --device flags to run the test on different device configurations.