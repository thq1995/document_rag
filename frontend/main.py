import chainlit as cl
from components.chat import AsyncChat
from typing import List
from chainlit.types import AskFileResponse
import aiohttp
from pathlib import Path
import tempfile
import os
from dotenv import load_dotenv

load_dotenv()
chat = AsyncChat()

    
@cl.on_chat_start
async def start():
    
    await cl.Message(
        content="**Welcome AIO Document RAG 📝 ! Please upload your documents using the file upload button. Enjoy 😁🚀**"
    ).send()
    
                    
@cl.on_message
async def main(msg: cl.Message):
    if not msg.elements and msg.content:
        content = await chat.get_response(msg.content)
        # print("content", content)
        if content:
            await cl.Message(
                content=content['answer']
            ).send()
    else:
        await chat.process_documents(msg.elements)
        content = await chat.get_response(msg.content)
        # print("content", content)
        if content:
            await cl.Message(
                content=content['answer']
            ).send()
        
        
@cl.on_stop
async def on_stop():
    if chat:
        await chat.close()@cl.on_file_upload