import asyncio
import httpx

async def test_stream():
    url = "http://127.0.0.1:8000/api/chat/stream"
    params = {"session_id": "test_session", "question": "Hello, can you hear me?"}
    headers = {"X-API-TOKEN": "my-dev-token"}
    
    print(f"Connecting to {url}...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("GET", url, params=params, headers=headers) as response:
                print(f"Status: {response.status_code}")
                if response.status_code != 200:
                    print(await response.aread())
                    return
                
                async for line in response.aiter_lines():
                    if line:
                        print(f"Received: {line}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_stream())
