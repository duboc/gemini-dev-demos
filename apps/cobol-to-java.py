import streamlit as st
import os
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part

# Initialize Vertex AI
PROJECT_ID = os.environ.get("GCP_PROJECT")
LOCATION = os.environ.get("GCP_REGION")
vertexai.init(project=PROJECT_ID, location=LOCATION)

def get_gemini_response(prompt, model_name="gemini-1.5-pro-001"):
    model = GenerativeModel(model_name)
    response = model.generate_content(prompt)
    return response.text

st.title("COBOL to Java Migration Demo using Gemini")

cobol_code = """
IDENTIFICATION DIVISION.
PROGRAM-ID.  CPSEQFR.
ENVIRONMENT DIVISION.
INPUT-OUTPUT SECTION.
FILE-CONTROL.
    SELECT INFILE ASSIGN  TO 'INFILE1'
           FILE STATUS IS INPUT-FILE-STATUS.
    SELECT OUTFILE ASSIGN TO 'OUTFILE1'
        FILE STATUS IS OUTPUT-FILE-STATUS.
DATA DIVISION.
FILE SECTION.
FD  INFILE
    LABEL RECORDS ARE STANDARD
    DATA RECORD IS INPUT-RECORD
    RECORD CONTAINS 40 CHARACTERS
    RECORDING MODE IS F
    BLOCK CONTAINS 0 RECORDS.
01  INPUT-RECORD.
    05 INPUT-FIRST-10      PIC X(10).
    05 INPUT-LAST-30       PIC X(30).

FD  OUTFILE
    LABEL RECORDS ARE STANDARD
    DATA RECORD IS OUTPUT-RECORD
    RECORD CONTAINS 40 CHARACTERS
    RECORDING MODE IS F
    BLOCK CONTAINS 0 RECORDS.
01  OUTPUT-RECORD.
    05 OUTPUT-FIRST-30     PIC X(30).
    05 OUTPUT-LAST-10      PIC X(10).

WORKING-STORAGE SECTION.
01  WorkAreas.
    05  INPUT-FILE-STATUS  PIC X(02).
        88  GOOD-READ      VALUE '00'.
        88  END-OF-INPUT   VALUE '10'.
    05  OUTPUT-FILE-STATUS PIC X(02).
        88  GOOD-WRITE     VALUE '00'.
    05  RECORD-COUNT       PIC S9(5) COMP-3.

PROCEDURE DIVISION.
    OPEN INPUT INFILE
    IF NOT GOOD-READ
        DISPLAY 'STATUS ON INFILE OPEN: ' INPUT-FILE-STATUS
        GO TO END-OF-PROGRAM
    END-IF
    OPEN OUTPUT OUTFILE
    IF NOT GOOD-WRITE
        DISPLAY 'STATUS ON OUTFILE OPEN: ' OUTPUT-FILE-STATUS
    END-IF
    PERFORM UNTIL END-OF-INPUT
        READ INFILE
        IF GOOD-READ
            MOVE INPUT-FIRST-10 TO OUTPUT-LAST-10
            MOVE INPUT-LAST-30 TO OUTPUT-FIRST-30
            WRITE OUTPUT-RECORD
            IF GOOD-WRITE
                 ADD 1 TO RECORD-COUNT
            ELSE
                DISPLAY 'STATUS ON OUTFILE WRITE: '
                        OUTPUT-FILE-STATUS
                GO TO END-OF-PROGRAM
            END-IF
        END-IF
    END-PERFORM
    .
END-OF-PROGRAM.
    DISPLAY 'NUMBER OF RECORDS PROCESSED: ' RECORD-COUNT
    CLOSE INFILE
    CLOSE OUTFILE
    GOBACK.
"""

if 'step_results' not in st.session_state:
    st.session_state.step_results = {}

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Original COBOL Code")
    st.code(cobol_code, language="cobol")

with col2:
    st.subheader("Migration Steps")

    steps = [
        ("Generate Java Classes", "Generate Java classes from the COBOL data structures"),
        ("Translate File I/O", "Translate COBOL file I/O to Java file handling"),
        ("Migrate Business Logic", "Migrate COBOL business logic to Java"),
        ("Convert Conditionals", "Convert COBOL conditionals and loops to Java"),
        ("Replace Functions", "Replace COBOL-specific functions with Java equivalents"),
        ("Generate Constants", "Generate Java constants from COBOL copybooks"),
        ("Update Variables", "Update variable names to Java conventions")
    ]

    for i, (step, description) in enumerate(steps, 1):
        with st.expander(f"Step {i}: {step}", expanded=True):
            if st.button(f"Execute Step {i}", key=f"button_{i}"):
                prompt = f"{description} for the following COBOL code:\n{cobol_code}\n\nIf there's existing Java code, use it as a base:\n{st.session_state.step_results.get(step, '')}"
                result = get_gemini_response(prompt)
                st.session_state.step_results[step] = result
            
            if step in st.session_state.step_results:
                st.code(st.session_state.step_results[step], language="java")

    with st.expander("Step 8: Generate Final Java Code", expanded=True):
        if st.button("Generate Final Java Code"):
            all_steps = "\n\n".join(st.session_state.step_results.values())
            prompt = f"Combine and refine all the following Java code snippets into a single, coherent Java program:\n\n{all_steps}"
            final_code = get_gemini_response(prompt)
            st.session_state.final_code = final_code

        if 'final_code' in st.session_state:
            st.code(st.session_state.final_code, language="java")

    if st.button("Reset"):
        st.session_state.step_results = {}
        if 'final_code' in st.session_state:
            del st.session_state.final_code
        st.rerun()