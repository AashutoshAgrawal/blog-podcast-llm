import os
import io
from agno.agent import Agent
from agno.run.agent import RunOutput
from agno.models.google import Gemini
from agno.tools.firecrawl import FirecrawlTools
from gtts import gTTS
import streamlit as st


# Streamlit Setup
st.set_page_config(page_title="📰 ➡️ 🎙️ Blog to Podcast", page_icon="🎙️")
st.title("📰 ➡️ 🎙️ Blog to Podcast Agent")

# API Keys (Runtime Input)
# st.sidebar.header("🔑 API Keys")
# google_api_key = st.sidebar.text_input("Google API Key", type="password")
# firecrawl_key = st.sidebar.text_input("Firecrawl API Key", type="password")
google_api_key = os.environ.get("GOOGLE_API_KEY")
firecrawl_key = os.environ.get("FIRECRAWL_API_KEY")

# Blog URL Input
url = st.text_input("Enter Blog URL:", "")

# Generate Button
if st.button("🎙️ Generate Podcast", disabled=not all([google_api_key, firecrawl_key])):
    if not url.strip():
        st.warning("Please enter a blog URL")
    else:
        with st.spinner("Scraping blog and generating podcast..."):
            try:
                # # Set API keys
                # google_api_key = os.environ.get("GOOGLE_API_KEY")
                # firecrawl_key = os.environ.get("FIRECRAWL_API_KEY")

                # Create agent for scraping and summarization
                agent = Agent(
                    name="Blog Summarizer",
                    model=Gemini(id="gemini-2.5-flash", api_key=google_api_key),
                    tools=[FirecrawlTools()],
                    instructions=[
                        "Scrape the blog URL and create a concise, engaging summary (max 2000 characters) suitable for a podcast.",
                        "The summary should be conversational and capture the main points."
                    ],
                )

                # Get summary
                response: RunOutput = agent.run(f"Scrape and summarize this blog for a podcast: {url}")
                summary = response.content if hasattr(response, 'content') else str(response)

                if summary:
                    # Generate audio using gTTS (free, no API key needed)
                    tts = gTTS(text=summary, lang='en')
                    audio_buffer = io.BytesIO()
                    tts.write_to_fp(audio_buffer)
                    audio_buffer.seek(0)
                    audio_bytes = audio_buffer.getvalue()

                    # Display audio
                    st.success("Podcast generated! 🎧")
                    st.audio(audio_bytes, format="audio/mp3")

                    # Download button
                    st.download_button(
                        "Download Podcast",
                        audio_bytes,
                        "podcast.mp3",
                        "audio/mp3"
                    )

                    # Show summary
                    with st.expander("📄 Podcast Summary"):
                        st.write(summary)
                else:
                    st.error("Failed to generate summary")

            except Exception as e:
                st.error(f"Error: {e}")