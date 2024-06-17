from enum import Enum
import os
import vertexai
from vertexai.generative_models import GenerativeModel
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
from vertexai.preview import rag

SYSTEM_INSTRUCTION = """
    Your name is Radhika from `Amazon Customer Support Agent Team` powered by LLM and you will be helping a customer today. 

    You need to always verify if you are talking to the same person as the account holder for security purposes.

    If there is no user_data, you can ask for his phone number and input it to the `find_data` function to get the data.

    After you have the data, you can verify then by asking pincode, city and state of the customer and matching it with the data.

    Only move ahead with query once you are able to verify pincode + address of the customer.

    Always start with: "Welcome to Amazon! and a good greeting"
"""

class VerificationChainStatus(Enum):
    NOT_VERIFIED = 0
    VERIFIED = 1
    IN_PROGRESS = 2

class VerificationChain():
    def __init__(self, user_data, system_message = SYSTEM_INSTRUCTION) -> None:
        self.system_message = system_message
        self.messages = []
        self.user_data = user_data
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
        self.chat_instance = None

        vertexai.init(location=os.environ['LOCATION'], project=os.environ['PROJECT_ID'])


    def get_tools(self):
        user_verified = FunctionDeclaration(
            name="user_verified",
            description="This is called when the user is successfully verified",
            parameters={
                "type": "object",
                "properties": {"status": {"type": "boolean"}},
            },
        )

        # get_user_data = FunctionDeclaration(
        #     name="get_user_data",
        #     description="Get the info of the user to verify",
        #     parameters={
        #         "type": "object",
        #         "properties": {"phone_number": {"type": "integer"}},
        #     },
        # )

        user_not_verified = FunctionDeclaration(
            name="user_not_verified",
            description="This is called when user is not verified",
            parameters={
                "type": "object",
                "properties": {"status": {"type": "boolean"}},
            },
        )

        tools = Tool(
            function_declarations=[
                user_not_verified,
                user_verified
                # get_user_data
            ]
        )

        return tools

    def get_system_message(self):
        return self.system_message

    def get_model(self):
        model = GenerativeModel(
            "gemini-1.5-pro-001",
            generation_config=GenerationConfig(temperature=0.2),
            tools=[self.get_tools()],
            system_instruction=SYSTEM_INSTRUCTION
        )

        return model

    def get_chat_instance(self):
        return self.chat_instance

    def convert_to_str(messages):
        ans = ""
        for i in messages:
            ans += i[0] + " : " + i[1] + "\n"

        return ans

    def format_text(self, text):
        return "".join(text.split("\n"))

    def start_chat(self):
        self.chat_instance = self.get_model().start_chat(response_validation=False)
        INIT_PROMPT = str(self.user_data)
        return self.send_message(INIT_PROMPT)

    def send_message(self, message):
        # self.messages.append(("human", message))
        response = self.chat_instance.send_message(message, safety_settings=self.safety_config)
        
        final_response = ""
        function_call = response.candidates[0].content.parts[0].function_call

        if(not function_call):
            print(response.candidates[0].content.parts[0].text)
            ai_reply = self.format_text(response.candidates[0].content.parts[0].text)
            # self.messages.append(("AI", ai_reply))
            return (VerificationChainStatus.IN_PROGRESS, ai_reply)
        else:
            function_name = response.candidates[0].content.parts[0].function_call.name

            if(function_name == "user_not_verified"):
                final_response = """I'm sorry, but I am unable to verify the details at this time. Thank you for contacting Amazon!"""
                return (VerificationChainStatus.NOT_VERIFIED, final_response)
            elif(function_name == "user_verified"):
                final_response = """Thank you for verifying your details."""
                return (VerificationChainStatus.VERIFIED, final_response)
            elif(function_name == "get_user_data"):
                phone_number = function_call.args['phone_number']
                # Perform a mongo query here, return data, send it to the Gemini. TODO
                response = self.send_message(
                    Part.from_function_response(
                        name=function_name,
                        response={
                            "content": "response from API",
                        },
                    ),
                )
                return (VerificationChainStatus.IN_PROGRESS, "TODO")