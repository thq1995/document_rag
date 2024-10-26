from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.memory import ConversationBufferMemory
import tempfile
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from app.core.config import Model
import os

class RAGService:
    def __init__(self, storage_path="vector_store"):
        self.conversation_chain = None
        self.chat_history = []
        self.storage_path = storage_path
        self.embeddings = OpenAIEmbeddings()
        
    async def process_documents(self, files=None):
        """Process documents and initialize conversation chain.
        If files is None, try to load existing vector store."""
        
        if files is None and os.path.exists(self.storage_path):
            # Load existing vector store
            try:
                vectorstore = FAISS.load_local(self.storage_path, self.embeddings)
                print(f"Loaded existing vector store from {self.storage_path}")
            except Exception as e:
                raise ValueError(f"Error loading vector store: {e}")
        else:
            # Process new documents
            if not files:
                raise ValueError("No files provided and no existing vector store found")
                
            documents = []
            for file in files:
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    content = await file.read()
                    temp_file.write(content)
                    temp_file.flush()
                    
                    if file.filename.endswith('.pdf'):
                        loader = PyPDFLoader(temp_file.name)
                    else:
                        loader = TextLoader(temp_file.name)
                    
                    documents.extend(loader.load())
                    
                os.unlink(temp_file.name)
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(documents)
            
            # Create and save vector store
            vectorstore = FAISS.from_documents(splits, self.embeddings)
            os.makedirs(self.storage_path, exist_ok=True)
            vectorstore.save_local(self.storage_path)
            print(f"Created and saved new vector store to {self.storage_path}")
            
        # System prompt template
        system_template = """You are a helpful AI assistant. Use the following pieces of context to answer the user's question.
        If the question is not clear, ask the user to provide more information.
        This is a Vietnamese language model and English model, so please answer in Vietnamese or English depending on the context.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        
        Context: {context}
        ---------------
        Chat History: {chat_history}
        """
        
        # User question template
        user_template = """Question: {question}"""
        
        # Create messages
        messages = [
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(user_template)
        ]
        
        # Create chat prompt template
        prompt = ChatPromptTemplate.from_messages(messages)
        
        # Create memory
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialize conversation chain
        llm = Model.openai
        self.conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(),
            combine_docs_chain_kwargs={"prompt": prompt},
            # return_source_documents=True,
            # memory=memory,
            get_chat_history=lambda h: h
        )
    
    async def get_response(self, question: str):
        """Get response for a question using the conversation chain"""
        if not self.conversation_chain:
            # Try to load existing vector store if conversation chain is not initialized
            try:
                await self.process_documents()
            except ValueError as e:
                raise ValueError("No documents processed yet and couldn't load existing vector store")
        
        response = self.conversation_chain({
            "question": question,
            "chat_history": self.chat_history
        })
        
        self.chat_history.append((question, response["answer"]))
        return response
    
    def clear_history(self):
        """Clear the chat history"""
        self.chat_history = []