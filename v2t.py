from langchain_community.document_loaders import YoutubeLoader
from langchain_community.document_loaders.youtube import TranscriptFormat

video_url = "https://www.youtube.com/watch?v=LKCVKw9CzFo"

def getContent(url):
    loader = YoutubeLoader.from_youtube_url(
        url, 
        add_video_info=False, 
        transcript_format=TranscriptFormat.TEXT
    ) 
    
    documents = loader.load()
    ans=''
    for i, doc in enumerate(documents):
        print(f"\n--- Document {i+1} ---")
        ans+=doc.page_content  
    return ans,documents
