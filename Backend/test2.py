from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.ollama         import Ollama
import asyncio

# Your multiplication tool
def multiply(a: float, b: float) -> float:
    return a * b

agent = FunctionAgent(
    tools=[multiply],
    llm=Ollama(model="llava:latest", request_timeout=360.0),
    system_prompt="You are a helpful assistant that can multiply two numbers.",
)

async def main():
    response = await agent.run("What is 1234 * 4567?")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
