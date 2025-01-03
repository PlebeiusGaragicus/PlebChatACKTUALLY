import json

# Markdown text to explain this construct
CONSTRUCT_INFORMATION = """
**Chatbot Agent**

Hi, I'm just some agent dude...

Try `/usage` for a list of commands.
"""


# Markdown text to explain the commands available
USAGE = """
/version                  Get the version of the agent

/info, /about             Get information about the agent

/draw                     Get the graph of the agent

/help, /usage             Get a list of commands

/debug                    Get debug information
"""



def handle_commands(request):
    split = request.user_message.split(" ")
    command = split[0][1:].lower() # Remove the slash and take the first word

######################################
# STANDARD COMMANDS FOR EVERY AGENT
######################################
    if command == "version":
        from .VERSION import VERSION
        yield f"data: Version `{VERSION}`\n\n"

    elif command == "info" or command == "about":
        yield f"data: {CONSTRUCT_INFORMATION}\n\n"

    elif command == "usage" or command == "help":
        # Send entire usage text as a single event
        response = f"Available commands:\n```\n{USAGE.strip()}```"
        response = response.replace('\n', '\\n')
        yield f"data: {response}\n\n"

    # elif command == "draw":
    #     from graph import GRAPH_ASCII
    #     yield f"```\n{GRAPH_ASCII}\n```"

    elif command == "debug":
        debug_info = f"# body:\n```json\n{json.dumps(request.body, indent=4)}\n```\n# model_id:"
        debug_info = debug_info.replace('\n', '\\n')
        yield f"data: {debug_info}\n\n"

######################################
# CUSTOM COMMANDS TO THIS AGENT
######################################

    else:
        response = f"Command not found.\nAvailable commands:\n```\n{USAGE.strip()}```"
        response = response.replace('\n', '\\n')
        yield f"data: {response}\n\n"
