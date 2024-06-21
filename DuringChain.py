from enum import Enum
import vertexai
import os
from vertexai.generative_models import GenerativeModel
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.vectorstores import FAISS
from utility.main import extract_function_call, parse_history
from vertexai.generative_models import (
    FunctionDeclaration,
    GenerationConfig,
    GenerativeModel,
    SafetySetting,
    HarmCategory,
    HarmBlockThreshold,
    Part,
    Tool,
)
from sentiment_analysis.main import SentimentTypes


class DuringChainStatus(Enum):
    TERMINATED = 0
    AGENT_TRANSFERRED = 1
    IN_PROGRESS_USER_QUERY = 2
    IN_PROGRESS_RETRIEVAL = 3
    IN_PROGRESS_GENERAL = 4


SYSTEM_INSTRUCTION = """
    Your name is Radha from Amazon Customer Support Agent Team.

    You are on a call so do not keep the customer waiting and give answers to every question. Reply shorter answers.
    
    You can use any of the tools for help. 
    get_data_of_user,
    get_answers_to_general_help,
    terminate_if_satisfied,
    send_to_agent_for_manual_intervention

    Do not verify anything about user because he is already verified.

    You can ask user if you need any details.
    
    If you are unable to find the answer, forward the call to agent by calling 'send_to_agent_for_manual_intervention'

    You can only tell the user about things, you cannot help if any thing needs to be executed. 
    For example, you cannot execute an return but you can only tell info about it.

    DO NOT MAKE UP ANSWERS/DETAILS OF YOUR OWN.
"""


class DuringChain():
    def __init__(self, user_data, user_query, sentiment, phone_number, system_instruction=SYSTEM_INSTRUCTION) -> None:
        vertexai.init(
            location=os.environ['LOCATION'], project=os.environ['PROJECT_ID'])
        self.user_data = user_data
        self.user_query = user_query
        self.safety_config = [
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_UNSPECIFIED,
                threshold=HarmBlockThreshold.BLOCK_NONE
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=HarmBlockThreshold.BLOCK_NONE
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=HarmBlockThreshold.BLOCK_NONE
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=HarmBlockThreshold.BLOCK_NONE
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=HarmBlockThreshold.BLOCK_NONE
            )
        ]
        self.sentiment = sentiment
        self.phone_number = phone_number

    def get_tools(self):
        get_data_of_user = FunctionDeclaration(
            name="get_data_of_user",
            description="""
                Do not make up any info, ask here if you need any info.

                Input what the user wants like his orders, product, transactions, items info and any other profile details. For example '''list previous orders of user'''.
            """,
            parameters={
                "type": "object",
                "properties": {"query": {"type": "string"}},
            }
        )

        get_info_about_query = FunctionDeclaration(
            name="get_info_about_query",
            description="""
            This searches through help docs of the Amazon Pages and finds relevant information about - 
            all policies (refund, cancellation and more)
            other related help docs
            You can take data from here to understand better about the solutions if not known to you already.
            """,
            parameters={
                "type": "object",
                "properties": {"query": {"type": "string"}},
            }
        )

        closes_the_call = FunctionDeclaration(
            name="closes_the_call",
            description="When the user seems satisfied, the call is closed by using this tool",
            parameters={
                "type": "object",
                "properties": {
                    "feedback_user": 
                        {
                            "type": "string"
                        }, 
                    "rating": 
                        {
                            "type": "integer"
                        }
                    },
            }
        )

        send_to_agent_for_manual_intervention = FunctionDeclaration(
            name="send_to_agent_for_manual_intervention",
            description="Sends the query to a human agent for manual intervention when the LLM is unable to process it.",
            parameters={
                "type": "object",
                "properties": {"query": {"type": "string"}},
            }
        )

        tools = Tool(
            function_declarations=[
                get_data_of_user,
                get_info_about_query,
                closes_the_call,
                send_to_agent_for_manual_intervention
            ],
        )

        return tools

    def initialize_model(self):
        model = GenerativeModel(
            "gemini-1.5-pro-001",
            generation_config=GenerationConfig(temperature=0.5),
            tools=[self.get_tools()],
            system_instruction=SYSTEM_INSTRUCTION,
            # safety_settings=self.safety_config
        )

        chat = model.start_chat(response_validation=False)
        self.chat = chat

        return chat

    def format_text(self, text):
        return "".join(text.split("\n"))

    def start_chat(self):
        print(self.user_query)
        response = self.chat.send_message(self.user_query)

        return self.validate_response(response)

    def validate_response(self, response):
        print(response, "Line 176 - During Chain")
        final_response = ""

        function_call_data = extract_function_call(response.to_dict())
        function_name = function_call_data['function_name']
        function_data = function_call_data['function_args']

        print(function_call_data)
        print(response.to_dict())
        
        print("Function Call:",  function_call_data)

        if (not function_name):
            try:
                ai_reply = self.format_text(response.text)
            except Exception as e:
                print(193, e)
                ai_reply = "There are some problems understanding or processing your text. Please say again! Sorry for the inconvenience caused. If you would like to transfer the call to agent, please let me know."

            return (DuringChainStatus.IN_PROGRESS_GENERAL, self.format_text(ai_reply))
        else:
            if (function_name == "send_to_agent_for_manual_intervention"):
                final_response = """You will soon receive a call from an agent. Thank you for contacting Amazon! This call can now be terminated."""
                return (DuringChainStatus.AGENT_TRANSFERRED, final_response)

            elif (function_name == "closes_the_call"):
                try:
                    feedback = function_data['feedback_user']
                    rating = function_data['rating']
                except Exception as e:
                    print("206", e)
                    feedback = 'NULL'
                    rating = 3

                print(feedback, rating)

                self.sentiment.analyze_chat_and_save(parse_history(self.chat), self.phone_number)
                self.sentiment.analyze_feedback_and_save_ai(feedback, rating, self.phone_number)

                final_response = """Thank you for calling Amazon. Have an amazing day!"""
                return (DuringChainStatus.TERMINATED, final_response)

            elif (function_name == "get_data_of_user"):
                question = function_data['query']

                response = self.send_message(
                    Part.from_function_response(
                        name=function_name,
                        response={
                            "content": self.get_data_of_user_chain(question),
                        },
                    ),
                )

                print(response)

                return (DuringChainStatus.IN_PROGRESS_USER_QUERY, self.format_text(response[1]))

            elif (function_name == "get_info_about_query"):
                response = self.send_message(
                    Part.from_function_response(
                        name=function_name,
                        response={
                            "content": self.get_info_about_query(question)
                        }
                    )
                )

                return (DuringChainStatus.IN_PROGRESS_RETRIEVAL, self.format_text(response[1]))

            else:
                self.sentiment.analyze_chat_and_save(parse_history(self.chat), self.phone_number)
                self.sentiment.analyze_feedback_and_save_ai("NULL", 3, self.phone_number)
                return (DuringChainStatus.AGENT_TRANSFERRED, """You will soon receive a call from an agent. Thank you for contacting Amazon! This call can now be terminated.""")

    def send_message(self, input):
        print(input, "to during chain")
        try:
            response = self.chat.send_message(input)
        except Exception as e:
            print(254, e)
            ai_reply = "There are some problems understanding or processing your text. Please say again! Sorry for the inconvenience caused. If you would like to transfer the call to agent, please let me know."
            return (DuringChainStatus.IN_PROGRESS_GENERAL, ai_reply)

        return self.validate_response(response)

    def get_data_of_user_chain(self, question):
        if(self.user_data == "None"):
            return "To access your orders, you need to call us using your registered Amazon Account mobile number."

        print("Starting get_data_of_user_chain")
        try:
            template = """
                Use the following pieces of context (JSON) which is everything of user data to answer the question at the end.
                If you don't know the answer, just say that you don't know, don't try to make up an answer.

                {context}

                Question: Find {question}

                Helpful Answer:"""

            prompt = PromptTemplate(
                input_variables=["context", "question"],
                template=template
            )

            sol = prompt.format(context=self.user_data, question=question)

            model = GenerativeModel(
                "gemini-1.5-pro-001",
                generation_config=GenerationConfig(temperature=0.5),
                safety_settings=None
            )

            chat = model.start_chat(response_validation=False)
            response = chat.send_message(sol)
            print(response.text)

            if (not response):
                return "There is no data available. Please transfer the call to agent."

            return self.format_text(response.text)
        except Exception as e:
            print("298", e)

    def get_info_about_query(self, user_question):
        print("Get Info About Query")
        model = ChatGoogleGenerativeAI(
            model="gemini-pro",
            client=genai,
            temperature=0.5,
            safety_settings=None
        )

        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001")

        new_db = FAISS.load_local(
            "faiss_index", embeddings, allow_dangerous_deserialization=True)
        print(new_db)

        def filter_contexts(term):
            contexts = new_db.similarity_search_with_score(term, k=3)

            print(contexts)

            ans_contexts = []

            for i in contexts:
                print(i[1])
                if (i[1] > 0.5):
                    ans_contexts.append(i[0].page_content)

            return ans_contexts

        data = filter_contexts(user_question)
        print(data)
        return "".join(data)
