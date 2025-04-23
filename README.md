# Youtube-Video-Summarizer-AI

A Streamlit-based web application that generates summaries, SEO-optimized titles, tags, and thumbnail titles for YouTube videos using the EuriaAI client and YouTube Transcript API. This app provides timestamped summaries and content creation tools to enhance video discoverability.

## Features

- **Video Summarization**: Generates concise, timestamped summaries of YouTube videos using transcripts.
- **SEO Optimization**: Creates SEO-friendly titles and tags for better video ranking.
- **Thumbnail Titles**: Suggests engaging titles for video thumbnails.
- **User-Friendly Interface**: Built with Streamlit for an interactive web experience.
- **Transcript Handling**: Fetches YouTube video transcripts with error handling for unavailable or disabled transcripts.

## Tech Stack

- **Frontend/Backend**: Streamlit
- **Programming Language**: Python 3.9
- **Dependencies**: streamlit, euriai, youtube_transcript_api, python-dotenv (see `requirements.txt`)
- **Containerization**: Docker
- **Deployment**: Render, Docker Hub

## Prerequisites

- Python 3.9 or higher
- Docker Desktop (for building and testing the Docker image)
- Docker Hub account (for storing the Docker image)
- Render account (for deployment)
- EuriaAI API key or client credentials (obtain from EuriaAI platform)

## Local Setup

1. **Clone the Repository** (if using version control):

   ```bash
   git clone https://github.com/your-username/youtube-video-summarizer-ai.git
   cd youtube-video-summarizer-ai
   ```

2. **Create a Virtual Environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**: Create a `.env` file in the project root and add your EuriaAI credentials:

   ```env
   EURIAI_API_KEY=your-euriai-api-key
   ```

   Adjust based on additional variables required by `EuriaAIClient` or `app.py`.

5. **Run the App Locally**:

   ```bash
   streamlit run app.py
   ```

   Open `http://localhost:8501` in a browser to access the app.

## Docker Setup

1. **Build the Docker Image**:

   ```bash
   docker build -t nahiyan14/youtube-video-summarizer-ai:latest .
   ```

2. **Test the Image Locally**:

   ```bash
   docker run -p 8501:8501 --env-file .env nahiyan14/youtube-video-summarizer-ai:latest
   ```

   Visit `http://localhost:8501` to verify the app.

3. **Push to Docker Hub**:

   ```bash
   docker login -u username
   docker push nahiyan14/youtube-video-summarizer-ai:latest
   ```

## Deployment on Render

1. **Create a Web Service**:

   - Log in to Render.
   - Click **New** &gt; **Web Service** and select **Docker**.

2. **Configure the Service**:

   - **Image URL**: `docker.io/nahiyan14/youtube-video-summarizer-ai:latest`
   - **Service Name**: `youtube-video-summarizer-ai`
   - **Region**: Choose a region (e.g., Oregon, USA)
   - **Instance Type**: Free (for testing) or a paid tier
   - **Environment Variables**:
     - `EURIAI_API_KEY`: Your EuriaAI API key
     - Add other variables as needed by `app.py`
   - **Health Check Path**: `/` (optional)

3. **Deploy**:

   - Click **Create Web Service**. Render will pull the image and deploy it.
   - Access the app via the provided URL (e.g., `https://youtube-video-summarizer-ai.onrender.com`).

## Updating the App

1. Make changes to `app.py` or other files.
2. Rebuild and push the Docker image:

   ```bash
   docker build -t nahiyan14/youtube-video-summarizer-ai:latest .
   docker push nahiyan14/youtube-video-summarizer-ai:latest
   ```
3. Trigger a redeploy in Render via **Manual Deploy** &gt; **Deploy latest commit**.

## Troubleshooting

- **Docker Build Errors**: Ensure `euriai` and `youtube_transcript_api` are in `requirements.txt`. Verify Docker Desktop is running and WSL2 is configured (Windows users).
- **Render Deployment Issues**: Check environment variables in the Render dashboard and review logs for errors.
- **EuriaAI Errors**: Confirm API key validity and quota limits. Inspect `EuriaAIClient` response handling in `app.py`.
- **Transcript Errors**: Handle `TranscriptsDisabled` or `NoTranscriptFound` exceptions gracefully in `app.py`.
- **Streamlit Issues**: Ensure `app.py` runs on port 8501 and binds to `0.0.0.0`.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue on the GitHub repository.

## License

This project is licensed under the MIT License.

## Contact

For questions or support, open an issue on GitHub.