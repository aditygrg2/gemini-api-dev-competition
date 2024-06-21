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
from utility.main import extract_function_call
commented = ""

SYSTEM_INSTRUCTION = """
You are an Amazon Customer Support Agent and you are compassionate and assuring to help your user always!

You need to always verify if you are talking to the same person as the account holder for security purposes.

If there is no user_data, you can ask for his amazon account phone number and input it to the `get_user_data_with_phone_number` function to get the data.

After you have the data, you can verify then by asking pincode and city and state of the customer and matching it with the data.

Only move ahead with query once you are able to verify pincode and address of the customer.

Call `user_verified` tool if user is verified, else if not verified call `user_not_verified` tool.
Good Luck Agent!
"""

class VerificationChainStatus(Enum):
    NOT_VERIFIED = 0
    VERIFIED = 1
    IN_PROGRESS = 2

class VerificationChain():
    def __init__(self, user_data, user_query, phone_number, system_message = SYSTEM_INSTRUCTION) -> None:
        self.system_message = system_message
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
        self.chat_instance = None
        self.phone_number = phone_number

        vertexai.init(location=os.environ['LOCATION'], project=os.environ['PROJECT_ID'])


    def get_tools(self):
        user_verified = FunctionDeclaration(
            name="user_verified",
            description="This is called when the user is successfully verified.",
            parameters={
                "type": "object",
                "properties": {"VerificationChainStatus": {"type": "boolean"}},
            },
        )

        get_user_data_with_phone_number = FunctionDeclaration(
            name="get_user_data_with_phone_number",
            description="Get the info of the user to verify using phone number",
            parameters={
                "type": "object",
                "properties": {"phone_number": {"type": "string"}},
            },
        )

        user_not_verified = FunctionDeclaration(
            name="user_not_verified",
            description="This is called when user is not verified",
            parameters={
                "type": "object",
                "properties": {"VerificationChainStatus": {"type": "boolean"}},
            },
        )

        tools = Tool(
            function_declarations=[
                user_not_verified,
                user_verified,
                get_user_data_with_phone_number
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

    def convert_to_str(self, messages):
        ans = ""
        for i in messages:
            ans += str(i[0]) + " : " + str(i[1]) + "\n"

        return ans

    def format_text(self, text):
        return "".join(text.split("\n"))

    def start_chat(self):
        commented = """
        [Ask pincode And `city and state` from user and match with this data, this is not provided by user, but received from database.]
        User Data: `{self.user_data}"""
        
        print("Start Chat")
        query = f"""
        User Query: `{self.user_query}` \n 
        Phone Number: `{self.phone_number}` \n
`"""
        self.chat_instance = self.get_model().start_chat(response_validation=False)
        print("146", query)
        return self.send_message(query)

    def send_message(self, message):
        print(self.chat_instance.history)
        # response = self.chat_instance.send_message(message, safety_settings=self.safety_config)
        response = self.chat_instance.send_message(message)

        function_call_data = extract_function_call(response.to_dict())
        function_name = function_call_data['function_name']
        function_data = function_call_data['function_args']

        print(function_call_data)
        print(response.to_dict())

        if(not function_name):
            not_function_text = ""
            try:
                not_function_text = response.text
                ai_reply = self.format_text(not_function_text)
                return (VerificationChainStatus.IN_PROGRESS, ai_reply)
            except:
                final_response = """You will receive a callback from Amazon. Thank you for contacting us!"""
                return (VerificationChainStatus.NOT_VERIFIED, final_response)
            
        else:
            if(function_name == "user_not_verified"):
                final_response = """I'm sorry, but I am unable to verify the details at this time. Thank you for contacting Amazon!"""
                return (VerificationChainStatus.NOT_VERIFIED, final_response)
            elif(function_name == "user_verified"):
                final_response = """Thank you for verifying your details."""
                return (VerificationChainStatus.VERIFIED, final_response)
            elif(function_name == "get_user_data_with_phone_number"):
                print("156", response)
            
                phone_number = self.format_text(function_data['phone_number'].strip().replace(" ", ""))
                # Perform a mongo query here, return data, send it to the Gemini. TODO

                if(not phone_number):
                    phone_number = str(self.phone_number)

                response = self.send_message(
                    Part.from_function_response(
                        name=function_name,
                        response={
                            "content": self.user_data,
                        },
                    ),
                )
                
                return (VerificationChainStatus.IN_PROGRESS, self.format_text(response[1]))