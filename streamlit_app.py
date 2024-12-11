# streamlit_app.py
import streamlit as st
import requests
from pyvis.network import Network
import networkx as nx

# Streamlit app title
st.title("Educational Economic Chatbot")

# Instructions
st.markdown("""
Enter a topic or question about economics to learn more. The chatbot will provide an explanation of the topic, 
and a knowledge graph will be displayed based on relevant economic terms related to the topic.
""")

# Input field
topic = st.text_input("Enter your economic topic or question:")

# Button to educate the user and display the knowledge graph
if st.button("Educate Me"):
    if topic:
        with st.spinner("Educating..."):
            try:
                # Call the FastAPI backend
                response = requests.post(
                    "http://127.0.0.1:8002/educate",
                    json={"topic": topic}
                )
                if response.status_code == 200:
                    result = response.json()
                    
                    # Extract explanation and terms with fallback
                    explanation = result.get("explanation", "No explanation provided.")
                    terms = result.get("terms", [])

                    # Display the explanation
                    st.success("Explanation of the topic:")
                    st.text_area("Explanation", explanation, height=300)

                    # Display the knowledge graph
                    if terms:
                        st.subheader("Knowledge Graph")
                        G = nx.Graph()

                        # Add the central query node
                        G.add_node(topic, size=20)

                        # Add term nodes and connect them to the query
                        for term in terms:
                            G.add_node(term, size=15)
                            G.add_edge(topic, term)

                        # Visualize the graph using PyVis
                        net = Network(notebook=False, width="800px", height="600px")
                        net.from_nx(G)
                        net.save_graph("knowledge_graph.html")
                        st.components.v1.html(
                            open("knowledge_graph.html", "r").read(), height=600
                        )
                    else:
                        st.warning("No terms were identified to generate the knowledge graph.")
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Connection error: {e}")
    else:
        st.warning("Please enter a topic or question.")
