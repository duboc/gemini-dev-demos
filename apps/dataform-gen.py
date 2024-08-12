import streamlit as st 
import utils_vertex as vertex
import json

def load_sample_schema():
    sample_schema = [
        {
            "name": "billing_account_id",
            "mode": "NULLABLE",
            "type": "STRING",
            "description": "",
            "fields": []
        },
        {
            "name": "service",
            "mode": "NULLABLE",
            "type": "RECORD",
            "description": "",
            "fields": [
                {"name": "id", "mode": "NULLABLE", "type": "STRING", "description": "", "fields": []},
                {"name": "description", "mode": "NULLABLE", "type": "STRING", "description": "", "fields": []}
            ]
        },
        {
            "name": "sku",
            "mode": "NULLABLE",
            "type": "RECORD",
            "description": "",
            "fields": [
                {"name": "id", "mode": "NULLABLE", "type": "STRING", "description": "", "fields": []},
                {"name": "description", "mode": "NULLABLE", "type": "STRING", "description": "", "fields": []}
            ]
        },
        {
            "name": "usage_start_time",
            "mode": "NULLABLE",
            "type": "TIMESTAMP",
            "description": "",
            "fields": []
        },
        {
            "name": "usage_end_time",
            "mode": "NULLABLE",
            "type": "TIMESTAMP",
            "description": "",
            "fields": []
        },
        {
            "name": "project",
            "mode": "NULLABLE",
            "type": "RECORD",
            "description": "",
            "fields": [
                {"name": "id", "mode": "NULLABLE", "type": "STRING", "description": "", "fields": []},
                {"name": "number", "mode": "NULLABLE", "type": "STRING", "description": "", "fields": []},
                {"name": "name", "mode": "NULLABLE", "type": "STRING", "description": "", "fields": []},
                {
                    "name": "labels",
                    "mode": "REPEATED",
                    "type": "RECORD",
                    "description": "",
                    "fields": [
                        {"name": "key", "mode": "NULLABLE", "type": "STRING", "description": "", "fields": []},
                        {"name": "value", "mode": "NULLABLE", "type": "STRING", "description": "", "fields": []}
                    ]
                },
                {"name": "ancestry_numbers", "mode": "NULLABLE", "type": "STRING", "description": "", "fields": []},
                {
                    "name": "ancestors",
                    "mode": "REPEATED",
                    "type": "RECORD",
                    "description": "",
                    "fields": [
                        {"name": "resource_name", "mode": "NULLABLE", "type": "STRING", "description": "", "fields": []},
                        {"name": "display_name", "mode": "NULLABLE", "type": "STRING", "description": "", "fields": []}
                    ]
                }
            ]
        },
        {
            "name": "labels",
            "mode": "REPEATED",
            "type": "RECORD",
            "description": "",
            "fields": [
                {"name": "key", "mode": "NULLABLE", "type": "STRING", "description": "", "fields": []},
                {"name": "value", "mode": "NULLABLE", "type": "STRING", "description": "", "fields": []}
            ]
        },
        {
            "name": "system_labels",
            "mode": "REPEATED",
            "type": "RECORD",
            "description": "",
            "fields": [
                {"name": "key", "mode": "NULLABLE", "type": "STRING", "description": "", "fields": []},
                {"name": "value", "mode": "NULLABLE", "type": "STRING", "description": "", "fields": []}
            ]
        },
        {
            "name": "location",
            "mode": "NULLABLE",
            "type": "RECORD",
            "description": "",
            "fields": [
                {"name": "location", "mode": "NULLABLE", "type": "STRING", "description": "", "fields": []},
                {"name": "country", "mode": "NULLABLE", "type": "STRING", "description": "", "fields": []},
                {"name": "region", "mode": "NULLABLE", "type": "STRING", "description": "", "fields": []},
                {"name": "zone", "mode": "NULLABLE", "type": "STRING", "description": "", "fields": []}
            ]
        },
        {
            "name": "resource",
            "mode": "NULLABLE",
            "type": "RECORD",
            "description": "",
            "fields": [
                {"name": "name", "mode": "NULLABLE", "type": "STRING", "description": "", "fields": []},
                {"name": "global_name", "mode": "NULLABLE", "type": "STRING", "description": "", "fields": []}
            ]
        },
        {
            "name": "tags",
            "mode": "REPEATED",
            "type": "RECORD",
            "description": "",
            "fields": [
                {"name": "key", "mode": "NULLABLE", "type": "STRING", "description": "", "fields": []},
                {"name": "value", "mode": "NULLABLE", "type": "STRING", "description": "", "fields": []},
                {"name": "inherited", "mode": "NULLABLE", "type": "BOOLEAN", "description": "", "fields": []},
                {"name": "namespace", "mode": "NULLABLE", "type": "STRING", "description": "", "fields": []}
            ]
        },
        {
            "name": "cost",
            "mode": "NULLABLE",
            "type": "FLOAT",
            "description": "",
            "fields": []
        },
        {
            "name": "currency",
            "mode": "NULLABLE",
            "type": "STRING",
            "description": "",
            "fields": []
        },
        {
            "name": "usage",
            "mode": "NULLABLE",
            "type": "RECORD",
            "description": "",
            "fields": [
                {"name": "amount", "mode": "NULLABLE", "type": "FLOAT", "description": "", "fields": []},
                {"name": "unit", "mode": "NULLABLE", "type": "STRING", "description": "", "fields": []},
                {"name": "amount_in_pricing_units", "mode": "NULLABLE", "type": "FLOAT", "description": "", "fields": []},
                {"name": "pricing_unit", "mode": "NULLABLE", "type": "STRING", "description": "", "fields": []}
            ]
        }
    ]
    return json.dumps(sample_schema, indent=2)

def generate_example_questions(schema):
    prompt = f"""
    Given the following JSON schema for a billing dataset:

    {schema}

    Generate three insightful questions that a user might ask about their billing data in Google Cloud. 
    The questions should be diverse and cover different aspects of the schema.
    Return only the questions, one per line, without any additional text or numbering.
    """
    response = vertex.sendPrompt(prompt, vertex.model_gemini_pro)
    return [q.strip() for q in response.split('\n') if q.strip()]

# Initialize session state variables
if 'dataform_sql' not in st.session_state:
    st.session_state.dataform_sql = ""
if 'example_questions' not in st.session_state:
    st.session_state.example_questions = []

st.header("Dataform ELT Generator :bar_chart:")
st.markdown(" **Effortless BigQuery Table Deployment: Schema-to-SQLx-to-Terraform with Gemini**")
st.markdown("Transform your ELT using BigQuery with table creation workflow with Gemini's AI-powered capabilities. \
Simply provide your table schema, and Gemini will generate:")
st.markdown("- SQLx Code: Precise Rust code using SQLx to efficiently implement your desired transformations \
or data loading logic.")
st.markdown("- Terraform Configuration: A ready-to-use Terraform file to create the \
corresponding BigQuery table, complete with schema definition and data loading steps leveraging the generated SQLx code.")


# Step 1: Schema Input
st.subheader("Step 1: Enter Your Schema")

schema_option = st.radio(
    "Choose schema input method:",
    ("Upload your own schema", "Use sample billing schema")
)

if schema_option == "Upload your own schema":
    uploaded_file = st.file_uploader("Upload JSON schema file", type="json")
    if uploaded_file is not None:
        schema = uploaded_file.getvalue().decode("utf-8")
    else:
        schema = ""
else:
    schema = load_sample_schema()

with st.expander("View/Edit Schema"):
    schema = st.text_area("Schema (JSON format)", value=schema, height=400)

# Step 2: Custom Question Input and Dataform SQL Generation
st.subheader("Step 2: Generate Dataform SQL")
st.write("Example Questions when using the Simple Billing Schema:")

# Generate example questions only if they haven't been generated yet
if not st.session_state.example_questions:
    st.session_state.example_questions = generate_example_questions(schema)

for question in st.session_state.example_questions:
    st.write("- " + question)

custom_question = st.text_input("Enter your question about the schema:")

if st.button("Generate Dataform SQL"):
    with st.spinner("Generating Dataform SQL..."):
        dataform_prompt = f"Given the following table schema in JSON format: \n{schema} \
        generate a SQLx query for Dataform to answer the question: {custom_question} \
        generate a step-by-step guide to include the sqlx inside Dataform's paths i.e *definitions \
        Make the following assumptions: \
        * Assume that the user is trying to generate an ELT using the {schema} that is not stored in Bigquery yet \
        * Generate a step by step guide to conver the {schema} that is in JSON, to a CSV to be stored in a Bigquery table \
        * Assume that the only table the user has is the {schema}, so do not include any JOIN \
        * If the question involves filtering by date or time, assume the relevant column exists in the table from the schema provided and is named 'date' or 'timestamp' (choose the most appropriate one based on the schema).    "  

        dataform_input = schema + "\n" + dataform_prompt
        st.session_state.dataform_sql = vertex.sendPrompt(dataform_input, vertex.model_gemini_pro)

if st.session_state.dataform_sql:
    with st.expander("View Generated Dataform SQL"):
        st.write(st.session_state.dataform_sql, language="sql")

# Step 3: Terraform Generation
st.subheader("Step 3: Generate Terraform")

# Specific inputs for Terraform variables
dataform_workspace_id = st.text_input("Dataform Workspace ID:")
dataform_project_id = st.text_input("Project ID:")
dataform_action_name = st.text_input("Dataform Name:")
bigquery_dataset = st.text_input("Bigquery Dataset:")
bigquery_table = st.text_input("Bigquery Table:")


if st.button("Generate Terraform"):
    if not st.session_state.dataform_sql:
        st.error("Please generate Dataform SQL in Step 2 before generating Terraform.")
    else:
        with st.spinner("Generating Terraform..."):
            terraform_prompt = f"""
            Create two bash scripts. One to get the output from the {st.session_state.dataform_sql} and transform this as an input for the next bash
            Now generate a bash with gcloud code to facilitate a deploy in Bigquery using the following Dataform SQL: \
            {st.session_state.dataform_sql} \
            Use the following variables provided by the user in your gcloud code: \
            - Dataform Workspace Name: {dataform_workspace_id} \
            - Google Cloud Project ID:{dataform_project_id} \
            - Dataform Name: {dataform_action_name} \
            - Bigquery Dataset Name: {bigquery_dataset} \
            - Bigquery Table Name: {bigquery_table} \
            * Please include a table creation in Bigquery to match the Dataform SQL generated code \

        
            Use only the following reference for the dataform cli generation

            Dataform CLI commands
                The open-source Dataform CLI provides commands to initialize, compile, test, and run Dataform core locally, outside of Google Cloud.

                Dataform CLI command	Description
                dataform help	Shows help for all Dataform CLI commands.
                dataform help [command]	Shows help for the specified command.
                dataform init [project-dir]	Creates a new Dataform project.
                dataform install [project-dir]	Installs NPM dependencies for the specified Dataform project.
                dataform init-creds [project-dir]	Creates a .df-credentials.json file for Dataform to use when accessing Google Cloud APIs.
                dataform compile [project-dir]	Compiles the specified Dataform project. Produces JSON output describing the non-executable graph.
                dataform test [project-dir]	Runs the specified Dataform project's unit tests on BigQuery.
                dataform run [project-dir]	Runs the specified Dataform project's scripts on BigQuery.
                dataform format [project-dir]	Formats the specified Dataform project's files.
                --help	Shows help [boolean].
                --version	Shows the version number of the Dataform CLI [boolean].
            
            """
            print(terraform_prompt)
            terraform_response = vertex.sendPrompt(terraform_prompt, vertex.model_gemini_pro)

            if terraform_response:
                with st.expander("View Generated Terraform Code"):
                    st.write(terraform_response, language="hcl")

st.info("Note: The generated Dataform SQL and Terraform code are based on AI predictions and may require review and adjustments.")