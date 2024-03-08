import os
from crewai import Agent, Task, Crew, Process
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import load_tools
from langchain.tools import tool
from langchain_community.llms import OpenAI
from crewai.tasks.task_output import TaskOutput
from rich import print

search_tool = DuckDuckGoSearchRun()

from langchain_community.llms import Ollama

# llm = Ollama(model="mistral")

llm = OpenAI(model_name="gpt-3.5-turbo-instruct")

os.environ["OPENAI_MODEL_NAME"] = "gpt-3.5-turbo-1106"

# Define the topic of interest
topic = "Air Liquide vs Linde in Hydrogen Market"

# Loading Human Tools
human_tools = load_tools(["human"])


def callback_function(output: TaskOutput):
    # Do something after the task is completed
    # Example: Send an email to the manager
    print(
        f"""
        Task completed!
        Task: {output.description}
        Output: {output.result}
    """
    )


# Creating custom tools
class ContentTools:
    @tool("Read webpage content")
    def read_content(url: str) -> str:
        """Read content from a webpage."""
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        text_content = soup.get_text()
        return text_content[:5000]


# Define the manager agent
manager = Agent(
    role="Project Manager",
    goal="Coordinate the project to ensure a seamless integration of research findings into compelling narratives",
    verbose=True,
    backstory="""With a strategic mindset and a knack for leadership, you excel at guiding teams towards
    their goals, ensuring projects not only meet but exceed expectations.""",
    allow_delegation=True,
    max_iter=10,
    max_rpm=20,
)

# Define the senior researcher agent
researcher = Agent(
    role="Senior Researcher",
    goal=f"Uncover groundbreaking technologies around {topic}",
    verbose=True,
    backstory="""Driven by curiosity, you're at the forefront of innovation, eager to explore and share
    knowledge that could change the world.""",
)

# Define the writer agent
writer = Agent(
    role="Writer",
    goal=f"Narrate compelling tech stories around {topic}",
    verbose=True,
    backstory="""With a flair for simplifying complex topics, you craft engaging narratives that captivate
    and educate, bringing new discoveries to light in an accessible manner.""",
)

# Define the asynchronous research tasks
list_ideas = Task(
    description="List of 5 interesting ideas to explore for an article about {topic}.",
    expected_output="Bullet point list of 5 ideas for an article.",
    tools=[search_tool, ContentTools().read_content],
    agent=researcher,
    async_execution=True,
)

list_important_history = Task(
    description="Research the history of {topic} and identify the 5 most important events.",
    expected_output="Bullet point list of 5 important events.",
    tools=[search_tool, ContentTools().read_content],
    agent=researcher,
    async_execution=True,
)

# Define the writing task that waits for the outputs of the two research tasks
write_article = Task(
    description=f"Compose an insightful article on {topic}, including its history and the latest interesting ideas.",
    expected_output="A 4 paragraph article about AI in healthcare.",
    tools=[search_tool, ContentTools().read_content],
    agent=writer,
    context=[
        list_ideas,
        list_important_history,
    ],  # Depends on the completion of the two asynchronous tasks
    callback=callback_function,
)

# Define the manager's coordination task
manager_task = Task(
    description=f"""Oversee the integration of research findings and narrative development to produce a final comprehensive
    report on {topic}. Ensure the research is accurately represented and the narrative is engaging and informative.""",
    expected_output=f"A final comprehensive report that combines the research findings and narrative on {topic}.",
    agent=manager,
)

# Forming the crew with a hierarchical process including the manager
crew = Crew(
    agents=[manager, researcher, writer],
    tasks=[list_ideas, list_important_history, write_article, manager_task],
    process=Process.hierarchical,
    manager_llm=llm,
)

# Kick off the crew's work
results = crew.kickoff()

# Print the results
print("Crew Work Results:")
print(results)
