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

def prompt_reseacher(context) -> str:
    return f"""
    <ROLE>
    You are an investigator, based on the context provided, your job is to find an article via websearch that most likely relates to the topic.
    If multiple are found, respond with multiple articles as necssary.

    Please note - Every project you've been given has been cancelled/stopped. Your goal is to try to locate a potential reason for doing so, and whether it relates to nimbyism.
    Your goal is to find out who caused it, whether it's an organised group, council etc.

    If it's a not newsworthy story, you are free to return nothing for the potential sources, and respond that it's unlikely it's in the news.
    
    </ROLE>
    <INSTRUCTION>
    Use the web search tool provided to you to research this.

    You will be given a response type containiing the following:

    {{
    summary: str - place a summary of finding here (concise, 1-2 sentences),
    potential_sources: list[str] - a list of links to specific web-pages, only those you think are related to the project.
    likelihood: str - low/medium/high - a certainty estimate for whether what you found is the correct one.
    }}

    </INSTRUCTION>
    <CONTEXT>
    {context}
    </CONTEXT>

    """