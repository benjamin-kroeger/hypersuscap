import os
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings

import random

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
        self.product_groups = self._get_product_groups()
        self.vehicle_classes = self._get_vehicle_classes()
        self.brands = self._get_brands()
        self.table_info = """
The following is a list of all column names, some contain a description:
        market_id - The unique identifier of the market.
        model_id - The unique identifier of the model.
        initial_price - The initial price of the car.
        net_initial_price - The net initial price of the car.
        tax_amount - The tax amount of the car price.
        product_group - The product group of the car. Like 'Gelaendewagen' or 'Limousine'.
        fuel_type - Only electric cars are included in this table.
        power_hp 
        power_kw 
        continuous_power_kw 
        emission_standard - The EU emission standard of the car indicates it's CO2 emissions.
        nominal_torque 
        type_of_propulsion 
        battery_type 
        battery_capacity 
        energy_content 
        charging_capacity_ac 
        charging_capacity_dc 
        length 
        width 
        height
        width_without_mirrors 
        turn_circle 
        luggage_space_front_seat  - The luggage space of the car for the front seat.
        boot_capacity_max - The maximum boot capacity of the car for the luggage.
        boot_capacity_min - The minimum boot capacity of the car for the luggage.
        wheel_base 
        front_gauge 
        rear_gauge 
        transmission_category 
        acceleration 
        top_speed 
        doors 
        seats 
        actual_mass 
        payload 
        kerb_weight 
        charge_time_ac_high 
        charge_time_dc_high 
        co2_class 
        total_range 
        maximum_weight - The maximum weight of the car with luggage.
        front_tyres 
        back_tyres 
        front_brakes
        rear_brakes
        front_suspension
        rear_suspension
        model_name  - The name of the car model from Mercedes-Benz.
        brand_name - The name of the sub-brand of Mercedes-Benz. E.g. "Maybach" or "AMG"
        vehicle_class - The class of the car. E.g. "G-Klasse"
        facelift 
        all_terrain 
        steering_position 
"""
    
    def _get_model_names(self):
        return self.db.run("SELECT model_name FROM configurations;")
    
    def _get_brands(self):
        return self.db.run("SELECT DISTINCT brand_name FROM configurations;")
    
    def _get_product_groups(self):
        return self.db.run("SELECT DISTINCT product_group FROM configurations;")

    def _get_vehicle_classes(self):
        return self.db.run("SELECT DISTINCT vehicle_class FROM configurations;")

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
        # Define system prompt
        system_prompt = f"You are an assistant which rewrites a given user question to be more specific based on the chat history and database information. Please keep the adjusted queries very simple, it should only consider entities and information which can really be extracted from the database, so no information like 'What is the most luxurious car?'. Reduce the complexity of the user queries. Always rewrite the user query to match somehow the database schema.\n\nHere is the relevant table info: {self.table_info}\n\nThe following car models are available by model_name: {self.model_names}\n\nThe following vehicle classes are available by vehicle_class: {self.vehicle_classes}\n\nThe following product groups are available by product_group: {self.product_groups}\n\nThe followin brands are available by brand_name:{self.brands}\n\nBelow are a number of examples of questions and their adjusted queries."

        adjust_examples = [
            {"abstract": "Which Mercedes electric vehicle model has the highest top speed?", "adjusted": "Which car model has the highest top speed?"},
            {"abstract": "How do the EQS series models differ?", "adjusted": "Provide me with all information about cars contaning 'EQS' in the model name."},
            {"abstract": "I often buy a lot in the supermarket, does it fit in the car?", "adjusted": "What is the luggage space of the car?"},
        ]

        # Add examples to system prompt
        for example in adjust_examples:
            system_prompt += f"\n\nAbstract question: {example['abstract']}\nAdjusted question: {example['adjusted']}"


        messages = [{"role": "system", "content": system_prompt}]

        answerable_prompt = f"""
        User question: {test_query}

        Rewrite the user question to be more specific based on the database data.

        Adjusted question: """


        answer = send_message(answerable_prompt,'user', context=messages ,model="gpt-3.5-turbo")
        
        print("Query Adjustment: ", answer)

        return answer
    
    def query_rewrite(self, test_query, chat_history, num_iterations=3):
        "Contextualize the user query to the chat history."

        system_prompt = "You are an assistant which rewrites a given user question to be contextualized based on the chat history."

        # Define contextualization prompt
        cqu_prompt = f"""Rewrite the last user question to be contextualized.

        Contextualized question: """

        context = chat_history.copy()
        context.extend([{"role": "user", "content": test_query}])

        # Initialize list to store contextualized queries
        contextualized_queries = []

        # Loop over iterations to generate multiple contextualized queries with randomness
        for i in range(num_iterations):
            # Randomly select temperature for each iteration
            # temperature = random.uniform(0.3, 0.7)
            temperature = 0.6 
            
            # Generate contextualized query
            contextualized_query = send_message(cqu_prompt, 'user', context=context, model="gpt-3.5-turbo", max_tokens=400, temperature=temperature)
            
            # Append contextualized query to list
            contextualized_queries.append(contextualized_query)

        return contextualized_queries

    def retrieve(self, test_query, chat_history=[]):

        # 1. Contextualize the user query given the chat history
        cqu = self.query_rewrite(test_query, chat_history=chat_history, num_iterations=1) 

        print("Contextualized Queries: ", cqu)

        adjusted_queries = []

        for query in cqu:
            adjusted_query = self.query_check(query)
            adjusted_queries.append(adjusted_query)

        # 2. Get Database answer to the query
        list_of_sql_queries = []
        for query in adjusted_queries:
            for i in range(10):
                list_of_sql_queries.append(self.retrieve_query_sql(query))
        
        # 3. Select the best answer from the list of answers
        answer = self.select_best_answer(test_query, chat_history, list_of_sql_queries)

        return answer

    def select_best_answer(self, test_query, chat_history, list_of_sql_queries=[]):

        answer_prompt =f"""Given the following user question, conversation context, corresponding SQL query, and SQL result, answer the user question. Make sure to always point out which car model or car models you're referring to in your answer, never just state values or metrics without matching it to a car model. All metrics are german standards e.g. km/h, kWh, kW, €, etc.
    # Question: {test_query}
    # Chat History: {chat_history}"""
            
        # enumerate over pairs
        for i, pair in enumerate(list_of_sql_queries):
            answer_prompt+=f"""
    # Alteranative {i+1}:
    # SQL Query: {pair["query"]}
    # SQL Result: {pair["result"]}
    """

        answer_prompt+=f"""# Answer: """

        messages = [{"role": "system", "content": "You are an assistant which answers a given user question based on the SQL query and the SQL result."}]
        if len(answer_prompt) > 16000:
            answer_prompt = answer_prompt[:14000]
        answer = send_message(answer_prompt, 'user', context=messages, model="gpt-3.5-turbo", max_tokens=800)

        return answer
    
    def retrieve_query_sql(self, test_query):

        prompt = FewShotPromptTemplate(
            example_selector=self.example_selector,
            example_prompt=self.example_prompt,
            prefix="You are a SQLite expert. Given an input question, create a syntactically correct SQLite query to run. Unless otherwise specificed, do not return more than {top_k} rows.\n\nHere is the relevant table info: {table_info}\n\nThe following car models are available by model_name: {model_names}\n\nThe following vehicle classes are available by vehicle_class: {vehicle_classes}\n\nThe following product groups are available by product_group: {product_groups}\n\nBelow are a number of examples of questions and their corresponding SQL queries.",
            suffix="User input: {input}\nSQL query: ",
            input_variables=["input", "top_k", "table_info", "model_names", "vehicle_classes", "product_groups"],
        )

        chain = create_sql_query_chain(self.llm, self.db, prompt)

        result = chain.invoke({"question": test_query, "model_names": self.model_names, "vehicle_classes": self.vehicle_classes, "product_groups": self.product_groups, "table_info": self.context["table_info"], "top_k": 5})

        try:
            db_result = self.db.run(result)
        except:
            db_result = None

        return {"query": result, "result": db_result}
