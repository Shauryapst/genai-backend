from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings,ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from dotenv import load_dotenv
import os
load_dotenv()

def get_pdf_text(pdfFiles):
    for file in pdfFiles:
        print(file)
        print()
    text = ""
    for pdf_file in pdfFiles:
        pdf_reader = PdfReader(pdf_file.file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_chunks_from_text(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap = 10)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks, sessionId):
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
    except Exception as e:
        return {"error": f"Failed to create embeddings: {str(e)}"}
    
    try:
        vector_store = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    except Exception as e:
        return {"error": f"Failed to create vector store: {str(e)}"}
    try:
        save_path = f"./db/{sessionId}/faiss_index"
        vector_store.save_local(save_path)
    except Exception as e:
        return {"error": f"Failed to save vector store locally: {str(e)}"}
    
    return {"success": "Vector store created and saved successfully"}

def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context\n\n
    Context : \n{context}?\n
    Question : \n{question}\n
    
    Answer : 
     
    """
    model = ChatGoogleGenerativeAI(model='gemini-pro', temperature=0.7)
    prompt = PromptTemplate(template=prompt_template, input_variables=['context', 'question'])
    chain = load_qa_chain(model, chain_type='stuff', prompt=prompt)
    return chain

def user_input(user_question, sessionId):
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
    except Exception as e:
        print(f"Failed to create embeddings: {str(e)}")
        return
    
    try:
        save_path = f"./db/{sessionId}/faiss_index"
        new_db = FAISS.load_local(save_path, embeddings=embeddings, allow_dangerous_deserialization=True)
    except Exception as e:
        print(f"Failed to load vector store: {str(e)}")
        return
    
    try:
        docs = new_db.similarity_search(query=user_question)
    except Exception as e:
        print(f"Failed to perform similarity search: {str(e)}")
        return
    
    try:
        chain = get_conversational_chain()
    except Exception as e:
        print(f"Failed to get conversational chain: {str(e)}")
        return
    
    try:
        response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)
        print(response)
        return response
    except Exception as e:
        print(f"Failed to generate response: {str(e)}")
        return