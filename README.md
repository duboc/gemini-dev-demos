# Gemini developer lifecycle demos

This repository contains 13 interactive [Streamlit](https://streamlit.io/) demos
that call Google's Gemini models through
[Vertex AI](https://cloud.google.com/vertex-ai/docs). Each demo applies a Gemini
model to one stage of the software development lifecycle: inspecting a
codebase, migrating legacy code, generating test scripts from screen
recordings, reviewing user experience and accessibility, turning user stories
into code, and generating data pipelines.

The demos target developers, solution architects, and technical presenters who
want runnable examples of AI-assisted engineering. Treat the code as
demonstration material that you read, run, and adapt, not as production
software.

![Animated Gemini logo](images/gemini_gif.gif)

## Before you begin

Install and configure the following:

- Python 3.12. The container image in `Dockerfile` builds on `python:3.12`, so
  use the same version locally to match it.
- A Google Cloud project with billing enabled.
- The [Google Cloud CLI](https://cloud.google.com/sdk/docs/install),
  authenticated against that project.
- [Docker](https://docs.docker.com/get-started/get-docker/), if you plan to
  build the container image or deploy to Cloud Run.

Enable these APIs in your project. The `setup.sh` script enables all of them for
you:

- `aiplatform.googleapis.com`
- `cloudbuild.googleapis.com`
- `run.googleapis.com`
- `artifactregistry.googleapis.com`
- `iam.googleapis.com`
- `storage-api.googleapis.com`

### Gemini model identifiers

`utils_vertex.py` holds every Gemini identifier this repository sends to
Vertex AI, in two module-level constants. No file under `apps/` carries a
model literal of its own: every demo imports `MODEL_ID`, and a demo that
offers a model picker lists that one identifier, so a single edit reaches all
13 demos.

| Identifier | Constant in `utils_vertex.py` | Availability on Vertex AI |
| --- | --- | --- |
| `gemini-3.8-flash` | `MODEL_ID` | Listed under "Models available for shorter availability periods", a tier whose members retire 45 days after Google ships a replacement. The page states no fixed date. |
| `gemini-embedding-001` | `EMBEDDING_MODEL_ID` | Listed among the embeddings models Vertex AI serves. No demo calls it, so the constant names the model an embedding feature would reach for. |

Both identifiers come from
[Model versions and lifecycle](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/model-versioning),
the page that states which models Vertex AI serves and for how long. Read it
again before you trust either one. A 45-day window is short enough that a
checkout a few months old can name a model the API no longer answers, and
Vertex AI responds to a retired identifier with a not-found error rather than
a fallback.

The same page dates the end of service for `gemini-embedding-001` no sooner
than May 20, 2028, so the embedding constant carries far more runway than the
generation one. That row sits in the "Embeddings models" table, which the page
shows without a click.

Dates for models Vertex AI already retired sit one level down, inside the
expander labeled "The following table lists the retired models (click to
expand)", so open the expander before you look for one of those.
`check_readme.py` rejects a date that its transcription of these tables does
not carry.

`gemini-3.8-flash` handles every prompt in this repository, including the ones
that send a video or an image. That is a change from the earlier layout, where
`utils_vertex.py` exported five model objects and the demos picked among
three. Those objects, and the image generation and multimodal embedding models
that sat beside them, are gone.

Vertex AI serves that model only on the `global` endpoint. A run against a
live project sent one generation call per endpoint and got an answer from
`global` and a 404 from `us-central1`, `us-east5`, `southamerica-east1`,
`us-east1`, `us-south1`, and `europe-southwest1`. Every other Gemini 3.x flash
identifier behaved the same way, and only the previous model generation, which
this repository does not pin, answered regionally. The module docstring in
`utils_vertex.py` dates that run. Five demos used to offer a region picker;
every option it listed now fails, so the picker is gone and each of those
pages states the endpoint instead.

### Key dependencies

`requirements.txt` lists 15 direct dependencies. The demos depend most
directly on these packages:

- `streamlit` renders every demo page.
- `google-genai` carries every Gemini call, in Vertex AI mode.
- `GitPython` clones the repository that the repository inspection demo
  analyzes.
- `magika` classifies the file types that the same demo reads.
- `pandas` builds the token usage table that the same demo shows.

That list is neither complete nor fully pinned, so two installs from the same
`requirements.txt` can give you different code.

`apps/repo-inspection.py` imports `pandas` to build that table. The manifest
names `pandas` directly, so the demo survives a later `streamlit` release that
drops it.

`requirements.txt` does not list `nltk`, `nbconvert`, `nbformat`, or `PyPDF2`.
No source file imports them, and between them they carried most of the
security advisories this repository reported, including four that no release
fixes.

No source file imports `tqdm` either, but `magika` depends on it, so every
install pulls it in. The `tqdm>=4.66.3` line holds that dependency above the
version the advisory covers, which a reinstall over an older environment
otherwise keeps.

Eight of the 15 lines carry no version constraint, among them `streamlit`,
`google-genai`, and `pandas`. Pin them before you depend on a build that has
to keep working.

## Set up your environment

1. Clone the repository and change into it:

   ```bash
   git clone https://github.com/duboc/gemini-dev-demos.git
   cd gemini-dev-demos
   ```

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

1. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

1. Authenticate with application default credentials:

   ```bash
   gcloud auth application-default login
   ```

1. Export the environment variables that the `google-genai` client reads:

   ```bash
   export GOOGLE_CLOUD_PROJECT="my-project"
   export GOOGLE_CLOUD_LOCATION="global"
   export GOOGLE_GENAI_USE_VERTEXAI=true
   ```

   Replace `my-project` with your Google Cloud project ID. Leave the location
   set to `global`. Vertex AI serves the model this repository pins only on
   the global endpoint, and a regional value such as `us-central1` makes every
   call answer with a not-found error. The third variable points the client at
   Vertex AI instead of the Gemini Developer API, which takes an API key.

### Environment variables

No file in this repository calls `os.environ` for any of the first three
variables. The `google-genai` client reads them itself when `get_client()`
constructs it, which is why a typo shows up as an authentication error from
the SDK rather than as a `None` inside a demo.

| Variable | Set or read by | Purpose |
| --- | --- | --- |
| `GOOGLE_CLOUD_PROJECT` | `Dockerfile` and `cloudbuild.yaml` set it, and the `google-genai` client reads it | Google Cloud project that bills and serves the Gemini calls. |
| `GOOGLE_CLOUD_LOCATION` | `Dockerfile` and `cloudbuild.yaml` set it, and the `google-genai` client reads it | Vertex AI endpoint. Both files set it to `global`, the only endpoint that serves the pinned model. No demo overrides it. |
| `GOOGLE_GENAI_USE_VERTEXAI` | `Dockerfile` and `cloudbuild.yaml` set it | Set it to `true` to route the client through Vertex AI and application default credentials. |
| `DEMO_ASSETS_BUCKET` | `Dockerfile` and `setup.sh` set it | Names a Cloud Storage bucket for demo assets. No file in this repository reads the variable, so setting it changes nothing. |
| `STREAMLIT_SERVER_ENABLE_STATIC_SERVING` | `Dockerfile` sets it | Flag that lets Streamlit serve files from a static directory. |

## Run the demos locally

Start the Streamlit server from the repository root:

```bash
streamlit run home.py
```

Streamlit reads `.streamlit/config.toml`, which sets port 8080. Open
`http://localhost:8080` in your browser to use the demos.

`home.py` renders the shell for every demo. Use the **Select a category** list
in the sidebar to pick a category, then click a demo button to load that page.
If the app reports a state error, click **Reset All** in the sidebar to clear
the Streamlit session state.

Every page renders on its own. A page that calls Gemini needs application
default credentials and a project, so run
`gcloud auth application-default login` and export the variables above before
you press a generate button. For the identifiers those calls use, see
[Gemini model identifiers](#gemini-model-identifiers).

## Available demos

Every demo lives in its own file under `apps/` and loads inside the `home.py`
shell. The first column gives the label on the sidebar button that opens the
demo.

| Sidebar button | File | Description |
| --- | --- | --- |
| **Repo Inspection** | `apps/repo-inspection.py` | Clones a Git repository, classifies its files with Magika, generates an analysis of the codebase, and reports the tokens the run consumed. |
| **Image to Code, Test and Deploy** | `apps/code-to-image.py` | Turns an uploaded image of an application screen into a description, backend code, frontend code, deployment commands, test cases, and a Selenium script. |
| **Cobol to Java** | `apps/cobol-to-java.py` | Migrates a COBOL sample to Java in reviewable steps, then merges the steps into one program. |
| **Selenium Automation** | `apps/selenium-automation.py` | Generates a Selenium test script from a video of a user session. |
| **Firebase Robo Script** | `apps/firebase-testlab.py` | Generates a Firebase Test Lab Robo script from a video of an app walkthrough. |
| **Appium Automation** | `apps/appium-automation.py` | Generates an Appium script for mobile testing from a video of an app walkthrough. |
| **UX Heuristic Analysis using Gemini AI** | `apps/ux-heuristics-app.py` | Reviews an interface against usability heuristics and reports the findings. |
| **UX Friction Log Generator** | `apps/ux-frictionlog-app.py` | Produces a friction log from a recording of a user interaction. |
| **Accessibility with Gemini** | `apps/ux-accessibility.py` | Analyzes an interface against WCAG guidance, then turns the findings into accessibility user stories. |
| **User Story to Code** | `apps/generate-story-to-code-generic.py` | Generates a user story, breaks it into tasks, then generates code and a unit test implementation. |
| **User Story to Data** | `apps/generate-story-to-data-generic.py` | Generates a user story, breaks it into tasks, then generates a data warehouse model and a BigQuery implementation. |
| **User Story to API** | `apps/generate-story-to-api-generic.py` | Generates a user story, breaks it into tasks, then generates an OpenAPI specification and an Apigee implementation. |
| **Dataform ELT Generation** | `apps/dataform-gen.py` | Takes a schema that you enter and generates Dataform SQL and the matching Terraform definitions. |

The three user story demos read seed prompts from `data/`. That directory holds
one text file per industry and language, such as `data/retail-en.txt`,
`data/finance-pt.txt`, and `data/health-es.txt`.

`home.py` defines six categories, and the sidebar shows the buttons for the
category you select. The last category, **Others**, repeats the Dataform ELT
generation demo, so the six categories list 14 entries for 13 demo files.

## Repository layout

| Path | Contents |
| --- | --- |
| `home.py` | Streamlit entry point: sidebar, category list, and demo loader. |
| `apps/` | One Python file per demo. |
| `apps/firebase/` | Support modules for the Firebase Robo script demo: `apps/firebase/config.py`, `apps/firebase/generation.py`, and `apps/firebase/ui_components.py`. |
| `apps/firebase/prompts/` | Markdown prompt templates for that demo. |
| `utils_vertex.py` | Shared Gemini access: the `google-genai` client, the model identifiers, the safety settings, and the `sendPrompt()` helper. |
| `utils_streamlit.py` | Helpers that reset Streamlit session state. |
| `snippets/model-request.py` | Minimal example of calling `sendPrompt()`. |
| `data/` | Seed text for the user story demos. |
| `images/` | Logo and animation that the interface displays. |
| `.streamlit/config.toml` | Streamlit server, browser, and theme settings. |
| `Dockerfile` | Container image definition. |
| `cloudbuild.yaml` | Cloud Build pipeline that builds, pushes, and deploys the image. |
| `setup.sh` | One-shot script that enables APIs, creates a bucket and an Artifact Registry repository, and deploys to Cloud Run from source. |
| `check_readme.py` | Verification script for this README. |
| `docs/CONTRIBUTING.md` | Contribution guide. |
| `LICENSE` | Apache License 2.0 text. |

## Run the demos in a container

1. Build the image:

   ```bash
   docker build -t gemini-dev-demos .
   ```

1. Run the container, overriding the placeholder values that `Dockerfile` bakes
   in:

   ```bash
   docker run -p 8080:8080 \
     -e GOOGLE_CLOUD_PROJECT="${GOOGLE_CLOUD_PROJECT}" \
     -e GOOGLE_CLOUD_LOCATION="${GOOGLE_CLOUD_LOCATION}" \
     gemini-dev-demos
   ```

The image exposes port 8080 and starts `streamlit run home.py`. Open
`http://localhost:8080` to use the demos.

The container has no Google Cloud credentials of its own. Mount your
application default credentials into the container or run it on a Google Cloud
service that provides a service identity.

## Deploy to Cloud Run

The repository offers two deployment paths. Both deploy the same application.

### Deploy from source with setup.sh

`setup.sh` enables the required APIs, creates a Cloud Storage bucket, creates an
Artifact Registry repository named `dev-lifecycle`, and deploys a Cloud Run
service named `dev-lifecycle` from source with `DEMO_ASSETS_BUCKET` set to the
new bucket. No demo reads that variable, so the bucket stays empty.

1. Edit `setup.sh` and replace `YOUR_PROJECT_ID` and `YOUR_REGION` with your
   project ID and region.

1. Run the script:

   ```bash
   bash setup.sh
   ```

### Deploy with Cloud Build

1. Create the Artifact Registry repository that `cloudbuild.yaml` expects:

   ```bash
   gcloud artifacts repositories create gemini-dev-demos --repository-format=docker --location=us-central1 --description="Gemini developer lifecycle demos"
   ```

1. Submit the build:

   ```bash
   gcloud builds submit . --config=./cloudbuild.yaml --substitutions SHORT_SHA=1.0
   ```

`cloudbuild.yaml` installs the dependencies, builds the image, pushes it to
Artifact Registry, and deploys it to Cloud Run with `--allow-unauthenticated`
and with `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, and
`GOOGLE_GENAI_USE_VERTEXAI` set on the service.

Override these substitution variables to change the target:

| Substitution | Default | Purpose |
| --- | --- | --- |
| `_ARTIFACT_REGISTRY_REPO` | `gemini-dev-demos` | Artifact Registry repository name. |
| `_REPO_LOCATION` | `us-central1` | Artifact Registry location. |
| `_SERVICE_NAME` | `gemini-re-demos` | Cloud Run service name and image name. |
| `_SERVICE_REGION` | `us-central1` | Cloud Run region. |
| `_VERTEX_LOCATION` | `global` | Vertex AI endpoint the deployed service calls. |

`_SERVICE_REGION` and `_VERTEX_LOCATION` name two different things, and the
pipeline used to pass one value for both. `_SERVICE_REGION` places the
container; `_VERTEX_LOCATION` becomes `GOOGLE_CLOUD_LOCATION` on the service
and picks the Vertex AI endpoint. A service that runs in `us-central1` still
calls the global endpoint, because that is the only endpoint serving the
pinned model. Move the service wherever you like and leave the endpoint alone.

Cloud Build also requires `SHORT_SHA`, which it populates automatically for
trigger-driven builds and which you pass yourself for manual builds.

The build step hardcodes the `us-central1` Artifact Registry host, whereas the
push and deploy steps use `_REPO_LOCATION`. If you change `_REPO_LOCATION`,
update the build step in `cloudbuild.yaml` as well.

## Verify this README

`check_readme.py` checks this README against the repository: the sections it
must contain, referenced paths, demo coverage, sidebar labels, model
identifiers, the Vertex AI endpoint, dated claims, environment variables,
packages, deployment commands, the license statement, and a set of mechanical
style rules. It needs no arguments, no network access, and no Google Cloud
credentials.

```bash
python3 check_readme.py
```

The script prints one line per check and exits with a non-zero status if any
check fails. Run it after you change `README.md` or rename anything it
references.

## Troubleshooting

- **Vertex AI returns a permission or API error.** Confirm that the project
  named by `GOOGLE_CLOUD_PROJECT` has `aiplatform.googleapis.com` turned on,
  and that your credentials carry the Vertex AI User role.
- **The client reports missing credentials or no project.** `get_client()`
  builds the `google-genai` client on the first call, not at import, so a
  missing variable surfaces when you press a generate button rather than when
  the page loads. Run `gcloud auth application-default login`, export
  `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, and
  `GOOGLE_GENAI_USE_VERTEXAI`, then restart the server.
- **A model call returns a not-found error.** Two different causes produce the
  same error. Check the endpoint first: run `echo $GOOGLE_CLOUD_LOCATION` and
  set it to `global` if it names a region, because a region serves no Gemini
  3.x model and changing which region you pick cannot help. If the endpoint is
  already `global`, the identifier is the suspect: Vertex AI serves
  `gemini-3.8-flash` for a short availability window, so confirm it against
  [Gemini model identifiers](#gemini-model-identifiers).
- **A repository inspection run exhausts memory.** `apps/repo-inspection.py`
  loads a whole repository into the prompt. Analyze a smaller repository, or
  run the app on a machine with more memory.
- **The container reports the wrong project.** `Dockerfile` bakes in
  `GOOGLE_CLOUD_PROJECT=my-demo-project-400313`. Override it with
  `-e GOOGLE_CLOUD_PROJECT` when you run the container, or with
  `--update-env-vars` when you deploy.
- **Streamlit reports a session state error.** Click **Reset All** in the
  sidebar, which clears every key in the session state.
- **Streamlit warns that it found no static folder.** `.streamlit/config.toml`
  sets `enableStaticServing`, and the repository ships no `static` directory,
  so the server prints the warning on every start. Ignore it, or create the
  directory if you want to serve your own files from it.

## Contribute

Contributions are welcome. Read the
[contribution guide](docs/CONTRIBUTING.md) for the Contributor License
Agreement, the community guidelines, and the pull request process. Run
`python3 check_readme.py` before you send a change that touches this README.

## Security

- Grant service accounts the smallest set of roles that the demos need.
- Prefer `gcloud auth application-default login` or an attached service
  identity over downloaded service account keys.
- Keep credential files out of the repository directory. `.gitignore`,
  `.dockerignore`, and `.gcloudignore` each exclude `.env`, and `.gitignore`
  also excludes `*-credentials.json`, but none of them excludes a service
  account key saved under another name, so such a key reaches your commits and
  your build context.
- Remove `--allow-unauthenticated` from `cloudbuild.yaml` and `setup.sh`, or put
  the service behind Identity-Aware Proxy, before you expose a deployment beyond
  a demo audience.
- Upload only material that you are allowed to send to Vertex AI. The demos
  forward your uploads, including source code and videos, to the model.

## License

This project is licensed under the Apache License 2.0. For the full text, see
the [LICENSE](LICENSE) file.