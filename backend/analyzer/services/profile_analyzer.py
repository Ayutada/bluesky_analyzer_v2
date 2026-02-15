import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

# 1. Load API Key from .env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))

# Check if Key is loaded successfully
if not os.getenv("GOOGLE_API_KEY"):
    print("Error: Please check the .env file to ensure GOOGLE_API_KEY is filled in correctly!")

# 2. Configure Model
# Chat Model: Use Google Gemini 2.5 Flash-Lite
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite", 
    temperature=0
)

class PersonalityAnalysis(BaseModel):
    mbti: str = Field(description="Inferred MBTI type, e.g. INTJ")
    animal: str = Field(description="Inferred Spirit Animal figure, e.g. Black Panther")
    description: str = Field(description="Brief personality portrait description, about 200-300 words")

def analyze_personality(text_content, lang="cn"):
    """
    Analyze MBTI and spirit animal based on user input text content.
    Return data in JSON format.
    Args:
        text_content (str): User profile and post content
        lang (str): Target language code ('cn', 'jp', 'en')
    """
    parser = JsonOutputParser(pydantic_object=PersonalityAnalysis)
    
    # Determine language instruction based on lang parameter
    lang_instruction = "IMPORTANT: The content of your analysis (mbti, animal, description) MUST BE IN CHINESE (Simplified). For the 'animal' field, output ONLY the Chinese name (e.g. '海狸'), DO NOT include Pinyin, English, or parentheses. ensure the JSON keys ('mbti', 'animal', 'description') remain in ENGLISH."
    if lang == "jp":
        lang_instruction = "IMPORTANT: The content of your analysis (mbti, animal, description) MUST BE IN JAPANESE. For the 'animal' field, output ONLY the Japanese name (use Katakana whenever possible, e.g. 'ゾウ' instead of '象'), DO NOT include Romanji or English. ensure the JSON keys ('mbti', 'animal', 'description') remain in ENGLISH."
    elif lang == "en":
        lang_instruction = "IMPORTANT: The content of your analysis (mbti, animal, description) MUST BE IN ENGLISH. For the 'animal' field, output ONLY the English name."

    # Define the 12 standard animals
    valid_animals = """
    1. Lion (狮子 / ライオン)
    2. Cheetah (猎豹 / チーター)
    3. Pegasus (飞马 / ペガサス)
    4. Elephant (象 / ゾウ)
    5. Monkey (猴子 / サル)
    6. Wolf (狼 / オオカミ)
    7. Koala (考拉 / コアラ)
    8. Tiger (虎 / トラ)
    9. Black Panther (黑豹 / クロヒョウ)
    10. Sheep (羊 / ヒツジ)
    11. Raccoon Dog (狸猫 / タヌキ)
    12. Fawn (小鹿 / コジカ)
    """

    prompt = ChatPromptTemplate.from_template(
        """
        You are a psychoanalytic expert proficient in MBTI personality theory and animal divination (Dobutsu Uranai).
        Please carefully read the following social media content of the user (including profile and posts), deeply analyze their behavior style, values, and thinking patterns.

        [User Content]:
        {text}

        Please infer:
        1. The user's MBTI type (16 personalities).
        2. The user's corresponding animal figure in "Animal Fortune". 
           IMPORTANT: You MUST choose one from the following 12 animals based on the user's personality traits. 
           [Valid Animals List]:
           {valid_animals}
           
        3. Generate a personality portrait (200-300 words).

        {lang_instruction}

        IMPORTANT: Ouptut MUST be valid JSON. Do NOT translate the JSON keys (mbti, animal, description).
        Please ensure output in JSON format, do not include Markdown format tags (json ...).
        
        {format_instructions}
        """
    ).partial(lang_instruction=lang_instruction, valid_animals=valid_animals)

    chain = prompt | llm | parser

    try:
        print("Performing AI personality analysis...")
        result = chain.invoke({
            "text": text_content,
            "format_instructions": parser.get_format_instructions()
        })
        return result
    except Exception as e:
        print(f"AI Analysis Failed: {e}")
        return {
            "mbti": "Unknown",
            "animal": "Unknown", 
            "description": "An error occurred during verification, please try again later."
        }
