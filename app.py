from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import json

formatter = TextFormatter()

def get_transcript(youtube_url):
    try:
        video_id = youtube_url.split('v=')[-1]
        transcript = None
        language = None

        # Try to get Hindi transcript first
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['hi'])
            language = 'hi'
        except:
            # If Hindi is not available, fall back to English
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
                print(transcript)
                language = 'en'
            except:
                print("Neither Hindi nor English transcript is available.")
                return None, None

        return formatter.format_transcript(transcript), language
    except Exception as e:
        print(f"Error fetching transcript: {str(e)}")
        return None, None


def generate_summary_and_quiz(transcript, num_questions, language, difficulty):
    try:
        prompt = f"""
        Summarize the following transcript by identifying the key topics covered, and provide a detailed summary of each topic in 6 7 sentences.
        Each topic should be labeled clearly as "Topic X", where X is the topic name. Provide the full summary for each topic in English, even if the transcript is in a different language.

        After summarizing, create a quiz with {num_questions} multiple-choice questions in English, based on the transcript content.
        Only generate {difficulty} difficulty questions. Format the output in JSON format as follows:

        {{
            "summary": {{
                "topic1": "value1",
                "topic2": "value2",
                "topic3": "value3"
            }},
            "questions": {{
                "{difficulty}": [
                    {{
                        "question": "What is the capital of France?",
                        "options": ["Paris", "London", "Berlin", "Madrid"],
                        "answer": "Paris"
                    }},
                    {{
                        "question": "What is the capital of Germany?",
                        "options": ["Paris", "London", "Berlin", "Madrid"],
                        "answer": "Berlin"
                    }}
                ]
            }}
        }}

        Transcript: {transcript}
        """

        # Invoke language model (assuming you have integrated some LLM API)
        # Corrected the integration of the hypothetical ChatGroq model to a general placeholder as your API key seems placeholder
        # Replace with the actual LLM invocation code
        llm = ChatGroq(
            model="llama-3.1-70b-versatile",
            temperature=0,
            groq_api_key="MEIN NAHI BATAUNGA"
        )
        response = llm.invoke(prompt)
        return response.content

    except Exception as e:
        print(f"Error generating summary and quiz: {str(e)}")
        return None


if __name__ == "__main__":
    youtube_link = input("Enter YouTube video URL: ")
    transcript, language = get_transcript(youtube_link)
    
    if transcript:
        num_questions = int(input("Enter the number of questions you want in the quiz: "))
        difficulty = input("Enter quiz difficulty level (easy, medium, hard): ").lower()
        
        # Call generate_summary_and_quiz with obtained transcript and inputs
        summary_and_quiz = generate_summary_and_quiz(transcript, num_questions, language, difficulty)
        
        if summary_and_quiz:
            print("Generated Summary and Quiz:")
            print(summary_and_quiz)
        else:
            print("Failed to generate the summary and quiz.")
    else:
        print("Transcript could not be fetched.")
