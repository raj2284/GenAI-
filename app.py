import json
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

GOOGLE_API_KEY = "AIzaSyCJ3mrkXKWMNbnQbmjch58tBpYru75xu6Q"  
genai.configure(api_key=GOOGLE_API_KEY)

quiz_no = int(input("Enter the number of questions you want in the quiz: "))


prompt_template = f"""You are a YouTube video summarizer. You will be taking a transcript text,
summarizing the entire video, providing the important summary in points in around 350 words, 
and also generating a quiz of {quiz_no} questions for test along with answer keys.
The transcript text will be : """


def get_transcript(youtube_url, preferred_languages):
    try:
        video_id = youtube_url.split('v=')[-1]
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=preferred_languages)
        transcript = ' '.join([item['text'] for item in transcript_data])
        return transcript
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None


def generate_summary_and_quiz(transcript, prompt):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content(prompt + transcript)
    return response.text

# Convert the summary and quiz into JSON format
def generate_json(youtube_link, quiz_no):
    
    transcript = get_transcript(youtube_link, ['hi'])

    
    if not transcript:
        print("Hindi transcript not available, trying English...")
        transcript = get_transcript(youtube_link, ['en'])

    if transcript:
      
        summary_and_quiz = generate_summary_and_quiz(transcript, prompt_template)
        
      
        result_json = json.dumps({
            'youtube_link': youtube_link,
            'quiz_number': quiz_no,
            'summary_and_quiz': summary_and_quiz
        }, indent=4)
        
        return result_json
    else:
        return json.dumps({
            'error': 'Failed to extract transcript in both Hindi and English.'
        }, indent=4)

def main():
    youtube_link = input("Enter the YouTube video link: ")
    result_json = generate_json(youtube_link, quiz_no)
    print(result_json)

if __name__ == "__main__":
    main()
