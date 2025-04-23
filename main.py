import os
import re
from typing import Dict, Any
from dotenv import load_dotenv
from euriai import EuriaiClient
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load environment variables
load_dotenv()

# Initialize API keys from environment
euri_api_key = os.getenv("EURI_API_KEY")
youtube_api_key = os.getenv("YOUTUBE_API_KEY")

if not euri_api_key:
    raise EnvironmentError("Missing EURI_API_KEY in environment variables")
if not youtube_api_key:
    raise EnvironmentError("Missing YOUTUBE_API_KEY in environment variables")

# Initialize the Euriai client
client = EuriaiClient(
    api_key=euri_api_key,
    model="gpt-4.1-nano"
)

# Initialize YouTube API client
youtube = build("youtube", "v3", developerKey=youtube_api_key)

# Maximum transcript length to process
MAX_TRANSCRIPT_LENGTH = 8000

def extract_video_id(youtube_url: str) -> str:
    """
    Extract YouTube video ID from URL, including support for Shorts.
    
    Args:
        youtube_url: A YouTube video URL
        
    Returns:
        The video ID
        
    Raises:
        ValueError: If the URL format is invalid
    """
    patterns = [
        r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})",      # Standard and shortened URLs
        r"(?:embed/)([a-zA-Z0-9_-]{11})",             # Embed URLs
        r"(?:watch\?v=)([a-zA-Z0-9_-]{11})",          # Watch URLs
        r"(?:shorts/)([a-zA-Z0-9_-]{11})"             # Shorts URLs
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    
    raise ValueError("❌ Invalid YouTube URL format. Please provide a valid YouTube video URL.")

def get_transcript(video_id: str) -> str:
    """
    Get and format transcript for a YouTube video using YouTube Data API.
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        Formatted transcript text
        
    Raises:
        ValueError: If transcripts are unavailable or an error occurs
    """
    try:
        # Fetch available captions for the video
        captions_response = youtube.captions().list(
            part="snippet",
            videoId=video_id
        ).execute()

        captions = captions_response.get("items", [])
        if not captions:
            raise ValueError("❌ No captions found for this video. Many YouTube Shorts don't have captions available.")

        # Select the first available caption track (preferably in English)
        caption_id = None
        for caption in captions:
            if caption["snippet"]["language"] == "en" or caption["snippet"]["language"].startswith("en-"):
                caption_id = caption["id"]
                break
        if not caption_id:
            caption_id = captions[0]["id"]  # Fallback to first available caption

        # Download the caption track
        caption_resource = youtube.captions().download(
            id=caption_id,
            tfmt="srt"  # Use SRT format for timestamps
        ).execute()

        # Decode the caption content (SRT format)
        caption_text = caption_resource.decode("utf-8")

        # Parse SRT to create formatted transcript
        formatted_text = ""
        srt_lines = caption_text.split("\n\n")
        for block in srt_lines:
            lines = block.strip().split("\n")
            if len(lines) >= 3:  # SRT format: index, timestamp, text
                timestamp = lines[1].split(" --> ")[0]  # Get start time
                # Convert SRT timestamp (e.g., 00:00:01,000) to [MM:SS]
                time_parts = timestamp.split(":")
                minutes = int(time_parts[1])
                seconds = int(time_parts[2].split(",")[0])
                formatted_timestamp = f"[{minutes:02d}:{seconds:02d}] "
                text = " ".join(lines[2:]).strip()
                formatted_text += f"{formatted_timestamp}{text}\n"

        return formatted_text

    except HttpError as e:
        if e.resp.status in [403, 404]:
            raise ValueError("❌ Captions are disabled or not available for this video.")
        raise ValueError(f"❌ Error fetching transcript: {str(e)}")
    except Exception as e:
        raise ValueError(f"❌ Error fetching transcript: {str(e)}")

def summarize_youtube_video_full(url: str) -> Dict[str, Any]:
    """
    Summarize a YouTube video from its URL using YouTube Data API.
    
    Args:
        url: YouTube video URL
        
    Returns:
        Dictionary containing the video ID, URL, and summary response
    """
    try:
        # Extract video ID
        video_id = extract_video_id(url)
        
        # Get transcript
        raw_text = get_transcript(video_id)
        
        # Clip transcript if too long
        if len(raw_text) > MAX_TRANSCRIPT_LENGTH:
            clipped_text = raw_text[:MAX_TRANSCRIPT_LENGTH]
            truncation_notice = "\n[Note: Transcript was truncated due to length]"
        else:
            clipped_text = raw_text
            truncation_notice = ""
        
        # Prepare prompt for AI
        summary_prompt = f"""
You are an AI content expert. Watch this YouTube video transcript and generate the following:
1. Timestamped and formatted summary of the video (with key sections and timestamps).
2. 5 SEO-friendly YouTube title suggestions (separated by new lines).
3. Comma-separated video tags for SEO.
4. A short thumbnail title for this video.
5. A short Description or caption for this video

Transcript:{truncation_notice}
{clipped_text}
"""

        # Generate completion
        response = client.generate_completion(
            prompt=summary_prompt,
            temperature=0.6,
            max_tokens=3000
        )
        
        # Handle different response formats
        generated_text = ""
        
        # If response is already just a string
        if isinstance(response, str):
            generated_text = response
            
        # If response is a response object from choices format
        elif isinstance(response, dict):
            if "choices" in response and len(response["choices"]) > 0:
                choice = response["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    generated_text = choice["message"]["content"]
                    
            # Check for common API response keys
            elif "text" in response:
                generated_text = response["text"]
            elif "content" in response:
                generated_text = response["content"]
            elif "completion" in response:
                generated_text = response["completion"]
            elif "response" in response:
                generated_text = response["response"]
            elif "generated_text" in response:
                generated_text = response["generated_text"]
                
        # If we couldn't extract text, use the raw response as a fallback
        if not generated_text:
            generated_text = str(response)

        return {
            "video_id": video_id,
            "video_url": url,
            "response": generated_text
        }

    except ValueError as e:
        return {"error": str(e), "video_url": url}
    except Exception as e:
        return {"error": f"❌ Unexpected error: {str(e)}", "video_url": url}