from typing import List, Union, Generator, Iterator
from schemas import OpenAIChatMessage
import requests
from pydantic import BaseModel


class Pipeline:
    class Valves(BaseModel):
        MODEL: str = "aya:latest"
        
        pass    
    def __init__(self):
        # Optionally, you can set the id and name of the pipeline.
        # Best practice is to not specify the id so that it can be automatically inferred from the filename, so that users can install multiple versions of the same pipeline.
        # The identifier must be unique across all pipelines.
        # The identifier must be an alphanumeric string that can include underscores or hyphens. It cannot contain spaces, special characters, slashes, or backslashes.
        # self.id = "ollama_pipeline"
        self.name = "DDGS&Aya 8B Pipeline"
        self.valves = self.Valves(
            **{
                "MODEL": "aya:latest"
            }
        )
        pass

    async def on_startup(self):
        # This function is called when the server is started.
        print(f"on_startup:{__name__}")
        pass

    async def on_shutdown(self):
        # This function is called when the server is stopped.
        print(f"on_shutdown:{__name__}")
        pass

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        # This is where you can add your custom pipelines like RAG.
        print(f"pipe:{__name__}")
        
        from duckduckgo_search import DDGS
        results = DDGS().text(user_message, max_results=5)
        OLLAMA_BASE_URL = "http://192.168.0.57:11434"
        MODEL = self.Valves.MODEL
        
        user_message=f"{user_message}. \n 이 질문에 답을 하기 위해, 질문과 연관성이 높은 사실만을 참조하여 답해주세요. \n {results} "
        body["messages"][0]["title"]=user_message
        
        if "user" in body:
            print("######################################")
            print(f'# User: {body["user"]["name"]} ({body["user"]["id"]})')
            print(f"# Message: {user_message}.")
            print("######################################")

        try:
            r = requests.post(
                url=f"{OLLAMA_BASE_URL}/v1/chat/completions",
                json={**body, "model": MODEL},
                stream=True,
            )

            r.raise_for_status()

            if body["stream"]:
                return r.iter_lines()
            else:
                return r.json()
        except Exception as e:
            return f"Error: {e}"