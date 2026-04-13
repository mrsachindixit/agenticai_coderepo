

import base64
from pathlib import Path
from utils.ollama_client import chat

def analyze_image(image_path: str, question: str) -> str:
    """
    Analyze an image file using a vision model (llava).
    
    Args:
        image_path: Path to the image file (jpg, png, etc.)
        question: Question or prompt about the image
        
    Returns:
        Model's analysis/response about the image
    """
    # Step 1: Read and encode image as base64
    image_data = Path(image_path).read_bytes()
    image_b64 = base64.b64encode(image_data).decode()
    
    # Step 2: Prepare message with image for vision model
    # Ollama's chat endpoint accepts images as base64 strings
    message = {
        "role": "user",
        "content": question,
        "images": [image_b64]  # Pass raw base64 data
    }
    
    # Step 3: Call vision model via chat API
    response = chat(messages=[message], model="llava")
    return response


# Example usage (minimal teaching scenario)
if __name__ == "__main__":
    # Provide your own image file path
    image_file = "sample.png"
    
    # Example 1: Describe image
    print("=== Image Description ===")
    try:
        result = analyze_image(image_file, "Describe what you see in this image.")
        print(result)
    except FileNotFoundError:
        print(f"Error: {image_file} not found. Provide an image file to analyze.")
    except Exception as e:
        print(f"Error: {e}\nNote: Ensure 'ollama pull llava' is run first.")
    
    print("\n=== Image Question ===")
    try:
        result = analyze_image(image_file, "How many objects are in this image?")
        print(result)
    except Exception as e:
        print(f"Error: {e}")


