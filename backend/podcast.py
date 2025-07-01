import google.generativeai as genai
from langchain.agents import AgentType, initialize_agent
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
import edge_tts
from v2t import getContent

api_key = "AIzaSyBkbo1jrW6p1TuamMvnHju4JipBoK1cGfM"
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
    You are a podcast script generator who generats large podcast. Convert the following text into a two-person conversational podcast script.

    ## CONTEXT
    The script must cover ALL key ideas from the original text.
    Original Text:
    \"\"\"
    {transcript_text}
    \"\"\"

    ## STRICT OUTPUT FORMAT
    - Generate ONLY the raw dialogue strings, one per line .
    - NO speaker labels (e.g., "Host 1:").
    - Each dialogue line MUST be on a new line.
    - Alternate speakers, starting with Host 1.
    - Dont need to genarate less converstion try to cover all topics by how far it takes
    - Dont waste time with unwanted matter
    - There should be a minimum of 10 dialogues for each host.
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
    Question:
    \"\"\"
    {Question}
    \"\"\"

    ## STRICT OUTPUT FORMAT
    - Generate ONLY the raw dialogue strings, one per line ,attach \\n at ecey end of line.
    - NO speaker labels (e.g., "Host 1:").
    - Each dialogue line MUST be on a new line.
    - Alternate speakers, starting with Host 1.
    - maximum 6-8 lines each
    

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
    
    

agent = initialize_agent(
    tools=[script,answerscript],
    llm=ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.3,
        google_api_key=api_key
    ),
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False,
)

async def getScript(url):
    video_url = "https://youtu.be/Fy1UCBcgF2o"
    transcript ,document= getContent(url) 
    transcript_input = transcript
    

    prompt = f"Use the script tool to get a podcast script from this transcript: {transcript_input}. Return ONLY the raw script output from the tool, nothing else."

    response = script.invoke({"transcript_text": transcript_input})
    print("\n--- Initial Podcast Created ---")
    print(response)
    return response 

def qA(user_question : str ,script : str):
    prompt = f"Use the answerscript tool to generate an answer for this question: {user_question} based on script {script}. Return ONLY the raw answer script output from the tool,nothing else."
    answer_response = agent.invoke({"input": prompt})
    print("\n--- Question Answer Audio Created ---")
    print(answer_response['output'])
    return answer_response['output']