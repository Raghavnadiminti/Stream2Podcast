import google.generativeai as genai
from langchain.agents import AgentType, initialize_agent
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
import edge_tts
from v2t import getContent


genai.configure(api_key=api_key)


@tool
def script(transcript_text: str) -> str:
    """
    Generates a two-person podcast script from a given text.
    The output is a single string with each line of dialogue separated by a newline character.
    This is the first tool to be used in the chain.
    """
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    prompt = f"""
    ## TASK
    You are a podcast script generator. Convert the following text into a two-person conversational podcast script.

    ## CONTEXT
    The script must cover ALL key ideas from the original text.
    *Original Text:*
    \"\"\"
    {transcript_text}
    \"\"\"

    ## STRICT OUTPUT FORMAT
    - Generate ONLY the raw dialogue strings, one per line.
    - NO speaker labels (e.g., "Host 1:").
    - Each dialogue line MUST be on a new line.
    - Alternate speakers, starting with Host 1.
    - Dont need to genarate less converstion try to cover all topics by how far it takes
    - Dont waste time with unwanted matter
    """
    try:
        response = model.generate_content(prompt)
        if response.text:
            lines = [line.strip() for line in response.text.strip().split('\n') if line.strip()]
            return '\n'.join(lines)
        raise ValueError("Empty response from Gemini API")
    except Exception as e:
        return f"Error generating script: {str(e)}"

@tool
def answerscript(Question: str) -> str:
    """
    Generates a two-person conversational answer script for a question asked during podcast.
    The output is a single string with each line of dialogue separated by a newline character.
    Both hosts provide a direct answer to the question.
    """
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    prompt = f"""
    ## TASK
    Generate a SHORT two-person conversation where both hosts directly answer a listener's question.

    ## CONTEXT
    A listener has asked this question during the podcast:
    *Question:*
    \"\"\"
    {Question}
    \"\"\"

    ## STRICT OUTPUT FORMAT
    - Generate ONLY the raw dialogue strings, one per line.
    - NO speaker labels (e.g., "Host 1:").
    - Each dialogue line MUST be on a new line.
    - Alternate speakers, starting with Host 1.
    - Maximum 6-8 lines total

    ## CONVERSATION STYLE
    - Host 1: Briefly acknowledge and start answering ("Great question! The answer is...")
    - Host 2: Continue or add to the answer ("Exactly, and I'd add that...")
    - Host 1: Provide additional detail or example ("For instance...")
    - Host 2: Conclude the answer ("So in summary..." or "Hope that helps!")

    ## CRITICAL RULES
    - NO new questions from either host
    - NO "What do you think?" or similar question prompts
    - ONLY provide direct answers to the specific question
    - Keep it conversational but focused on answering
    - End definitively, don't open new discussion topics
    """
    try:
        response = model.generate_content(prompt)
        if response.text:
            lines = [line.strip() for line in response.text.strip().split('\n') if line.strip()]
            return '\n'.join(lines)
        raise ValueError("Empty response from Gemini API")
    except Exception as e:
        return f"Error generating answer script: {str(e)}"



def audio(script_text: str) -> str:
    """
    Generates an audio file from a script.
    The input MUST be a single string containing dialogue lines separated by newlines.
    This tool takes the output from the 'script' tool to create the final podcast.
    """
    text_list = [line.strip() for line in script_text.strip().split('\n') if line.strip()]
    
    if not text_list:
        return "Error: The provided script was empty. Cannot generate audio."

    all_audio = b""
    male_voice = "en-US-AndrewNeural"
    female_voice = "en-US-AriaNeural"
    
    for i, text in enumerate(text_list):
        voice = male_voice if i % 2 == 0 else female_voice
        
        communicate = edge_tts.Communicate(text, voice)
        
        for chunk in communicate.stream_sync():
            if chunk["type"] == "audio":
                all_audio += chunk["data"]
    
    return all_audio 
    
    return f"Successfully created podcast audio file at: {output_file}"

agent = initialize_agent(
    tools=[script,answerscript],
    llm=ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.3,
        google_api_key=api_key
    ),
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

async def getScript(url):
    video_url = "https://youtu.be/Fy1UCBcgF2o"
    transcript ,document= getContent(url) 
    transcript_input = transcript
    

    prompt = f"""
    1. take the following text and generate a podcast script using the 'script' tool and give script as output: "{transcript_input} " 
    """
    response = agent.invoke({"input": prompt})
    print("\n--- Initial Podcast Created ---")
    print(response['output'])
    return response['output']
    # user_question = input("\nEnter your question about the podcast: ")
    
    # answer_prompt = f"""
    # 1. First, use the 'answerscript' tool to generate a conversational answer script for this question: "{user_question} remember you not use 'script' tool since it dont answer specific question only create discussion"
    # 2. Then, take the entire answer script output from the first step and use it as the input for the 'audio' tool to generate the answer audio file.
    # """
    # answer_response = agent.invoke({"input": answer_prompt})
    # print("\n--- Question Answer Audio Created ---")
    # print(answer_response['output'])
    
    # print("\n--- Agent Final Output ---")
    # print("Initial podcast and question answer audio files have been generated successfully!")
