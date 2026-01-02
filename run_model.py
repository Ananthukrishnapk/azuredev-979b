"""
Azure AI Foundry Integration Module
This module integrates Azure OpenAI services with the SEO-GEO-AEO API project
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import Optional, List, Dict

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
AZURE_OPENAI_ENDPOINT = os.getenv(
    "AZURE_OPENAI_ENDPOINT", 
    "https://johngeorge-2562-resource.openai.azure.com/openai/v1/"
)
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "<your-api-key>")

# Initialize OpenAI client
client = OpenAI(
    base_url=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY
)


def chat_completion(
    messages: List[Dict[str, str]], 
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
) -> str:
    """
    Get a chat completion from Azure OpenAI
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        temperature: Sampling temperature (0.0 to 2.0)
        max_tokens: Maximum tokens in response (None for default)
    
    Returns:
        str: The completion response content
    """
    try:
        completion = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error calling Azure OpenAI: {e}")
        return f"Error: {str(e)}"


def analyze_content_with_ai(
    content: str,
    analysis_type: str = "SEO"
) -> str:
    """
    Analyze content using Azure OpenAI for SEO, GEO, or AEO insights
    
    Args:
        content: The content to analyze
        analysis_type: Type of analysis (SEO, GEO, or AEO)
    
    Returns:
        str: AI-generated analysis
    """
    prompts = {
        "SEO": "Analyze the following content for SEO optimization. Provide insights on keyword usage, meta information, and content quality:",
        "GEO": "Analyze the following content for Generative Engine Optimization (GEO). Check for factual accuracy, transparent intent, and AI spam:",
        "AEO": "Analyze the following content for Answer Engine Optimization (AEO). Verify factual accuracy and EEAT compliance:"
    }
    
    prompt = prompts.get(analysis_type, prompts["SEO"])
    
    messages = [
        {
            "role": "system",
            "content": "You are an expert in web content optimization for search engines and AI systems."
        },
        {
            "role": "user",
            "content": f"{prompt}\n\n{content}"
        }
    ]
    
    return chat_completion(messages, temperature=0.7)


def main():
    """Main function for testing the Azure AI Foundry integration"""
    print("🚀 Testing Azure AI Foundry Integration\n")
    print(f"Endpoint: {AZURE_OPENAI_ENDPOINT}")
    print(f"Deployment: {AZURE_OPENAI_DEPLOYMENT}\n")
    
    # Test basic completion
    print("=" * 50)
    print("Test 1: Basic Chat Completion")
    print("=" * 50)
    
    messages = [
        {
            "role": "user",
            "content": "What is the capital of France?",
        }
    ]
    
    response = chat_completion(messages)
    print(f"Response: {response}\n")
    
    # Test content analysis
    print("=" * 50)
    print("Test 2: SEO Content Analysis")
    print("=" * 50)
    
    sample_content = """
    Welcome to our website! We offer the best products in the market.
    Our services include web development, SEO optimization, and digital marketing.
    Contact us today to learn more about our offerings.
    """
    
    seo_analysis = analyze_content_with_ai(sample_content, "SEO")
    print(f"SEO Analysis:\n{seo_analysis}\n")
    
    print("✅ Azure AI Foundry integration test complete!")


if __name__ == "__main__":
    main()