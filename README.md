# Anytime Fitness Agent

## Project Overview
This project, the "Anytime Fitness Agent," is an intelligent system designed to interact with and process information related to Anytime Fitness. It utilizes **Firecrawl** for efficient web scraping, converting web pages into structured markdown files. The scraped data undergoes a crucial cleaning process powered by **Artificial Intelligence**, with strict protocols to exclude sensitive documents like "Terms of Use" and "Privacy Policy" from modification. The cleaned markdown files are then uploaded to an **OpenAI vector store**, forming the knowledge base for a sophisticated **chatbot** capable of providing information and answering queries based on the processed data. The project includes Jupyter notebooks for exploratory data analysis and development, alongside a final Python script for core operations.

## Features
- **Advanced Web Scraping**: Employs **Firecrawl** to efficiently scrape web content and convert it into structured markdown files.
- **AI-Powered Data Cleaning**: Utilizes AI for intelligent data cleaning, ensuring data quality while respecting privacy by excluding sensitive documents (e.g., Terms of Use, Privacy Policy) from modification.
- **OpenAI Vector Store Integration**: Uploads cleaned data to an OpenAI vector store, creating a robust knowledge base.
- **Intelligent Chatbot**: Powers a chatbot capable of answering questions and providing information based on the processed and vectorized data.
- **Jupyter Notebooks**: Provides interactive environments for exploratory data analysis, development, and testing.
- **Automated Scripting**: Includes a main Python script for orchestrating core agent functionalities and workflows.

## Installation
To set up the project locally, follow these steps:

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/AnytimeFitnessAgent.git
    cd AnytimeFitnessAgent
    ```
2.  **Create a virtual environment (recommended)**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: A `requirements.txt` file is assumed. If not present, you may need to install libraries like `requests`, `BeautifulSoup4`, `pandas`, etc., manually.)*

4.  **Environment Variables**:
    Create a `.env` file in the root directory of the project and add any necessary environment variables (e.g., API keys, credentials). Refer to `.env.example` if available.

## Usage
To run the main script:

```bash
python FinalPythonScript.py
```

To explore the Jupyter notebooks:

```bash
jupyter notebook
```
Then navigate to `app.ipynb` or `initial_test.ipynb` in your browser.

## Project Structure
- `AnytimeFitnessAgent/`:
    - `.env`: Environment variables (local configuration).
    - `app.ipynb`: Main Jupyter notebook for application logic/testing.
    - `FinalPythonScript.py`: The primary Python script for the agent's operations.
    - `initial_test.ipynb`: Jupyter notebook for initial tests and data exploration.
    - `Scraping Data/`: Directory containing scraped data in markdown format.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
