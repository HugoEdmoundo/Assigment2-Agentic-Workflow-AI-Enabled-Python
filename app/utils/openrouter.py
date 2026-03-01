import os
from openai import OpenAI
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# OpenRouter client (compatible dengan OpenAI SDK)
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError("OPENROUTER_API_KEY not found in environment variables!")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

def research_topic(topic: str) -> dict:
    """Research topic menggunakan AI"""
    try:
        logger.info(f"Researching topic: {topic}")
        
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"Research and provide key information about: {topic}. Include main points, statistics, and important facts. Be detailed and informative."
                }
            ]
        )
        
        content = response.choices[0].message.content
        
        return {
            "topic": topic,
            "research_result": content,
            "model": "gpt-3.5-turbo",
            "tokens": response.usage.total_tokens if response.usage else 0
        }
    except Exception as e:
        logger.error(f"Error researching topic: {str(e)}")
        raise

def summarize_text(text: str, max_words: int = 100) -> str:
    """Summarize text menggunakan AI"""
    try:
        logger.info(f"Summarizing text ({len(text)} chars)")
        
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"Summarize this text in maximum {max_words} words:\n\n{text}"
                }
            ]
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error summarizing: {str(e)}")
        raise

def extract_key_points(text: str) -> list:
    """Extract key points dari text"""
    try:
        logger.info("Extracting key points")
        
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"Extract 5 key points from this text. Return as numbered list (1. 2. 3. etc):\n\n{text}"
                }
            ]
        )
        
        content = response.choices[0].message.content
        # Parse numbered list
        points = [line.strip() for line in content.split('\n') if line.strip() and any(c.isdigit() for c in line[:3])]
        
        return points[:5]  # Max 5 points
    except Exception as e:
        logger.error(f"Error extracting key points: {str(e)}")
        raise

def generate_recommendations(topic: str, research_data: str) -> list:
    """Generate recommendations based on research"""
    try:
        logger.info("Generating recommendations")
        
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"Based on this research about '{topic}', provide 3 actionable recommendations. Return as numbered list (1. 2. 3.):\n\nResearch:\n{research_data[:500]}"
                }
            ]
        )
        
        content = response.choices[0].message.content
        recommendations = [line.strip() for line in content.split('\n') if line.strip() and any(c.isdigit() for c in line[:3])]
        
        return recommendations[:3]  # Max 3 recommendations
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        raise
