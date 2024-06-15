from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("API_KEY"))

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001", google_api_key="AIzaSyArBLvZkvVDeYEk4jVmXoU885elkoq2AGk")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

def get_conversational_chain():
    prompt_template = """
    You are an amazon customer support agent and you will be helping a customer today. Be polite, assuring and helping

    You will be provided with the user data, and context.

    DO NOT make up any answer and always try to answer using the context. Feel free to ask the user if you need any details.

    %Question
    {question}

    %USER DATA
    {user_data}

    Context
    {context}

    Begin!

    Previous conversation history:
    {chat_history}

    New input: {input}
    {agent_scratchpad}

    Answer:
    """

    memory = ConversationBufferMemory(memory_key="chat_history")
    model = ChatGoogleGenerativeAI(model="gemini-pro",
                             temperature=0.3, google_api_key="AIzaSyArBLvZkvVDeYEk4jVmXoU885elkoq2AGk", memory=memory)
                             

    prompt = PromptTemplate(template = prompt_template, input_variables = ["question", "user_data", "context"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    return chain

def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001", google_api_key="AIzaSyArBLvZkvVDeYEk4jVmXoU885elkoq2AGk")
    
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()

    response = chain(
        {"input_documents":docs, "question": user_question}
        , return_only_outputs=True)

    print(response)

def main():
    # user_input("My order is not delivered yet. Can you please check?")
    file = open("data.txt", 'r')
    raw_text = file.read()
    text_chunks = get_text_chunks(raw_text)
    get_vector_store(text_chunks)

if __name__ == "__main__":
    main()