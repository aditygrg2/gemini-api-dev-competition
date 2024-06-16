from langchain import OpenAI
from langchain.chat_models import ChatOpenAI
import os
from langchain.agents import Tool
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from langchain.chains import ConversationChain
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.schema import SystemMessage
from langchain.agents import AgentExecutor, initialize_agent
from langchain_google_vertexai import VertexAI
from langchain_google_community import VertexAISearchRetriever
from langchain_google_community import VertexAIMultiTurnSearchRetriever
from langchain.chains import ConversationalRetrievalChain

during_chain_prompt = """
    %USER QUERY
    {user_query}

    %USER DATA
    {user_data}

    Context
    {context}

    Begin!

    Previous conversation history:
    {chat_history}

    New input: {input}
    {agent_scratchpad}
"""

sys_ins = """
Your name is Radhika from `Amazon Customer Support Agent Team` powered by LLM and you will be helping a customer today. 

Be polite, assuring and helping. 

You will be provided with the user data by him, and context.
DO NOT SHARE USER DATA TO THE USER, JUST USE IT FOR YOUR HELP AND DETECTING THE ANSWERS.

Feel free to ask the user if you need any details. 
Ask and communicate with user, context is just for your help. You can answer things on your own as well!

Anytime if you feel you are unable to find the answer, you can forward the call to the agent executive.

Always start with: "Welcome to Amazon! and a good greeting"

%Context
{context}

%Question
{question}

Previous conversation history:
{chat_history}

Begin! call is live with customer
"""

class DuringChain():
    def __init__(self, prompt = during_chain_prompt, system_instructions = sys_ins) -> None:
        self.template = prompt = PromptTemplate(
            input_variables=["user_query", "user_data", "context"],
            template=during_chain_prompt
        )
        self.system_instructions = system_instructions

    def initialize_model(self, user_phone_number):
        MODEL = os.environ['MODEL']
        PROJECT_ID = os.environ['PROJECT_ID']
        DATA_STORE_LOCATION = os.environ['DATA_STORE_LOCATION']
        DATA_STORE_ID = os.environ['DATA_STORE_ID']

        llm = VertexAI(model_name=MODEL, temperature=0.4, max_output_tokens=1024, project=PROJECT_ID, system_instruction=self.system_instructions)

        multi_turn_retriever = VertexAIMultiTurnSearchRetriever(
            project_id=PROJECT_ID, location_id=DATA_STORE_LOCATION, data_store_id=DATA_STORE_ID
        )

        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        conversational_retrieval = ConversationalRetrievalChain.from_llm(
            llm=llm, retriever=multi_turn_retriever, memory=memory, combine_docs_chain_kwargs={
                'prompt': self.template
            }, rephrase_question=False
        )

        self.conversational_retrieval = conversational_retrieval

    def first_message(self, user_data, user_query):
        response = self.conversational_retrieval.invoke("""
        
        User Data:
        {user_data}

        User Query:
        {user_query}
        
        """.format(user_data, user_query))

        return response.answer
    
    def send_message(self, request):
        response = self.conversational_retrieval.invoke(request)
        return response.answer