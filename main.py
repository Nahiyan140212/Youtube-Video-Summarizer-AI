import streamlit as st
import re
from youtube_summary_full import summarize_youtube_video_full

# Page configuration
st.set_page_config(
    page_title="📘 YouTube Video Summarizer", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF0000;
        text-align: center;
    }
    .subheader {
        font-size: 1.5rem;
        color: #333333;
        margin-top: 1rem;
        margin-bottom: 2rem;
    }
    .summary-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1.5rem;
        border-left: 5px solid #4285F4;
    }
    .timestamp-summary {
        background-color: #e8f0fe;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .timestamp {
        font-weight: bold;
        color: #1a73e8;
    }
    .section-title {
        font-weight: bold;
        color: #202124;
        text-decoration: underline;
    }
    .title-suggestions {
        background-color: #fef8e8;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #fbbc04;
    }
    .tags-section {
        background-color: #e6f4ea;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #34a853;
    }
    .thumbnail-section {
        background-color: #fce8e6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #ea4335;
    }
    .tag-pill {
        display: inline-block;
        background-color: #34a853;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        margin: 0.25rem;
        font-size: 0.9rem;
    }
    .title-option {
        padding: 0.5rem;
        margin: 0.5rem 0;
        background-color: #fff8e1;
        border-radius: 0.25rem;
        border-left: 3px solid #ffab40;
    }
    .info-box {
        background-color: #e8f0fe;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 5px solid #4285F4;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">📹 YouTube Video Summarizer</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Get an AI-powered summary of any YouTube video or short</p>', unsafe_allow_html=True)

# Input section
video_link = st.text_input("Paste YouTube Video or Shorts Link Here", placeholder="https://www.youtube.com/watch?v=... or https://www.youtube.com/shorts/...")

# Function to validate YouTube URL and extract video ID
def extract_video_id(url):
    patterns = [
        r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})",  # Standard and shortened URLs
        r"(?:embed/)([a-zA-Z0-9_-]{11})",         # Embed URLs
        r"(?:watch\?v=)([a-zA-Z0-9_-]{11})",      # Watch URLs
        r"(?:shorts/)([a-zA-Z0-9_-]{11})"         # Shorts URLs
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

# Function to parse and format the summary output
def format_summary(text):
    sections = {}
    current_section = None
    
    # Find the timestamp summary section
    timestamp_match = re.search(r"\*\*1\.\s*Timestamped\s*Summary:\*\*(.*?)(?:\*\*2\.|$)", text, re.DOTALL)
    if timestamp_match:
        sections['timestamp_summary'] = timestamp_match.group(1).strip()
    
    # Find the title suggestions
    title_match = re.search(r"\*\*2\.\s*5\s*SEO-Friendly\s*YouTube\s*Title\s*Suggestions:\*\*(.*?)(?:\*\*3\.|$)", text, re.DOTALL)
    if title_match:
        title_text = title_match.group(1).strip()
        # Split by newlines or by spaces followed by capital letters
        titles = re.split(r'\n+|\s+(?=[A-Z][a-z])', title_text)
        sections['title_suggestions'] = [t.strip() for t in titles if t.strip()]
    
    # Find the tags
    tags_match = re.search(r"\*\*3\.\s*Comma-Separated\s*Video\s*Tags\s*for\s*SEO:\*\*(.*?)(?:\*\*4\.|$)", text, re.DOTALL)
    if tags_match:
        tags_text = tags_match.group(1).strip()
        sections['tags'] = [tag.strip() for tag in tags_text.split(',')]
    
    # Find the thumbnail title
    thumbnail_match = re.search(r"\*\*4\.\s*Short\s*Thumbnail\s*Title:\*\*(.*?)(?:$)", text, re.DOTALL)
    if thumbnail_match:
        sections['thumbnail_title'] = thumbnail_match.group(1).strip()
    
    # If no structured parsing worked, return the original text
    if not sections:
        return {'original_text': text}
    
    return sections

# Process the video
if st.button("Summarize Video"):
    if not video_link:
        st.error("Please enter a YouTube URL")
    else:
        # Try to extract video ID
        video_id = extract_video_id(video_link)
        if not video_id:
            st.error("Please enter a valid YouTube URL")
        else:
            # Show video preview
            is_shorts = 'shorts' in video_link.lower()
            
            # Display different preview based on video type
            if is_shorts:
                st.markdown(f"""
                <div class="info-box">
                    <strong>YouTube Short:</strong> {video_id}
                    <p>Note: YouTube Shorts often have limited or no transcripts available. Results may vary.</p>
                </div>
                """, unsafe_allow_html=True)
                # Use a custom embedded player size for shorts
                st.markdown(f"""
                <iframe width="360" height="640" src="https://www.youtube.com/embed/{video_id}" 
                frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                allowfullscreen></iframe>
                """, unsafe_allow_html=True)
            else:
                # Regular video
                st.video(f"https://youtu.be/{video_id}")
            
            # Process in stages
            with st.status("Processing video...", expanded=True) as status:
                st.write("Extracting video information...")
                st.write("Downloading transcript...")
                summary = summarize_youtube_video_full(video_link)
                
                if 'error' in summary:
                    status.update(label="Error!", state="error")
                    st.error(summary['error'])
                else:
                    status.update(label="Summary complete!", state="complete")
                    
                    # Parse and format the summary output
                    formatted_data = format_summary(summary['response'])
                    
                    # Display the results in an organized way
                    st.markdown("### 📘 Video Summary")
                    
                    # Timestamp Summary Section
                    if 'timestamp_summary' in formatted_data:
                        st.markdown('<div class="summary-section">', unsafe_allow_html=True)
                        st.markdown("#### 🕒 Timestamped Summary")
                        
                        # Find and format each timestamp entry
                        timestamp_entries = re.findall(r"\*\s*\*\*(\d+:\d+-\d+:\d+\s+[^:]*?):\*\*\s*(.*?)(?=\*\s*\*\*|\Z)", 
                                                  formatted_data['timestamp_summary'], re.DOTALL)
                        
                        if timestamp_entries:
                            for timestamp, description in timestamp_entries:
                                st.markdown(f"""
                                <div class="timestamp-summary">
                                    <span class="timestamp">{timestamp}</span>: {description.strip()}
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            # If no timestamps found, display the entire summary as text
                            st.markdown(formatted_data['timestamp_summary'], unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Title Suggestions Section
                    if 'title_suggestions' in formatted_data:
                        st.markdown('<div class="title-suggestions">', unsafe_allow_html=True)
                        st.markdown("#### 📋 SEO-Friendly Title Suggestions")
                        
                        for i, title in enumerate(formatted_data['title_suggestions'], 1):
                            st.markdown(f"""
                            <div class="title-option">
                                {i}. {title}
                            </div>
                            """, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Tags Section
                    if 'tags' in formatted_data:
                        st.markdown('<div class="tags-section">', unsafe_allow_html=True)
                        st.markdown("#### 🏷️ SEO Tags")
                        
                        tags_html = ""
                        for tag in formatted_data['tags']:
                            tags_html += f'<span class="tag-pill">{tag}</span>'
                        
                        st.markdown(tags_html, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Thumbnail Title Section
                    if 'thumbnail_title' in formatted_data:
                        st.markdown('<div class="thumbnail-section">', unsafe_allow_html=True)
                        st.markdown("#### 🖼️ Thumbnail Title")
                        st.markdown(f"""
                        <h2 style="text-align: center; font-weight: bold;">{formatted_data['thumbnail_title']}</h2>
                        """, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # If the parsing failed, show the original text
                    if 'original_text' in formatted_data:
                        st.text_area("Summary Output", formatted_data['original_text'], height=400)
                    
                    # Add download button for the summary
                    st.download_button(
                        label="Download Summary",
                        data=summary['response'],
                        file_name=f"summary_{video_id}.txt",
                        mime="text/plain"
                    )

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and EuriAI")