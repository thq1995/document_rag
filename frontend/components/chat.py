import aiohttp
from typing import List
import chainlit as cl
from io import BytesIO
import os

class AsyncChat:
    def __init__(self):
        self.api_url = os.getenv("API_URL", "http://localhost:8000")
        self.api_port = os.getenv("PORT", "8080")

        self.session = None
    
    async def setup(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def process_documents(self, files: List[cl.File]):
        await self.setup()
        async with cl.Step("Processing documents...") as step:
            if not files:
                await cl.Message("Please attach files to upload").send()
                return
        
            for file in files:
                try:
                    # Check if file path is available and read content as bytes
                    with open(file.path, "rb") as f:
                        file_content = f.read()
                    
                    # Prepare multipart form data
                    form_data = aiohttp.FormData()
                    form_data.add_field(
                        "files", 
                        file_content, 
                        filename=file.name, 
                        content_type=file.type
                    )

                    # Send the request to FastAPI
                    async with self.session.post(
                        f"{self.api_url}:{self.api_port}/documents/upload",
                        data=form_data
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            await cl.Message(f"✅ Successfully uploaded {file.name}").send()
                        else:
                            error_text = await response.text()
                            await cl.Message(f"❌ Failed to upload {file.name}. Status: {response.status}, Error: {error_text}").send()
                            
                except Exception as e:
                    await cl.Message(f"❌ Error uploading {file.name}: {str(e)}").send()
            
            
    async def get_response(self, message: str):
        await self.setup()
        async with cl.Step("Thinking...") as step:
            try:
                data = {"question": message}
                print("data", data)
                url = f"{self.api_url}:{self.api_port}/documents/query"
                print("url", url)
                async with self.session.post(
                    f"{self.api_url}:{self.api_port}/documents/query",
                    json=data
                ) as response:
                    print("response", response.status)
                    if response.status == 200:
                        result = await response.json()
                        return result
                    if response.status == 400:
                        result = await response.json()
                        await cl.Message(f"❌ Error getting response: {result['detail']}").send()
                        return
                    
            except Exception as e:
                cl.Message(f"❌ Error getting response: {str(e)}").send()
                raise
    
    async def close(self):
        if self.session:
            await self.session.close()