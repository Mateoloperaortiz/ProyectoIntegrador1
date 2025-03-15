"""
Utility functions for the catalog app.
"""
import json
import os
import time
import logging
import random
from django.http import HttpResponse
from django.conf import settings
from typing import Dict, Any, List, Optional, Union

# Import from core utilities
from core.utils import call_api
from core.security import get_api_key

# Get a logger for this module
logger = logging.getLogger(__name__)

class AIService:
    """Service class for handling AI API interactions."""
    
    @staticmethod
    def call_openai_api(prompt: str, model: str = "gpt-3.5-turbo") -> Dict[str, Any]:
        """
        Call OpenAI API with the provided prompt.
        
        Args:
            prompt (str): The message to send to the API
            model (str): The OpenAI model name to use
            
        Returns:
            dict: Response with success status and data/error
        """
        # Get API key securely
        api_key = get_api_key('OPENAI_API_KEY')
        
        # If no API key set, return a simulated response
        if not api_key:
            return AIService.simulate_ai_response("openai", prompt)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        # Use centralized API call function
        response = call_api(
            url="https://api.openai.com/v1/chat/completions",
            method="POST",
            headers=headers,
            json_data=data,
            timeout=30,
            service_name="OpenAI Chat"
        )
        
        # Process response
        if response["success"]:
            try:
                # Extract the model's response from OpenAI's JSON structure
                result = response["data"]["choices"][0]["message"]["content"]
                return {
                    "success": True,
                    "data": result
                }
            except (KeyError, IndexError) as e:
                logger.error(f"Error parsing OpenAI response: {str(e)}")
                return {
                    "success": False,
                    "error": f"Error parsing response: {str(e)}"
                }
        else:
            return response
    
    @staticmethod
    def call_huggingface_api(prompt: str, model: str = "google/flan-t5-base") -> Dict[str, Any]:
        """
        Call Hugging Face API with the provided prompt.
        
        Args:
            prompt (str): The message to send to the API
            model (str): The Hugging Face model name to use
            
        Returns:
            dict: Response with success status and data/error
        """
        # Get API key securely
        api_key = get_api_key('HUGGINGFACE_API_KEY')
        
        # If no API key set, return a simulated response
        if not api_key:
            return AIService.simulate_ai_response("huggingface", prompt)
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
        }
        
        # Use centralized API call function
        response = call_api(
            url=f"https://api-inference.huggingface.co/models/{model}",
            method="POST",
            headers=headers,
            json_data=payload,
            timeout=30,
            service_name=f"HuggingFace ({model})"
        )
        
        # Process response
        if response["success"]:
            try:
                # Extract the model's response from HuggingFace's JSON structure
                result = response["data"][0]["generated_text"]
                return {
                    "success": True,
                    "data": result
                }
            except (KeyError, IndexError) as e:
                logger.error(f"Error parsing HuggingFace response: {str(e)}")
                return {
                    "success": False,
                    "error": f"Error parsing response: {str(e)}"
                }
        else:
            return response
    
    @staticmethod
    def simulate_ai_response(service_type: str, prompt: str) -> Dict[str, Any]:
        """
        Simulate an AI response for demo purposes when API keys aren't available.
        
        Args:
            service_type (str): The type of AI service ('openai' or 'huggingface')
            prompt (str): The user's prompt
            
        Returns:
            dict: Simulated response with success status and data
        """
        # Add a slight delay to simulate API call latency
        # This makes the simulation more realistic by mimicking network delay
        time.sleep(1)
        
        # Define a set of generic fallback responses
        # These will be used if no specific pattern matches the user's prompt
        responses = [
            "I'm a simulated AI response since no API key was provided. Your question seems interesting!",
            "This is a placeholder response. To get real AI responses, please configure the API keys.",
            "I'm a demo response. In production, this would connect to the actual AI service.",
            "Thanks for your prompt! This is a simulated response for testing purposes.",
            "I understand you're asking about something, but I'm just a simulated response."
        ]
        
        # Attempt to generate contextually relevant responses based on prompt content
        # First, convert to lowercase for case-insensitive matching
        prompt_lower = prompt.lower()
        
        # RESPONSE SELECTION LOGIC:
        # The following conditional blocks analyze the prompt for specific patterns
        # and select an appropriate response category
        
        # Pattern 1: Greeting detection
        # Check if the prompt contains common greeting words
        if any(word in prompt_lower for word in ["hello", "hi", "hey", "greetings"]):
            response = "Hello! I'm a simulated AI assistant. How can I help you today? I can provide information on various topics, answer questions, or just chat with you."
        
        # Pattern 2: Help request detection
        # Identify if the user is asking for assistance
        elif "help" in prompt_lower:
            response = "I'd be happy to help! I can provide information on various topics, answer questions, or assist with tasks. What specifically do you need help with? (Note: I'm currently running in simulation mode without API access, but I'll do my best to assist you.)"
        
        # Pattern 3: Weather-related query detection
        # Check if the user is asking about weather information
        elif any(word in prompt_lower for word in ["weather", "temperature", "forecast"]):
            response = "I can't check the real-time weather as I'm running in simulation mode, but I can tell you that weather forecasting involves collecting data from satellites, weather stations, and other sources. This data is then analyzed using complex mathematical models to predict future weather conditions."
        
        # Pattern 4: Programming topic detection
        # Identify if the query is related to programming languages or coding
        elif any(word in prompt_lower for word in ["code", "programming", "javascript", "python", "java", "html", "css"]):
            response = "Programming is a fascinating field! Here's a simulated response about coding:\n\nPython is known for its readability and simplicity, making it great for beginners. JavaScript is essential for web development. HTML and CSS are the building blocks of web pages. Java is widely used in enterprise applications.\n\nIf you have a specific programming question, feel free to ask, and I'll provide a simulated response based on common knowledge."
        
        # Pattern 5: AI/ML topic detection
        # Check if the query is about AI, machine learning, or language models
        elif any(word in prompt_lower for word in ["ai", "artificial intelligence", "model", "gpt", "llm"]):
            response = "Artificial Intelligence (AI) refers to systems that can perform tasks that typically require human intelligence. Machine Learning is a subset of AI where systems learn from data. Large Language Models (LLMs) like GPT are trained on vast amounts of text data to generate human-like responses. These models have revolutionized natural language processing but also raise important ethical considerations around bias, privacy, and misinformation."
        
        # Pattern 6: General information request detection
        # Identify if the user is asking for an explanation or information
        elif any(word in prompt_lower for word in ["data", "information", "tell me", "explain"]):
            response = "I would normally provide detailed information on this topic based on my training data. Since I'm in simulation mode, I can offer a general response: Information and data are fundamental to understanding our world. Data becomes information when it's organized and presented in a meaningful context. Knowledge is derived from information when patterns and insights are extracted. If you have a specific topic you'd like explained, please let me know."
        
        # Pattern 7: Gratitude expression detection
        # Check if the user is expressing thanks
        elif any(word in prompt_lower for word in ["thanks", "thank you", "appreciate"]):
            response = "You're welcome! I'm happy to help, even in simulation mode. If you have any other questions or need assistance with anything else, feel free to ask. I'm here to make your experience as helpful as possible."
        
        # Pattern 8: Platform-specific query detection
        # Identify if the user is asking about the application itself
        elif any(word in prompt_lower for word in ["app", "platform", "website", "tool", "inspire"]):
            response = "This platform is designed to provide access to various AI tools and models. You can chat with different AI assistants, save your favorite prompts, and explore various capabilities. Currently, I'm running in simulation mode, but once API keys are configured, you'll be able to access more advanced AI features and capabilities."
        
        # Pattern 9: Capability inquiry detection
        # Check if the user is asking about what the AI can do
        elif any(word in prompt_lower for word in ["can you", "are you able", "capability", "function"]):
            response = "In simulation mode, I can provide pre-defined responses to common questions. I can simulate conversations on various topics including technology, general knowledge, and casual chat. Once API keys are configured, I'll be able to generate more dynamic and personalized responses, process complex queries, and provide more accurate and up-to-date information."
        
        # Pattern 10: Science topic detection
        # Identify if the query is related to scientific disciplines
        elif any(word in prompt_lower for word in ["science", "physics", "chemistry", "biology", "astronomy"]):
            response = "Science is the systematic study of the structure and behavior of the physical and natural world through observation and experiment. Physics explores matter, energy, and their interactions. Chemistry studies substances, their properties, and reactions. Biology examines living organisms. Astronomy focuses on celestial objects and the universe. Each field has made remarkable contributions to our understanding of the world around us."
        
        # Pattern 11: History topic detection
        # Check if the query is about historical events or periods
        elif any(word in prompt_lower for word in ["history", "war", "ancient", "civilization", "century"]):
            response = "History provides us with valuable insights into past events, cultures, and civilizations. Through studying history, we can understand how societies have evolved, learn from past successes and failures, and gain perspective on current global issues. While I'm in simulation mode, I can provide general information about historical periods, significant events, and cultural developments."
        
        # Pattern 12: Arts and culture topic detection
        # Identify if the query is about artistic or cultural subjects
        elif any(word in prompt_lower for word in ["art", "music", "literature", "movie", "culture", "book"]):
            response = "Art and culture are fundamental expressions of human creativity and experience. The arts encompass visual arts, music, literature, film, dance, and more. These creative forms allow us to explore emotions, share stories, and connect across different backgrounds and perspectives. Cultural traditions also shape our identities and communities. If you have a specific topic in arts or culture you'd like to discuss, feel free to ask."
        
        # Pattern 13: Economics/business topic detection
        # Check if the query is related to financial or business topics
        elif any(word in prompt_lower for word in ["economy", "business", "market", "finance", "investment", "money"]):
            response = "Economics and business are fascinating fields that study how societies allocate resources and how organizations operate. Economic principles help us understand markets, trade, and financial systems. Business concepts cover entrepreneurship, management, marketing, and organizational behavior. While I'm in simulation mode, I can discuss general concepts but cannot provide specific financial advice or real-time market data."
        
        # Pattern 14: Question mark detection
        # Special handling for any question not caught by previous patterns
        elif "?" in prompt:
            response = "That's an interesting question! In a fully configured system, I would provide a detailed answer based on my training data and available information. For now, I'm operating in simulation mode with pre-defined responses. If you'd like to discuss a different topic, feel free to ask another question."
        
        # Fallback response logic
        else:
            # If no specific patterns match, select a random generic response
            # This ensures the system always provides some response
            response = random.choice(responses)
            
            # Enhance the generic response based on message length analysis
            # This adds a more personalized touch even to generic responses
            if len(prompt) > 100:
                # For very long prompts, acknowledge the detail and explain limitations
                response += "\n\nI notice you've shared quite a detailed message. In a fully configured system, I would analyze the specifics of your input and provide a tailored response. Feel free to continue our conversation or try a different topic."
            elif len(prompt) < 10:
                # For very short prompts, encourage more detail
                response += "\n\nYour message was quite brief. Feel free to provide more details if you'd like a more specific response."
        
        # Add transparency note about simulation mode
        # This informs the user that they're not interacting with a real AI service
        note = f"\n\n[Note: This is a simulated {service_type} response. Configure API keys for real AI responses.]"
        
        # Only add the simulation note for shorter responses
        # This prevents excessively long responses that might overwhelm the user
        if len(response) < 500:
            response += note
        
        return {
            "success": True,
            "data": response
        }
    
    @staticmethod
    def send_to_ai_service(prompt: str, service_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route the prompt to the appropriate AI service based on configuration.
        
        Args:
            prompt (str): The user's message
            service_config (dict): Configuration for the AI service
            
        Returns:
            dict: Response with success status and data/error
        """
        service_type = service_config.get('api_type', 'none')
        model = service_config.get('api_model', '')
        
        # Check if API keys are available
        has_openai_key = bool(get_api_key('OPENAI_API_KEY'))
        has_huggingface_key = bool(get_api_key('HUGGINGFACE_API_KEY'))
        
        # Use real API if keys are available, otherwise use simulation
        try:
            if service_type == 'openai' and has_openai_key:
                # Use default model if none specified
                if not model:
                    model = "gpt-3.5-turbo"
                return AIService.call_openai_api(prompt, model)
                
            elif service_type == 'huggingface' and has_huggingface_key:
                # Use default model if none specified
                if not model:
                    model = "google/flan-t5-base"
                return AIService.call_huggingface_api(prompt, model)
                
            elif service_type == 'custom':
                # For now, custom integrations will use simulation
                return AIService.simulate_ai_response('custom', prompt)
            
            else:
                # No API key available or unknown service type, use simulation
                logger.info(f"Using simulation mode for {service_type} (no API key available)")
                return AIService.simulate_ai_response(service_type, prompt)
                
        except Exception as e:
            logger.exception(f"Error in send_to_ai_service: {str(e)}")
            return {
                "success": False,
                "error": f"Error processing request: {str(e)}"
            }

# Legacy function wrappers for backward compatibility
def call_openai_api(prompt: str, model: str = "gpt-3.5-turbo") -> Dict[str, Any]:
    return AIService.call_openai_api(prompt, model)

def call_huggingface_api(prompt: str, model: str = "google/flan-t5-base") -> Dict[str, Any]:
    return AIService.call_huggingface_api(prompt, model)

def simulate_ai_response(service_type: str, prompt: str) -> Dict[str, Any]:
    return AIService.simulate_ai_response(service_type, prompt)

def send_to_ai_service(prompt: str, service_config: Dict[str, Any]) -> Dict[str, Any]:
    return AIService.send_to_ai_service(prompt, service_config)