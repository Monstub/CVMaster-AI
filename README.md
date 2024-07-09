# CVMaster AI

## Introduction

CVMaster AI is an intelligent application designed to analyze resumes and provide valuable feedback. It parses the resume to generate a resume score, offers skill suggestions, and recommends relevant YouTube videos to help improve the candidate's skills. The project is built using Python, Streamlit, Pandas, Pyreparser, and NLTK.

## Features

- **Resume Parsing**: Extracts information from resumes and evaluates them.
- **Resume Scoring**: Generates a score based on the resume's content and structure.
- **Skill Suggestions**: Provides suggestions for skills that can enhance the resume.
- **YouTube Recommendations**: Recommends YouTube videos for skill improvement.

## Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Libraries**: Pandas, Pyreparser, NLTK

## Installation

### Prerequisites

- Python 3.x
- Pip (Python package installer)

### Setting Up the Project

1. **Clone the Repository**:
   ```sh
   git clone https://github.com/Monstub/CVMaster-AI.git
   cd CVMaster-AI
   ```

2. **Install Python Dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the Streamlit Server**:
   ```sh
   streamlit run app.py
   ```

2. **Upload Resume**: Open the application in your web browser, and upload a resume in PDF or DOCX format.

3. **View Results**: Get the resume score, skill suggestions, and recommended YouTube videos.

## How It Works

1. **Resume Upload**: User uploads a resume through the Streamlit interface.
2. **Parsing**: The resume is parsed using Pyreparser to extract relevant information.
3. **Scoring**: The extracted information is evaluated and a resume score is generated using predefined criteria.
4. **Skill Suggestions**: Based on the resume content, the system suggests skills that could enhance the candidate's profile.
5. **YouTube Recommendations**: Relevant YouTube videos are recommended to help the user improve their skills.

## Example Commands

### Running the Application

```sh
streamlit run app.py
```

### Uploading and Analyzing a Resume

- Navigate to the Streamlit app in your browser.
- Click on the "Upload Resume" button and select your resume file.
- View the generated resume score, skill suggestions, and YouTube video recommendations.

## Tips for Using CVMaster AI

- Ensure the resume is in PDF or DOCX format for accurate parsing.
- Regularly update the skill suggestion criteria to match current industry trends.
- Customize the YouTube recommendation algorithm to provide more personalized suggestions.

## Feedback

If you encounter any issues or have suggestions for improvements, please create an issue in the project repository.
