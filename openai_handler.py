import os
import json
import base64
from io import BytesIO
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with API key from .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def encode_image_to_base64(image):
    """
    Convert a PIL Image to base64 encoded string
    """
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

def get_openai_analysis(image, prediction, areas_of_concern):
    """
    Generate detailed analysis of an oral cavity image using OpenAI's GPT-4 Vision.
    
    Args:
        image (PIL.Image): The image to be analyzed
        prediction (str): The prediction from the ensemble model ('Cancerous' or 'Non-Cancerous')
        areas_of_concern (list): List of areas detected as concerning
        
    Returns:
        dict: A dictionary containing the analysis information
    """
    if prediction != "Cancerous":
        return None
    
    # Convert image to base64
    base64_image = encode_image_to_base64(image)
    
    # Create a specific prompt based on the areas of concern
    areas_text = ", ".join(areas_of_concern) if areas_of_concern else "unspecified regions"
    
    prompt = f"""
    You are a medical AI assistant specializing in oral pathology. 
    This image shows signs of oral cancer in the following areas: {areas_text}.
    
    Please provide a detailed analysis covering:
    1. Possible type of oral cancer based on visual appearance (e.g., squamous cell carcinoma, verrucous carcinoma, etc.)
    2. Common symptoms associated with this type of cancer
    3. Risk factors that may contribute to this condition
    4. Importance of early detection and treatment
    
    Keep your response informative but compassionate, understanding this may be concerning for the patient.
    Limit your response to 300 words maximum.
    """
    
    try:
        # Call the OpenAI API using the Python package
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        analysis_text = response.choices[0].message.content
        
        # Extract structured information from the analysis using GPT
        structured_info = extract_structured_info(analysis_text)
        
        return {
            "analysis_text": analysis_text,
            **structured_info
        }
        
    except Exception as e:
        print(f"Error in OpenAI analysis: {str(e)}")
        return {
            "analysis_text": "An error occurred while generating the detailed analysis.",
            "cancer_type": "Unspecified",
            "symptoms": ["Unable to determine symptoms"],
            "risk_factors": ["Unable to determine risk factors"]
        }

def extract_structured_info(analysis_text):
    """
    Use GPT to extract structured information from the analysis text
    """
    try:
        extraction_prompt = f"""
        Extract the following information from this medical analysis:
        1. Cancer type mentioned
        2. All symptoms listed
        3. All risk factors mentioned
        
        Format the response as a JSON object with keys: "cancer_type" (string), "symptoms" (array of strings), 
        and "risk_factors" (array of strings).
        
        Here's the analysis text:
        {analysis_text}
        """
        
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "user", "content": extraction_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        structured_content = response.choices[0].message.content
        
        # Parse the JSON response
        structured_data = json.loads(structured_content)
        return structured_data
        
    except Exception as e:
        print(f"Error in extraction: {str(e)}")
        return {
            "cancer_type": "Unspecified",
            "symptoms": ["Unable to extract symptoms"],
            "risk_factors": ["Unable to extract risk factors"]
        }

def generate_recommendation(cancer_type, areas_of_concern):
    """
    Generate a tailored recommendation based on the cancer type and affected areas
    """
    areas_text = ", ".join(areas_of_concern) if areas_of_concern else "the oral cavity"
    
    recommendation = (
        f"Patterns suggestive of {cancer_type} detected in {areas_text}. "
        f"This requires immediate attention from an oral pathologist or oncologist. "
        f"Please consult with a healthcare professional as soon as possible for proper "
        f"diagnosis and treatment options."
    )
    
    return recommendation