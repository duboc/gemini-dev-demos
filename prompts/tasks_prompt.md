All the answers are required to be in {story_lang} and to stick to the persona. 
                Divide the user story into tasks as granular as possible. 
                The goal of fragmenting a user story is to create a list of tasks that can be completed within a sprint. 
                Therefore, it is important to break down the story into minimal tasks that still add value to the end user. 
                This facilitates progress tracking and ensures that the team stays on track.
                Create a table with the tasks as the table index with the task description.
                Based on the image analysis results, generate a list of tasks for implementing the described functionality. Break down the tasks into small, manageable units that can be completed within a sprint.

                Present the tasks in a table format with the following columns:
                    1. Task ID
                    2. Task Description
                    3. Estimated Effort (in hours)
                    4. Priority (High, Medium, Low)
                    5. Requires Code (Yes/No)

                Example of an output:

                    Task Breakdown for Transcription Application
                    Task ID	Task Description	Estimated Effort (hours)	Priority	Requires Code
                    UI-1	Design and implement the main user interface for audio recording and displaying transcription results.	8	High	Yes
                    UI-2	Implement UI elements for selecting transcription modes (Real-time, Flash, Pro).	4	High	Yes
                    UI-3	Design and implement UI for displaying analysis results from Gemini Pro.	6	Medium	Yes
                    BE-1	Implement backend logic for handling audio recording and streaming.	6	High	Yes
                    BE-2	Integrate Google Speech-to-Text API for real-time transcription.	4	High	Yes
                    BE-3	Integrate Gemini Flash 1.5 API for enhanced transcription.	8	Medium	Yes
                    BE-4	Integrate Gemini Pro 1.5 API for insights and summaries generation.	12	Medium	Yes
                    API-1	Define and implement API endpoints for communication between frontend and backend.	8	High	Yes
                    DB-1	Design BigQuery schema for storing transcribed text and analysis results.	4	Medium	No
                    DB-2	Implement data pipeline from application to BigQuery using Dataflow.	16	Medium	Yes
                    DP-1	Implement logic for processing real-time transcriptions.	6	High	Yes
                    DP-2	Implement logic for processing flash transcriptions.	8	Medium	Yes
                    DP-3	Implement logic for processing pro transcriptions.	12	Medium	Yes
                    T-1	Write unit tests for backend logic.	8	High	Yes
                    T-2	Write integration tests for API endpoints.	6	High	Yes
                    T-3	Write end-to-end tests for the application flow.	12	Medium	Yes
                    QA-1	Perform user acceptance testing.	4	High	No
                    DOC-1	Document API endpoints and data models.	4	Medium	No
                    DOC-2	Create user documentation for the application.	8	Low	No
                    R-1	Research and document the cost implications of using Google Cloud services.	4	Low	No
                    ERR-1	Implement error handling and retry mechanisms for API calls.	6	High	Yes
                    ERR-2	Implement error handling for data pipeline to BigQuery.	4	Medium	Yes
                    SEC-1	Implement security measures for data privacy and access control.	8	High	Yes
                