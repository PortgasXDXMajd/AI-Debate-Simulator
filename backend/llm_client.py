import json
import aiohttp
from pydantic import BaseModel
from typing import Any, AsyncIterator, Dict, List, Type, TypeVar

T = TypeVar("T", bound=BaseModel)

class OpenRouterClient:
    def __init__(self, api_key: str | None = None):
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def acomplete_messages(
        self,
        model: str,
        messages: List[Dict[str, str]],
        output_model: Type[T],
        temperature: float = 1.0,
        ) -> T:
            url = f"{self.base_url}/chat/completions"
            
            output_schema = output_model.model_json_schema()
            output_schema["additionalProperties"] = False

            payload: Dict[str, Any] = {
                "model": model,
                "temperature": temperature,
                "messages": messages,
                "response_format":{
                    "type": "json_schema",
                    "json_schema": {
                        "name": "output_schema",
                        "strict": True,
                        "schema": output_schema
                    }
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as resp:
                    if resp.status in (401, 403):
                        detail = await resp.text()
                        raise RuntimeError(f"OpenRouter auth/model error ({resp.status}): {detail}")
                    resp.raise_for_status()
                    res = await resp.json()

                    content = res["choices"][0]["message"]["content"]

                    if isinstance(content, str):
                        import json
                        content = json.loads(content)

                    return output_model.model_validate(content)
    
    async def astream_messages(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
    ) -> AsyncIterator[str]:
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": model,
            "plugins": [{ "id": "web" }],
            "temperature": temperature,
            "messages": messages,
            "stream": True
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, json=payload) as resp:
                if resp.status in (401, 403):
                    detail = await resp.text()
                    raise RuntimeError(f"OpenRouter auth/model error ({resp.status}): {detail}")
                resp.raise_for_status()
                async for raw in resp.content:
                    line = raw.decode("utf-8").strip()
                    if not line or not line.startswith("data:"):
                        continue
                    data = line[len("data:"):].strip()
                    if data == "[DONE]":
                        break
                    try:
                        event = json.loads(data)
                        delta = event["choices"][0]["delta"].get("content")
                        if delta:
                            yield delta
                    except Exception:
                        continue