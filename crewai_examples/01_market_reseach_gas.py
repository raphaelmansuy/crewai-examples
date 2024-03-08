import os
from crewai import Agent, Task, Crew, Process
from langchain_community.tools import DuckDuckGoSearchRun
from rich import print


search_tool = DuckDuckGoSearchRun()

os.environ["OPENAI_MODEL_NAME"] = "gpt-3.5-turbo-1106"


# Define your agents with roles and goals
researcher = Agent(
    role='Research Analyst',
    goal='Uncover the lastest trends on industrial Gas Market, especially for Hydrogen market.',
    backstory="""You are a research analyst with a focus on the industrial gas market.
    You are known for your ability to uncover the latest trends and breakthrough  
    technologies in the industry. You are also known for your ability to analyze
    complex data and transform it into actionable insights.""",
    verbose=True,
    allow_delegation=False,
    tools=[search_tool],
)
writer = Agent(
    role='Expert summarizer',
    goal='Craft compelling content on ',
    backstory="""You are an expert summarizer with a focus on the industrial gas market.
    You are known for your ability to transform complex data into engaging content
    that is accessible to a tech-savvy audience. You are also known for your ability
    to craft compelling narratives that are informative and engaging.""",
    verbose=True,
    allow_delegation=True,
)

# Create tasks for your agents
task1 = Task(
    description="""Conduct a comprehensive analysis on the topic of 
  industrial gas market, especially for Hydrogen market.
  You should provide a full analysis report that includes the latest trends,
  breakthrough technologies, and actionable insights.
  You can use any tool or method you see fit to
  answer that question.Your final answer MUST be a full analysis report""",
    expected_output="A full analysis report",
    agent=researcher
)

task2 = Task(
    description="""Using the insights provided by the research Analyst agent, 
  develop an engaging blog post that summarizes the content returned by ther agent
  Your post should be informative yet accessible, catering to a tech-savvy audience.
  Make it sound authoratative but avoid complex words so it doesn't sound like AI.
  Your final answer MUST be the full blog post of at least 4 paragraphs.""",
    expected_output="A blog post of at least 4 paragraphs",
    agent=writer
)

# Instantiate your crew with a sequential process
crew = Crew(
    agents=[researcher, writer],
    tasks=[task1, task2],
    verbose=2,  # You can set it to 1 or 2 to different logging levels
)

# Get your crew to work!
result = crew.kickoff()

print(result)
