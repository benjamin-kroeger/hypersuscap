import os
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings

# Import send_message and stream_message from open_ai_call.py
from open_ai_call import send_message, stream_message

class Retriever:
    def __init__(self, db_uri, model="gpt-3.5-turbo", temperature=0):

        # TODO: Change the API Key
        self.db = SQLDatabase.from_uri(db_uri)
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.context = self.db.get_context()
        self.examples = self._get_examples()
        self.example_prompt = PromptTemplate.from_template("User input: {input}\nSQL query: {query}")
        self.example_selector = SemanticSimilarityExampleSelector.from_examples(
            self.examples,
            OpenAIEmbeddings(),
            FAISS,
            k=5,
            input_keys=["input"],
        )
        self.model_names = self._get_model_names()
    
    def _get_model_names(self):
        return self.db.run("SELECT model_name FROM configurations;")

    def _get_examples(self):
        return [
            {
                "input": "List all electric cars.", 
                "query": "SELECT * FROM configurations;"
            },
            {
                "input": "Find all cars with a power of more than 200 kW.",
                "query": "SELECT * FROM configurations WHERE power_kw > 200;"
            },
            {
                "input": "List all cars with a battery capacity of more than 70 kWh.",
                "query": "SELECT * FROM configurations WHERE battery_capacity > 70;"
            },
            {
                "input": "Find the average price of all cars.",
                "query": "SELECT AVG(initial_price) FROM configurations;"
            },
            {
                "input": "List all cars of the brand 'Tesla'.",
                "query": "SELECT * FROM configurations WHERE brand_name = 'Tesla';"
            },
            {
                "input": "How many cars have a range of more than 500 km?",
                "query": "SELECT COUNT(*) FROM configurations WHERE total_range > 500;"
            },
            {
                "input": "Find the total number of cars.",
                "query": "SELECT COUNT(*) FROM configurations;"
            },
            {
                "input": "List all cars that accelerate from 0 to 100 km/h in less than 5 seconds.",
                "query": "SELECT * FROM configurations WHERE acceleration < 5;"
            },
            {
                "input": "Who are the top 5 cars by top speed?",
                "query": "SELECT model_name, top_speed FROM configurations ORDER BY top_speed DESC LIMIT 5;"
            },
            {
                "input": "Which cars have more than 4 doors?",
                "query": "SELECT * FROM configurations WHERE doors > 4;"
            },
            {"input": "Which cars have the largest battery capacity and cost less than 50,000 Euros?", "query": "SELECT * FROM configurations WHERE battery_capacity = (SELECT MAX(battery_capacity) FROM configurations WHERE initial_price < 50000);"},
            {"input": "Which cars have the highest range and accelerate from 0 to 100 km/h in less than 5 seconds?", "query": "SELECT * FROM configurations WHERE total_range = (SELECT MAX(total_range) FROM configurations WHERE acceleration < 5);"},
            {"input": "Which cars have the shortest charging time?", "query": "SELECT * FROM configurations WHERE charge_time_dc_high = (SELECT MIN(charge_time_dc_high) FROM configurations);"},
            {"input": "Which cars have the highest power and cost less than 100,000 Euros?", "query": "SELECT * FROM configurations WHERE power_kw = (SELECT MAX(power_kw) FROM configurations WHERE initial_price < 100000);"},
            {"input": "Which cars have the most seats and cost less than 60,000 Euros?", "query": "SELECT * FROM configurations WHERE seats = (SELECT MAX(seats) FROM configurations WHERE initial_price < 60000);"},
            {"input": "Which cars have the largest luggage capacity?", "query": "SELECT * FROM configurations WHERE boot_capacity_max = (SELECT MAX(boot_capacity_max) FROM configurations);"},
            {"input": "Which cars have the highest speed and cost less than 70,000 Euros?", "query": "SELECT * FROM configurations WHERE top_speed = (SELECT MAX(top_speed) FROM configurations WHERE initial_price < 70000);"},
            {"input": "Which cars have the largest battery capacity and the highest range?", "query": "SELECT * FROM configurations WHERE battery_capacity = (SELECT MAX(battery_capacity) FROM configurations) AND total_range = (SELECT MAX(total_range) FROM configurations);"},
            {"input": "Which cars have the shortest charging time and the highest range?", "query": "SELECT * FROM configurations WHERE charge_time_dc_high = (SELECT MIN(charge_time_dc_high) FROM configurations) AND total_range = (SELECT MAX(total_range) FROM configurations);"},
            {"input": "Which cars have the highest power and the shortest charging time?", "query": "SELECT * FROM configurations WHERE power_kw = (SELECT MAX(power_kw) FROM configurations) AND charge_time_dc_high = (SELECT MIN(charge_time_dc_high) FROM configurations);"},
        ]

    def query_check(self, test_query):
        "Check if the user query is "

        # 1. Check if the query is answerable by the database context, if not, return an indication
        system_prompt = "You are an assistant which identifies, if a given user question can be answered by the database context." 
        answerable_prompt = f"""
        User question: {test_query}

        Can the question be answered by the database content?

        Here is the relevant table info: 
        {self.context["table_info"]}

        Answer (Yes/No): """

        messages = [{"role": "system", "content": system_prompt}]

        answer = send_message(answerable_prompt,'user', context=messages ,model="gpt-3.5-turbo")
        
        print("Query Check Answer: ", answer)

        return True if "Yes" in answer else False

    def query_rewrite(self, test_query, chat_history):
        "Contextualize the user query to the chat history."

        # 1. Contextualize the user query given the chat history
        system_prompt = "You are an assistant which rewrites a given user question to be more specific based on the chat history."
        cqu_prompt = f"""
        User question: {test_query}

        Chat history: {chat_history}

        Rewrite the user question to be more specific based on the chat history.

        Contextualized question: """

        # messages = chat_history 
        # Add to the beginning of the chat history
        messages = []
        messages.insert(0, {"role": "system", "content": system_prompt})

        contextualized_query = send_message(cqu_prompt, 'user', context=messages, model="gpt-3.5-turbo")

        print("Contextualized Query: ", contextualized_query)

        # 2. Adjust the query to the information in the table 

        system_prompt="""You are an assistant which adjusts a given user question with potential abstract information needs to be more adjusted to the information provided in a database. Please reduce the abstractness of the user question to fit the table information only. Here are few examples of abstract questions and their corresponding adjustment: 
       
        Abstract question: What is the most prestigous car?
        Adjusted question: What is the most expensive car?

        Abstract question: I often buy a lot in the supermarket, does it fit in the car?
        Adjusted question: What is the luggage space of the car?
        """

        final_query_prompt = f"""
        User question: {contextualized_query}

        Please adjust the user question to be more specific based on the table information.

        Table information: {self.context["table_info"]}

        Adjusted question: """

        messages = []

        messages.append({"role": "system", "content": system_prompt})

        database_ready_query = send_message(final_query_prompt, 'user', context=messages, model="gpt-3.5-turbo")

        print("Database Ready Query: ", database_ready_query)

        return database_ready_query

    def retrieve(self, test_query, chat_history=[]):

        # 1. Contextualize the user query given the chat history
        cqu = self.query_rewrite(test_query, chat_history=chat_history) 

        # 2. Query Check
        self.query_check(cqu)

        # test_query = cqu

        prompt = FewShotPromptTemplate(
            example_selector=self.example_selector,
            example_prompt=self.example_prompt,
            prefix="You are a SQLite expert. Given an input question, create a syntactically correct SQLite query to run. Unless otherwise specificed, do not return more than {top_k} rows.\n\nHere is the relevant table info: {table_info}\n\nThe following car models are available by model_name: {model_names}\n\nBelow are a number of examples of questions and their corresponding SQL queries.",
            suffix="User input: {input}\nSQL query: ",
            input_variables=["input", "top_k", "table_info", "model_names"],
        )

        print(prompt.format(input=test_query, top_k=3, table_info=self.context["table_info"], model_names=self.model_names))

        chain = create_sql_query_chain(self.llm, self.db, prompt)

        print("Prompt:", chain.get_prompts()[0])

        result = chain.invoke({"question": test_query, "model_names": self.model_names})

        print("Generated SQL Query: ", result)

        db_result = self.db.run(result)
        print("DB Run: ", db_result)

        answer_prompt = PromptTemplate.from_template(
        f"""Given the following user question, corresponding SQL query, and SQL result, answer the user question.

# Question: {test_query}
# SQL Query: {result}
# SQL Result: {db_result}
# Answer: """
)

        messages = [{"role": "system", "content": "You are an assistant which answers a given user question based on the SQL query and the SQL result."}]
        answer = send_message(answer_prompt, 'user', context=messages, model="gpt-3.5-turbo")

        print("Final Answer: ", answer)

        return answer


# example_history = [
#     {"role": "assistant", "content": "How can I help you?"},
#     {"role": "user", "content": "I'm interested in a G-wagon?"},
#     {"role": "assistant", "content": "What would you like to know about the G-wagon?"},
# ]

# example_test_query = "Does a buggy fit into the car?"

# Retriever("sqlite:///electric_configurations.db").retrieve(example_test_query, chat_history=example_history)