import openai
from rasa_sdk import Action
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List
from rasa_sdk import Tracker
from .credential import OpenAICredentials
from .schema import Schema
from typedb.client import TypeDB, SessionType, TransactionType

class QueryGenerator:
    def __init__(self):
        # Your initialization code here
        self.schema = Schema()
        self.my_schema = self.schema.schema
        self.credentials = OpenAICredentials()
        openai.api_key = self.credentials.api_key

    def get_query(self, question):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "system", "content": "You are typeql query generator. You will generator a query based on users questions." + "\n" +
                "The schema of the database that you can construct your queries from is as below:" + "\n" + self.my_schema +"\n" +
                "Notes on queries in typedb:" + "\n" + 
                "1.Role-players in a relation must be distinguished with a comma, not a semicolon. " + "\n" + 
                "2.Attribute ownership should be written as has attribute-type attribute-value or has attribute-type $variable. You need to define the variable before you use it." + "\n" + 
                "3.The correct syntax for relations in TypeDB is as follows:($role1: $player1, $role2: $player2) isa $relation" + "\n" + 
                "4.TypeQL does not support ordering or sorting of results directly in the query language itself." + "\n" + 
                "Your response should only be in form of a typeql query that you answers the question. If the question is not answerable in typeql, return  'N/A'"},
                {"role": "user", "content": "What factors should I consider when getting a credit card?"},
                {"role": "assistant", "content": "match $x type credit-card, owns $a; get $a;"},
                {"role": "user", "content": "What are the benefits of getting a credit card?"},
                {"role": "assistant", "content": "match $p isa credit-card-pros, has pro $pr; get $pr;"},
                {"role": "user", "content": "How many banks are offering a credit card?"},
                {"role": "assistant", "content": "match $b isa bank; $c isa credit-card; (card-issuer: $b, issued-card: $c) isa issuance; get $b; count;"},
                {"role": "user", "content":question}
                ],
            temperature=0,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].message['content']

class QueryTranslator:
    def __init__(self):
        # Initialization code here
        self.credentials = OpenAICredentials()
        openai.api_key = self.credentials.api_key

    def get_trans(self, question,answer):
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
                {"role": "system", "content": "You are a typedb query output translator. You will answer users question in natural language using information from 2 inputs, users question and typedb query output. Do not use any information beyond the 2 inputs to construct your answer. If the question is not answerable, return  'N/A'"},
                {"role": "user", "content": "Question: What is the name of the bank that offers a card with an interest rate of 0.15? Output: [{'name': 'Bank A'}]"},
                {"role": "assistant", "content": "The bank that offers a card with an interest rate of 0.15 is Bank A."},
                {"role": "user", "content":f"Question: {question} Output:{answer}"}
                ],
        temperature=0,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )

        return response.choices[0].message['content']
        
class ActionTextResponse(Action):
    def name(self) -> Text:
        return "action_get_info"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get user's latest message
        latest_message_text = tracker.latest_message['text']

        # Initialize QueryGenerator and QueryTranslator
        query_gen = QueryGenerator()
        query_trans = QueryTranslator()

        # Generate TypeDB query
        try:
            query = query_gen.get_query(latest_message_text)
            print(query)

            #Send request to database to get output
            with TypeDB.core_client("localhost:1729") as client:
                with client.session("credit_card", SessionType.DATA) as session:
                    with session.transaction(TransactionType.READ) as transaction:
                        iterator = transaction.query().match(query)
                        
                        #Unpack output from mapping. Currently only handles attributes
                        result_list = []
                        for ans in iterator:
                            result_dict = {}
                            for variable in ans.map().keys():
                                #print(variable)
                                result_dict[variable] = str(ans.get(variable).as_attribute().get_value())
                            result_list.append(result_dict)
                            print(result_list)
             

            answer = query_trans.get_trans(latest_message_text,result_list)
            print(answer) 
            # Return the translated query output
            dispatcher.utter_message(text= answer)
            return []
        except Exception as e:
            dispatcher.utter_message(text=f"Failed to generate text TypeDB query: {e}")
            return []

class ActionNumericResponse(Action):
    def name(self) -> Text:
        return "action_get_data"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get user's latest message
        latest_message_text = tracker.latest_message['text']

        # Initialize QueryGenerator and QueryTranslator
        query_gen = QueryGenerator()
        query_trans = QueryTranslator()

        # Generate TypeDB query
        try:
            query = query_gen.get_query(latest_message_text)
            print(query)

            #Send request to database to get output
            with TypeDB.core_client("localhost:1729") as client:
                with client.session("credit_card", SessionType.DATA) as session:
                    with session.transaction(TransactionType.READ) as transaction:
                        iterator = transaction.query().match_aggregate(query) 
                        ans = iterator.get()
                        numer = ans._int_value
             

            answer = query_trans.get_trans(latest_message_text,numer)
            print(answer) 
            # Return the translated query output
            dispatcher.utter_message(text= answer)
            return []
        except Exception as e:
            dispatcher.utter_message(text=f"Failed to generate numeric TypeDB query: {e}")
            return []



        



