import json
from google.genai.types import FunctionDeclaration

with open(r"response_schema.json", "r") as f:
    response_schema = json.load(f)

search_documents = FunctionDeclaration(
        name="search_documents",
        description="""
            "Searches the document for text or image elements similar to a user query and returns their page number and bounding box.
        """,
        parameters=response_schema
        )
