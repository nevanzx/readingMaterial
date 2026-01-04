import streamlit as st
import json
import os
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches
import requests
import tempfile
from io import BytesIO
import re

# Function to add formatted text to a paragraph
def add_formatted_text(paragraph, text):
    """
    Adds text to a paragraph with formatting based on HTML-like tags.
    Supports <b> for bold and <i> for italic.
    """
    # Replace HTML entities to handle special characters
    text = text.replace('&lt;', '<').replace('&gt;', '>')

    # Split text by tags while keeping the tags
    parts = re.split(r'(<b>|</b>|<i>|</i>)', text)

    # Track current formatting state
    bold = False
    italic = False

    for part in parts:
        if part == '<b>':
            bold = True
        elif part == '</b>':
            bold = False
        elif part == '<i>':
            italic = True
        elif part == '</i>':
            italic = False
        elif part:  # Non-empty text content
            run = paragraph.add_run(part)
            run.bold = bold
            run.italic = italic

# Set page config
st.set_page_config(
    page_title="College Reading Material Generator",
    page_icon="📚",
    layout="wide"
)

# App title
st.title("📚 College Reading Material Generator")
st.markdown("Generate reading materials for college students using AI")

# Initialize session state
if 'course_outline' not in st.session_state:
    st.session_state.course_outline = None
if 'chapters_data' not in st.session_state:
    st.session_state.chapters_data = None
if 'selected_chapters' not in st.session_state:
    st.session_state.selected_chapters = []
if 'generated_materials' not in st.session_state:
    st.session_state.generated_materials = {}
if 'processing_status' not in st.session_state:
    st.session_state.processing_status = ""

# Sidebar for API keys
with st.sidebar:
    st.header("API Configuration")

    # Option to upload API keys from JSON file
    uploaded_keys = st.file_uploader("Upload API Keys (JSON)", type=["json"])

    if uploaded_keys:
        try:
            keys_data = json.load(uploaded_keys)
            apis = {api['name']: api['keys'][0] for api in keys_data['apis']}
            gemini_api_key = apis.get('gemini', '')
            deepseek_api_key = apis.get('deepseek', '')
            st.success("API keys loaded from file!")
        except Exception as e:
            st.error(f"Error loading API keys: {str(e)}")
            gemini_api_key = st.text_input("Gemini API Key", type="password")
            deepseek_api_key = st.text_input("Deepseek API Key", type="password")
    else:
        gemini_api_key = st.text_input("Gemini API Key", type="password")
        deepseek_api_key = st.text_input("Deepseek API Key", type="password")

    # Temperature setting for Deepseek
    deepseek_temperature = st.slider("Deepseek Temperature", min_value=0.0, max_value=1.0, value=0.6, step=0.1)

st.markdown("### Step 1: Upload Course Outline")
st.markdown("Upload a DOCX file containing your course outline and checklist")

# File upload
uploaded_file = st.file_uploader("Choose a DOCX file", type=["docx"])

if uploaded_file is not None:
    st.session_state.course_outline = uploaded_file
    st.success(f"File '{uploaded_file.name}' uploaded successfully!")

    # Display file info
    st.write(f"File size: {uploaded_file.size} bytes")

    # Process the document
    if st.button("Process Course Outline with Gemini"):
        if not gemini_api_key:
            st.error("Please enter your Gemini API key in the sidebar")
        else:
            with st.spinner("Processing with Gemini 2.5..."):
                # Extract text from the uploaded DOCX file
                from docx import Document as DocxDocument
                doc = DocxDocument(uploaded_file)

                # Extract all text from the document
                full_text = []
                for paragraph in doc.paragraphs:
                    full_text.append(paragraph.text)

                # Extract text from tables if any
                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            full_text.append(cell.text)

                course_outline_text = "\n".join(full_text)

                # Call Gemini API to extract chapters and topics
                try:
                    headers = {
                        "Content-Type": "application/json"
                    }

                    # Prepare the prompt for Gemini
                    prompt = f"""
                    Analyze the following course outline and extract chapters and topics in JSON format.
                    The JSON should have a structure like this:
                    {{
                        "chapters": [
                            {{
                                "chapter": "Chapter Name",
                                "topics": ["Topic 1", "Topic 2", "Topic 3"]
                            }}
                        ]
                    }}

                    Ensure that topics are specific and detailed enough to generate comprehensive reading materials.
                    Course Outline:
                    {course_outline_text}
                    """

                    # Make request to Gemini API
                    # For Gemini API, the key should be passed as a query parameter or in the URL
                    import urllib.parse
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={urllib.parse.quote(gemini_api_key)}"

                    response = requests.post(
                        url,
                        headers={"Content-Type": "application/json"},
                        json={
                            "contents": [{
                                "parts": [{
                                    "text": prompt
                                }]
                            }]
                        }
                    )

                    if response.status_code == 200:
                        result = response.json()

                        # Extract the text response
                        text_response = result['candidates'][0]['content']['parts'][0]['text']

                        # Find the JSON part in the response
                        import re
                        json_match = re.search(r'\{.*\}', text_response, re.DOTALL)

                        if json_match:
                            json_str = json_match.group()
                            st.session_state.chapters_data = json.loads(json_str)

                            # Clear selected chapters
                            st.session_state.selected_chapters = []

                            st.success("Course outline processed successfully!")
                            st.session_state.processing_status = "processed"
                        else:
                            st.error("Could not extract JSON from Gemini response")
                    else:
                        st.error(f"Gemini API error: {response.status_code} - {response.text}")

                except requests.exceptions.RequestException as e:
                    st.error(f"Network error while processing with Gemini: {str(e)}")
                except json.JSONDecodeError:
                    st.error("Invalid JSON response from Gemini API")
                except Exception as e:
                    st.error(f"Unexpected error while processing with Gemini: {str(e)}")

# Display chapters if available
if st.session_state.chapters_data:
    st.markdown("### Step 2: Select Chapters to Generate")

    # Display chapters as checkboxes
    selected_chapters = []
    for idx, chapter in enumerate(st.session_state.chapters_data.get("chapters", [])):
        chapter_name = chapter.get("chapter", f"Chapter {idx+1}")
        topics = chapter.get("topics", [])

        col1, col2 = st.columns([1, 4])
        with col1:
            is_selected = st.checkbox(f"Include {chapter_name}", key=f"chapter_{idx}")
        with col2:
            st.write(f"**{chapter_name}**")
            if topics:
                st.write("Topics:")
                for topic in topics:
                    st.write(f"- {topic}")

        if is_selected:
            selected_chapters.append({
                "chapter": chapter_name,
                "topics": topics
            })

    # Update session state with selected chapters
    st.session_state.selected_chapters = selected_chapters

    # Generate materials for selected chapters
    if st.button("Generate Reading Materials") and selected_chapters:
        if not deepseek_api_key:
            st.error("Please enter your Deepseek API key in the sidebar")
        else:
            # Create a progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()

            with st.spinner("Generating materials with Deepseek..."):
                # Process each selected chapter with Deepseek
                generated_materials = {}

                for idx, chapter_data in enumerate(selected_chapters):
                    chapter_name = chapter_data["chapter"]
                    topics = chapter_data["topics"]

                    status_text.text(f"Processing: {chapter_name}...")
                    progress_bar.progress((idx + 1) / len(selected_chapters))

                    # Prepare prompt for Deepseek Reasoner
                    prompt = f"""
                    You are an expert educator. Generate detailed, well-structured reading material for the following chapter and topics.
                    Use your reasoning capabilities to provide comprehensive explanations, examples, and connections between concepts.
                    Return the response in JSON format with the following structure:
                    {{
                        "title": "Chapter Title",
                        "introduction": "Brief introduction to the chapter",
                        "topics": [
                            {{
                                "topic": "Topic Name",
                                "content": [
                                    "Content paragraph 1",
                                    "Content paragraph 2",
                                    "Content paragraph 3"
                                ]
                            }}
                        ]
                    }}

                    When generating content, use HTML-like tags to emphasize important words or concepts:
                    - Use <b> and </b> for bold formatting (for key terms, definitions, important concepts)
                    - Use <i> and </i> for italic formatting (for examples, clarifications, or special notes)

                    Chapter: {chapter_name}
                    Topics: {', '.join(topics)}

                    - For each topic, generate 3-5 paragraphs depending on the complexity and length of explanation needed.
                    - Ensure the content is comprehensive, well-structured, and suitable for college-level students. 
                    - Add a summary at the end with title.
                    """

                    try:
                        # Call Deepseek API
                        headers = {
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {deepseek_api_key}"
                        }

                        response = requests.post(
                            "https://api.deepseek.com/chat/completions",
                            headers=headers,
                            json={
                                "model": "deepseek-reasoner",
                                "messages": [
                                    {"role": "user", "content": prompt}
                                ],
                                "temperature": deepseek_temperature,
                                "max_tokens": 16000,  # Set token limit to 16k
                                "response_format": {"type": "json_object"}
                            }
                        )

                        if response.status_code == 200:
                            result = response.json()
                            content = result['choices'][0]['message']['content']

                            # Extract JSON from response
                            import re
                            json_match = re.search(r'\{.*\}', content, re.DOTALL)

                            if json_match:
                                json_str = json_match.group()
                                material_data = json.loads(json_str)
                                generated_materials[chapter_name] = material_data
                                st.success(f"✓ Generated material for: {chapter_name}")
                            else:
                                st.warning(f"Could not extract JSON for {chapter_name}")
                        else:
                            st.error(f"Deepseek API error for {chapter_name}: {response.status_code} - {response.text}")

                    except requests.exceptions.RequestException as e:
                        st.error(f"Network error while generating material for {chapter_name}: {str(e)}")
                    except json.JSONDecodeError:
                        st.error(f"Invalid JSON response from Deepseek API for {chapter_name}")
                    except Exception as e:
                        st.error(f"Unexpected error while generating material for {chapter_name}: {str(e)}")

                st.session_state.generated_materials = generated_materials

                if generated_materials:
                    st.success("All reading materials generated successfully!")
                else:
                    st.warning("No materials were generated. Please check the API responses.")

            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()

# Download section
if st.session_state.generated_materials:
    st.markdown("### Step 3: Download Generated Materials")

    for chapter_name, content in st.session_state.generated_materials.items():
        st.subheader(f"{chapter_name}")

        # Create DOCX file
        doc = Document()
        title_heading = doc.add_heading(content.get("title", chapter_name), 0)
        # Format the main title heading with 10/72 before line spacing and 6/72 after line spacing
        title_heading.paragraph_format.space_before = Inches(0.1389)  # 10/72 inches
        title_heading.paragraph_format.space_after = Inches(0.0833)   # 6/72 inches

        # Add chapter introduction if available
        introduction = content.get("introduction")
        if introduction:
            intro_heading = doc.add_heading("Chapter Introduction", level=1)
            # Format the heading with 10/72 before line spacing and 6/72 after line spacing
            intro_heading.paragraph_format.space_before = Inches(0.1389)  # 10/72 inches
            intro_heading.paragraph_format.space_after = Inches(0.0833)   # 6/72 inches

            # Process introduction with formatting
            intro_para = doc.add_paragraph()
            # Format the paragraph: justified, 6/72 line spacing, 1 tab indent
            intro_para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            intro_para_format = intro_para.paragraph_format
            intro_para_format.space_after = Inches(0.0833)  # 6/72 inches after paragraph
            intro_para_format.line_spacing = 1.0  # Single line spacing
            intro_para_format.first_line_indent = Inches(0.5)  # 0.5 inch indent
            # Also set left indent to make it more visible
            intro_para_format.left_indent = 0  # Keep left margin at 0

            # Add formatted text to the paragraph
            add_formatted_text(intro_para, introduction)

        for topic in content.get("topics", []):
            # Add topic heading with 10pt before spacing and 6pt after spacing
            topic_heading = doc.add_heading(topic.get("topic", "Topic"), level=1)
            topic_heading.paragraph_format.space_before = Inches(0.1389)  # Approximately 10pt (10/72 inches)
            topic_heading.paragraph_format.space_after = Inches(0)   # Approximately 6pt (6/72 inches)

            # Handle both single content string and multiple content sections
            topic_content = topic.get("content", "")
            if isinstance(topic_content, list):
                # Multiple content sections
                for content_section in topic_content:
                    para = doc.add_paragraph()
                    # Format the paragraph: justified, 6/72 after spacing, 1 tab indent
                    para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    para_format = para.paragraph_format
                    para_format.space_after = Inches(0.0833)  # 6/72 inches after paragraph
                    para_format.line_spacing = 1.0  # Single line spacing
                    para_format.first_line_indent = Inches(0.5)  # 0.5 inch indent
                    # Also set left indent to make it more visible
                    para_format.left_indent = 0  # Keep left margin at 0

                    # Add formatted text to the paragraph
                    add_formatted_text(para, content_section)
            else:
                # Single content string
                para = doc.add_paragraph()
                # Format the paragraph: justified, 6/72 after spacing, 1 tab indent
                para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                para_format = para.paragraph_format
                para_format.space_after = Inches(0.0833)  # 6/72 inches after paragraph
                para_format.line_spacing = 1.0  # Single line spacing
                para_format.first_line_indent = Inches(0.5)  # 0.5 inch indent

                # Add formatted text to the paragraph
                add_formatted_text(para, topic_content)

        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
            doc.save(tmp_file.name)

            with open(tmp_file.name, "rb") as f:
                st.download_button(
                    label=f"Download {chapter_name}.docx",
                    data=f.read(),
                    file_name=f"{chapter_name.replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

        # Clean up temp file
        os.unlink(tmp_file.name)