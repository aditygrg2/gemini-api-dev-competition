from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain import hub

API_KEY = ""

llm_model = "gpt-3.5-turbo-0301"

llm = ChatOpenAI(temperature=0.2, model=llm_model,api_key=API_KEY)

prompt = hub.pull("hwchase17/react")

class LangchainTools():
    def __init__(self,context) -> None:
        self.formatContext(context)
        tools = [
            Tool(
                name='retrieveApplicationStatus',
                description="""""",
                func=self.retrieveApplicationStatus,
                return_direct=True,
            ),
            Tool(
                name='generalQueries',
                description="""""",
                func=self.generalQueries,
                return_direct=True,
            ),
        ]
        agent = create_react_agent(llm, tools, prompt)
        self.agent = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=4,handle_parsing_errors=True)
    
    def formatContext(self, context):
        self.context  = context


    def retrieveApplicationStatus(self, _):
        stage = self.context['candidate']
        return "your application stage is "+stage


    def generalQueries(self, _):
        prompt = f"""
        Context:

        Answer the user query based on the above data only
        """
        result = llm.invoke(prompt).content
        return result

    def run(self):
        prompt = f"""
        user query:
        

        you have to use only one tool to answer 1 query
        """
        return self.agent.invoke({"input":prompt})