# import dotenv
# dotenv.load_dotenv()

from typing import List
from pydantic import BaseModel
import json
import asyncio

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="LangGraph Agent API")


from src.graphs.phi.graph import graph as phi_graph
from src.graphs.phi.commands import handle_commands
from src.graphs.research.research_rabbit import builder as research_graph



# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins #TODO
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_sse_response(stream):
    """Create a StreamingResponse with SSE configuration."""
    return StreamingResponse(
        stream,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
            "X-Accel-Buffering": "no"
        }
    )

async def stream_graph_events(graph, input_data):
    """Stream events from a graph with standardized formatting."""
    async for event in graph.astream_events(input=input_data, version="v2"):
        kind = event["event"]
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                print("Sending:", content)
                # Replace newlines with encoded form for SSE
                content_encoded = content.replace('\n', '\\n')
                yield f"data: {content_encoded}\n\n"

async def stream_simple_response(message: str):
    """Stream a simple string message in SSE format."""
    yield f"data: {message}\n\n"

class PostRequest(BaseModel):
    user_message: str
    messages: List[dict]
    body: dict



@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "Welcome to the LangGraph Agent API"}

@app.post("/research", response_class=StreamingResponse)
async def research(request: PostRequest):
    research_topic = request.user_message
    if research_topic.startswith("/"):
        return create_sse_response(
            stream_simple_response("Commands are not supported in research mode.")
        )
        
    input_data = {"research_topic": research_topic}
    return create_sse_response(
        stream_graph_events(
            research_graph, 
            input_data
        )
    )

@app.post("/phi", response_class=StreamingResponse)
async def main(request: PostRequest):
    query = request.user_message
    if query.startswith("/"):
        return create_sse_response(handle_commands(request))

    # Create a default message from the user query if messages list is empty
    message = {"role": "user", "content": query}
    if request.messages and len(request.messages) > 0:
        message = request.messages[-1]

    input_data = {"messages": [message]}
    
    return create_sse_response(
        stream_graph_events(
            phi_graph, 
            input_data
        )
    )



# if __name__ == "__main__":
#     # TODO: LangSmith setup!

#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8510)
