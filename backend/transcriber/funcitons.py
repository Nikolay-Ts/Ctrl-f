import json
from google.genai.types import FunctionDeclaration

with open(r"response_schema.json", "r") as f:
    response_schema = json.load(f)

get_timestamp = FunctionDeclaration(
        name="get_timestamp",
        description="""
            Extract the timestamp from the transcript where the topic of the query is mentioned.
        """,
        parameters=response_schema
        )
