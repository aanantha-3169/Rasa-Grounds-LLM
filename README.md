
# Rasa Grounds LLMs

## Overview
### LLMs have made users:
1.<b>Ask more questions</b>, every bot should be able to chat <br>
2.<b>Receive human like responses</b>, bots speak my language <br>
3.<b>Expect quick, accurate facts</b>, hallucination is not tolerated 

Solutions involving vector databases are the go to when creating specilised agents with domain knowledge. However inaccuracies(hallucinations) and scaling such solutions can be challenging.

This project aim at creating an agent that has domain specific knowledge coming from a graph database that can be used to answer users broad questions about a given product/service. The goal is to strike a balance between providing response accuracy, having control over responses given, creating an intelligent agent and deliveriing great user experience.

## Solution([Demo Video](https://drive.google.com/file/d/129ibe-F-HTpq3VWVWQCLH0cNuoBcoZ--/view?usp=sharing))

<img width="710" alt="Screenshot 2023-07-21 at 09 13 44" src="https://github.com/aanantha-3169/Rasa-Grounds-LLM/assets/78289929/c54f7ee3-4c56-40c1-b16c-27e6122fd331">

By integrating Rasa with TypeDB, Rasa-Grounding-LLM enables the chatbot agent to understand user intents and generate precise queries to interact with the TypeDB database. The system acts as a mediator, allowing users to ask complex questions and receive meaningful responses by leveraging the expressive power of both Rasa's natural language processing capabilities and the semantic graph database of TypeDB.

The way we instruted the GPT 3.5 API that enables it to produce queries is as follows:

#### 1. Define role + provide database schema:<br>
                {"role": "system", "content": "You are typeql query generator. You will generator a query based on users questions." + "\n" +
                "The schema of the database that you can construct your queries from is as below:" + "\n" + self.my_schema +"\n" +

#### 2. Provide rules of how to query<br>
                "Notes on queries in typedb:" + "\n" +
                "1.Role-players in a relation must be distinguished with a comma, not a semicolon. " + "\n" + 
                "2.Attribute ownership should be written as has attribute-type attribute-value or has attribute-type $variable. You need to define the variable before you use it." + "\n" + 
                "3.The correct syntax for relations in TypeDB is as follows:($role1: $player1, $role2: $player2) isa $relation" + "\n" + 
                "4.TypeQL does not support ordering or sorting of results directly in the query language itself." + "\n" + 
                "Your response should only be in form of a typeql query that you answers the question. If the question is not answerable in typeql, return  'N/A'"},

#### 3. Example of questions and queries generated
                {"role": "user", "content": "What factors should I consider when getting a credit card?"},
                {"role": "assistant", "content": "match $x type credit-card, owns $a; get $a;"},
                {"role": "user", "content": "What are the benefits of getting a credit card?"},
                {"role": "assistant", "content": "match $p isa credit-card-pros, has pro $pr; get $pr;"},

## Next Steps

The project is a simple demostrastion of the possibility of using LLMs to bridge the gap in understanding between users questions and the responses generated from intelligent agents. Areas that will be explore next are:
1. Entities recognition; Leverage Rasa entity extractor to help identiy entities and use it for query generation <br>
2. Better prompting;  Using more relevant information eg. relevant parts of the schema, entities in question etc. <br>
3. Larger Context;  Test for more complex relationships and larger knowledge base <br>

