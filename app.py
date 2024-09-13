import json
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

GOOGLE_API_KEY = "AIzaSyCJ3mrkXKWMNbnQbmjch58tBpYru75xu6Q"
genai.configure(api_key=GOOGLE_API_KEY)

quiz_no = int(input("Enter the number of questions you want in the quiz: "))
prompt_template = f"""You are a YouTube video summarizer. You will be taking a transcript text,
summarizing the entire video in points (around 350 words) and DO NOT use any special symbols in between like '**', generating {quiz_no} questions with options. Make sure that questions start with Q1, Q2 and so on. Quiz should start with labeled Quiz Questions and the answer key should be generated separately.
The transcript text is: """

def get_transcript(youtube_url, preferred_languages):
    try:
        video_id = youtube_url.split('v=')[-1]
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=preferred_languages)
        transcript = ' '.join([item['text'] for item in transcript_data])
        return transcript
    except Exception as e:
        return None

def generate_summary_and_quiz(transcript, prompt):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content(prompt + transcript)
    return response.text

def parse_quiz_and_answers(summary_quiz_text):
    if summary_quiz_text:
       
        cleaned_text = summary_quiz_text.replace('**', '').replace('\n', ' ')

    
        if cleaned_text:
            parts = cleaned_text.split("Quiz Questions:")
            quiz_section = parts[1].split("Answer Key:")[0].strip() if len(parts) > 1 and "Answer Key:" in parts[1] else parts[1].strip()
            answer_section = parts[1].split("Answer Key:", 1)[1].strip() if len(parts) > 1 and "Answer Key:" in parts[1] else ""
        else:
            return {}, {} 

        quiz_questions = {}
        answer_key = {}
        question_count = 1
        current_question = None
        options = []

       
        lines = quiz_section.split('Q')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Handle questions and options
            if '?' in line:
                if current_question:
                    # Ensure exactly 4 options are present, pad with empty strings if needed
                    while len(options) < 4:
                        options.append("")
                    quiz_questions[f"question{question_count}"] = {
                        "question": current_question,
                        "options": {
                            "a": options[0] if len(options) > 0 else "",
                            "b": options[1] if len(options) > 1 else "",
                            "c": options[2] if len(options) > 2 else "",
                            "d": options[3] if len(options) > 3 else ""
                        }
                    }
                    question_count += 1

                
                parts = line.split('?')
                current_question = f"Q{parts[0].strip()}?"

                
                option_text = parts[1]
                options = [opt.strip() for opt in option_text.split('.') if opt.strip()]

                # Ensure options do not exceed 4
                options = options[:4]
            else:
                
                option_text = line
                options.extend([opt.strip() for opt in option_text.split('.') if opt.strip()])

       
        if current_question:
            while len(options) < 4:
                options.append("")
            quiz_questions[f"question{question_count}"] = {
                "question": current_question,
                "options": {
                    "a": options[0] if len(options) > 0 else "",
                    "b": options[1] if len(options) > 1 else "",
                    "c": options[2] if len(options) > 2 else "",
                    "d": options[3] if len(options) > 3 else ""
                }
            }

        
        answer_count = 1
        if answer_section:
            for answer in answer_section.split('Q'):
                answer = answer.strip()
                if ':' in answer:
                    answer_key[f"answer{answer_count}"] = {"answer": answer.split(':', 1)[1].strip()}
                    answer_count += 1

        return quiz_questions, answer_key
    else:
        return {}, {}  

def generate_json(youtube_link, quiz_no):
    transcript = get_transcript(youtube_link, ['hi'])

    if not transcript:
        transcript = get_transcript(youtube_link, ['en'])

    if transcript:
        summary_and_quiz = generate_summary_and_quiz(transcript, prompt_template)

        
        summary_and_quiz_cleaned = summary_and_quiz.replace('**', '').replace('\n', ' ')

        summary_part = summary_and_quiz_cleaned.split("Quiz Questions:")[0].strip()
        quiz_questions, answer_key = parse_quiz_and_answers(summary_and_quiz_cleaned)

        result_json = json.dumps({
            'youtube_link': youtube_link,
            'summary': summary_part,
            'quiz': quiz_questions,
            'answer_key': answer_key
        }, indent=4)

        return result_json
    else:
        return json.dumps({'error': 'Failed to extract transcript in both Hindi and English.'}, indent=4)

def main():
    youtube_link = input("Enter the YouTube video link: ")
    result_json = generate_json(youtube_link, quiz_no)
    print(result_json)

if __name__ == "__main__":
    main()
