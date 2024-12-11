from crewai import Task
from textwrap import dedent

class CustomTasks:
    def __tip_section(self):
        return "Ensure your response is clear, accurate, and provides real-world examples!"

    def educate_task(self, agent, topic: str):
        return Task(
            description=dedent(
                f"""
                Educate the user on the following topic: "{topic}". 

                {self.__tip_section()}

                Your explanation should include:
                - A clear and concise definition or overview of the topic.
                - Examples of its application in the real world.
                - Insights into how this topic connects to other economic concepts.
                - At the end give a list of four economic terms relevant to the query. Make sure the list is called Relevant economic terms.

                Use a structured approach to ensure the user understands the topic thoroughly.
                """
            ),
            expected_output="An educational explanation of the topic, including examples and connections to other concepts.",
            agent=agent,
        )