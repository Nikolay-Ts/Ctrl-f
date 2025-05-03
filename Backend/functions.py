import json
from google.genai.types import FunctionDeclaration

with open(r"response_schema.json", "r") as f:
    response_schema = json.load(f)

search_documents = FunctionDeclaration(
        name="search_documents",
        description="""
            Search all documents for the query. Find all relevant information and extract it.
        """,
        parameters=response_schema
        )
