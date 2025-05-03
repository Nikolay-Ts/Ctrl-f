import json
from google.genai.types import FunctionDeclaration, GenerateContentConfig, Part, Tool

with open("schema.json", "r") as f:
    schema = json.load(f)

search_documents = FunctionDeclaration(
        name="search_documents",
        description="""
            Search all documents for the query. Find all relevant information and extract it.
        """,
        parameters=json.load(schema)
        )
