from utils_vertex import MODEL_ID

# The one Gemini model this demo calls. utils_vertex.py owns the identifier so
# a single edit moves every demo to a new model.
MODEL_NAMES = [MODEL_ID]

video_uris = {
    "E-commerce (Nike)": "gs://convento-samples/nike-sbf.mp4",
    "Pharmacy (Raia)": "gs://convento-samples/raia.mp4",
    "Healthcare": "gs://convento-samples/friction-log.mp4"
}