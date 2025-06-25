
from fastapi import FastAPI,Request
import uvicorn 
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from fastapi.middleware.cors import CORSMiddleware
from podcast import getScript,audio
import io




app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)
class Prompt(BaseModel):
    user_id: str
    prompt: str

@app.get("/")
async def read_root():
    
    return {"message": "Hello World from mohith surya raghav"}


connected_clients = {}




# @app.post("/prompt")
# async def agent_run(prompt:Prompt):
#     user_id = prompt.user_id
#     prompt = prompt.prompt
#     socket_id = connected_clients.get(user_id)
#     agent,thoughts=initagent() 
#     res =  agent.invoke(prompt) 
#     print(type(res.get('output')))
#     return {"answer":str(res.get('output')),"thoughts":thoughts.thoughts}
    
@app.post('/url')
async def givespeech(data:Prompt):
    url=data.prompt 
    script= await getScript(url) 
    audio_bytes=audio(script) 
    stream = io.BytesIO(audio_bytes)
    stream.seek(0)
    return StreamingResponse(stream, media_type="audio/mpeg")

    







if __name__ == "__main__":
    print("Starting Uvicorn server...")
    
    uvicorn.run(
        "backend:app",  
        host="127.0.0.1",
        port=8000,
        reload=True, 
        log_level="info"
    )
   