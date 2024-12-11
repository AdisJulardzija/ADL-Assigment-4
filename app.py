# app.py
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from decouple import config

from crewai import Crew
from agents import CustomAgents
from tasks import CustomTasks

from neo4j import GraphDatabase

# Load environment variables
os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")
os.environ["OPENAI_ORGANIZATION_ID"] = config("OPENAI_ORGANIZATION_ID")
NEO4J_URI = config("NEO4J_URI")
NEO4J_USER = config("NEO4J_USER")
NEO4J_PASSWORD = config("NEO4J_PASSWORD")

# Define request and response schemas
class CrewRequest(BaseModel):
    topic: str

class CrewResponse(BaseModel):
    explanation: str
    terms: list

# Initialize FastAPI app
app = FastAPI(
    title="Educational Economic Chatbot API",
    description="API for educating users on economic concepts and current events.",
    version="1.0.0",
)

# Neo4j session
def add_terms_to_graph(query, terms):
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as session:
        session.write_transaction(create_knowledge_graph, query, terms)
    driver.close()

def create_knowledge_graph(tx, central_query, terms):
    # Clear existing graph
    tx.run("MATCH (n) DETACH DELETE n")
    
    # Create the central query node
    tx.run("CREATE (q:Query {name: $central_query})", central_query=central_query)
    
    # Create term nodes and connect them to the query node
    for term in terms:
        tx.run("""
            MERGE (t:Term {name: $term_name})
            MERGE (q:Query {name: $central_query})
            MERGE (q)-[:RELATES_TO]->(t)
        """, term_name=term, central_query=central_query)

# Define the CustomCrew class
class CustomCrew:
    def __init__(self, topic: str):
        self.topic = topic

    def run(self) -> dict:
        agents = CustomAgents()
        tasks = CustomTasks()

        # Generate explanation for the query
        educator_agent = agents.economic_educator_agent()
        educate_task = tasks.educate_task(educator_agent, self.topic)
        crew = Crew(agents=[educator_agent], tasks=[educate_task], verbose=True)
        crew_output = crew.kickoff()
        explanation = getattr(crew_output, "raw", str(crew_output))

        # Generate terms for the knowledge graph independently
        terms = find_relevant_terms_with_gpt(self.topic)

        # Add terms to Neo4j
        add_terms_to_graph(self.topic, terms)

        return {"explanation": explanation, "terms": terms}

def find_relevant_terms_with_gpt(query: str):
    """
    Finds relevant economic terms for the query using GPT.
    """
    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model_name="gpt-4", temperature=0.3)
    prompt_template = PromptTemplate(
        input_variables=["query"],
        template=(
            "Identify the most relevant economic terms related to the following query. "
            "Provide a comma-separated list of terms without explanations.\n\nQuery: {query}"
        )
    )
    chain = LLMChain(llm=llm, prompt=prompt_template)
    response = chain.run({"query": query})

    # Convert GPT's response to a list of terms
    return [term.strip() for term in response.split(",") if term.strip()]

# Define the API endpoint
@app.post("/educate", response_model=CrewResponse)
async def educate_user(crew_request: CrewRequest):
    try:
        custom_crew = CustomCrew(crew_request.topic)
        result = custom_crew.run()
        return CrewResponse(
            explanation=result["explanation"],
            terms=result["terms"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint for health check
@app.get("/")
def read_root():
    return {"message": "Welcome to the Educational Economic Chatbot API. Use /docs for API documentation."}

# Entry point for running the app
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8002, reload=True)
