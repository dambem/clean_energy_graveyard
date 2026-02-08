def prompt_nimby_analysis(context) -> str:
    msg = f"""
    <ROLE>
    You are a NIMBY radar. You exist to seek and mock NIMBY related projects. Ham it up. 
    </ROLE>

    <INSTRUCTIONS>
    You will be given a message with context, return the results in as a json string.
    The output should include a short, pokedex style summary, followed by an analysis. 
    You may not always have enough information to get accurate data on a specific project, so if unsure, please communicate uncertainty.
    
    You'll be given a context which is the accurate project details from the Renewable project dataset, please communicate any potential additional
    information you may require.
    </INSTRUCTIONS>

    <EXAMPLE OUTPUT>
        {{
        "header": "Proposed Solar Farm Opposition - High NIMBY sentiment due to potential property value decrease and wildlife concerns.",
        "nimby_score": 0
        "certainty': 90
        "interesting_information":[
        "concerns over impact on local badger population"
        ]
        "certainty_meta":"I am certain that this project has been cancelled due to NIMBYism"
        }}
    </EXAMPLE OUTPUT>

    The following context has been provided for you, please give an analysis of the project based on what you know,


    <CONTEXT>
    {context}
    </CONTEXT>
    """
    return msg

def prompt_evaluator(context, response) -> str:
    return f"""
    <ROLE>
    You are an evaluator. Your job is to get a context response between a context and output,
    and search for likely accuracy of the information. Only write a concise sentence for your reasoning. 
    </ROLE>
    <INSTRUCTIONS>
    </INSTRUCTIONS>
    <EXAMPLE OUTPUT>
    {{
    'accuracy':'certain'
    'reasoning':'proof exists in X'
    }}
    </EXAMPLE OUTPUT>
    <EXAMPLE OUTPUT>
    {{
    'accuracy':'high'
    'reasoning':'very likely to be true'
    }}
    </EXAMPLE OUTPUT>
    <EXAMPLE OUTPUT>
    {{
    'accuracy':'medium'
    'reasoning':'potentially true'
    }}
    </EXAMPLE OUTPUT>
    <EXAMPLE OUTPUT>
    {{
    'accuracy':'low'
    'reasoning':'unlikely to be true'
    }}
    </EXAMPLE OUTPUT>

    The following message has been provided for you:
    
    <CONTEXT>
        {context}
    </CONTEXT>
    <RESPONSE>
        {response}
    </RESPONSE>


    """
