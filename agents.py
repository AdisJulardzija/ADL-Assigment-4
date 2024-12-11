from crewai import Agent, LLM
from textwrap import dedent
from langchain_openai import ChatOpenAI

class CustomAgents:
    def __init__(self):
        self.GPTModel = ChatOpenAI(model_name="gpt-4", temperature=0.7)  # Using GPT-4 for robust answers

    def economic_educator_agent(self):
        return Agent(
            role="Economic Educator",
            backstory=dedent("""
                An expert in economics with a mission to educate users on key concepts and their real-world implications. 
                Combines academic knowledge with current events to provide clear, structured, and engaging explanations.
            """),
            goal=dedent("""
                To answer user questions about economics, explain complex topics in an accessible manner, 
                and provide real-world examples to enhance understanding. At the end of your explanation provide four economic terms relevent to the query.
            """),
            llm=self.GPTModel,
        )
