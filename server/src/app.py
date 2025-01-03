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


from src.graph.graph import graph
from src.graph.commands import handle_commands



# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins #TODO
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




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


@app.post("/chat")
async def main(request: PostRequest):

    query = request.user_message
    if query.startswith("/"):
        return StreamingResponse(
            handle_commands(request),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            }
        )

    # Create a default message from the user query if messages list is empty
    message = {"role": "user", "content": query}
    if request.messages and len(request.messages) > 0:
        message = request.messages[-1]

    async def event_stream():
        async for event in graph.astream_events(input={"messages": [message]}, version="v2"):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    # Replace newlines with encoded form for SSE
                    content_encoded = content.replace('\n', '\\n')
                    yield f"data: {content_encoded}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
            "X-Accel-Buffering": "no",
            "Transfer-Encoding": "chunked"
        }
    )



if __name__ == "__main__":
    # TODO: LangSmith setup!

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8510)
