# The goal of the context gathering agent is to search, compact the context and save it in memory

from google.adk.agents import Agent
from google.adk.tools import google_search

def create_context_gathering_agent() -> Agent:
    '''
    Creates a specialized context gathering agent that :
    1. Performs high quality Google Search on a given topic
    2. Compacts and structures the results
    3. Saves a context knowledge base into session state
    '''
    return Agent(
        name="ContextGatheringAgent",
        model="gemini-2.5-flash-lite",
        description="Expert researcher that gathers and curates high-quality web context on any topic",
        instruction="""You are Context Gathering specialized agent with world class web researcher. Your mission is to receive a topic, use google_search tool to find the 5 most educational resources based on user's learning style and level. Return only a compact, well-structured knowledge base and format it with clean title and key snippet per source. Prioritize the educational content, just gather and present raw curated context and always return markdown with bullet points and links""",
        tools=[google_search],
        output_key="raw_search_results",
    )


def create_compaction_agent() -> Agent:
    '''
    Context Engineering concept compaction is implemented here to improve the context gathered from the Context Gathering Agent
    '''
    return Agent(
        name="ContextCompactionAgent",
        model="gemini-2.5-flash-lite",
        description="Expert knowledge distiller that compresses web research into dense, high-signal context.",
        instruction="""You are a Context Compaction Agent and your job is to take the raw, noisy output from google_search (with titles, snippets, URLs) and transform it into a compact, high-density knowledge base.
        You are given raw search results from the previous step. Your job is to read the {raw_search_results} and transform it into a compact, high density knowledge base.

        RULES:
        - Keep only the most important, verifiable facts
        - Remove duplicates, ads, fluff, navigation text
        - Structure as clean markdown with clear sections
        - Max 500 tokens total (aim for 300-400)
        - Use bullet points, bold key terms
        - Include source URLs only if truly authoritative
        - Prioritize educational depth over breadth
        - Match the user's learning style from the original query

        Input: Raw google_search results
        Output: A single, dense, perfectly curated knowledge base ready for teaching.
        """,
        output_key="context_knowledge_base",
    )