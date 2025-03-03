
# TalentScout Hiring Assistant

TalentScout Hiring Assistant is an AI-powered chatbot designed to assist in the recruitment process by automating various tasks, such as answering candidate queries, scheduling interviews, and providing information about job positions. Built with Python and deployed as a web application, this assistant aims to streamline hiring processes for HR teams and provide a better candidate experience.

## Demo

You can view the live demo of the TalentScout Hiring Assistant here:  
[TalentScout Hiring Assistant Demo](https://web-production-37c3.up.railway.app/)

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Dependencies](#dependencies)
- [Configuration](#configuration)
- [Documentation](#documentation)
- [Contributors](#contributors)
- [License](#license)

## Installation

To run the TalentScout Hiring Assistant locally, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/thilak-r/hiring-assist-chatbot.git
    ```

2. Navigate to the project directory:
    ```bash
    cd hiring-assist-chatbot
    ```

3. Create a virtual environment (optional but recommended):
    ```bash
    python3 -m venv venv
    ```

4. Activate the virtual environment:
    - On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    - On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

5. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

6. Run the application:
    ```bash
    python app.py
    ```

## Usage

Once the application is running, navigate to `http://127.0.0.1:5000/` in your browser to access the TalentScout Hiring Assistant. The chatbot interface will allow users to interact with the assistant and perform various tasks such as scheduling interviews or getting answers to common questions related to hiring.

## Dependencies

The project relies on several Python libraries. You can find the full list in the `requirements.txt` file, which includes:

- `Flask`
- `Flask-Session`  
- `pymongo`  
- `google-generativeai` 
- `requests`  
- `python-dotenv`  
- `openai`  
To install these dependencies, run:
```bash
pip install -r requirements.txt
```

## Configuration

The application requires certain environment variables and configurations for optimal performance. Please ensure that you have the following set up:

1. **Environment variables**: Ensure that API keys and any necessary credentials for external services (such as NLP models or scheduling tools) are added to your environment.

2. **Customizing the Chatbot**: You can customize the responses, conversation flow, and other functionalities by modifying the relevant parts of the code in `app.py` and the chatbot handler scripts.

## Documentation

- The main components of the application include:
  - `app.py`: The main Flask application file.
  - `chatbot.py`: Handles interactions with the user.
  - `static/` and `templates/`: Contains web assets like HTML, CSS, and JavaScript for the frontend.


## Contributors

- [Thilak R](https://github.com/thilak-r) - Project maintainer

We welcome contributions! Feel free to fork the repository, create a branch, and submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```
