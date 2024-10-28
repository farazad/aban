# Aban Project
This project is based on Django-based REST Framework that allows users to view, buy, and manage their balances.

## Getting Started
### Prerequisites
Before running the project, you'll need to have the following installed on your machine:
. Python3
. Docker (if running with Docker)

### Running Locally
To run the project locally, follow these steps:

1. Clone the repository to your local machine:
```bash
git clone https://github.com/farazad/aban.git
cd aban/
```
2. Install the project's dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Run the development server:
```bash
python manage.py runserver
```
Once the server is running, you can access the API at http://localhost:8000/.

### Running with Docker
To run the project using Docker, follow these steps:
```bash
docker-compose build
docker-compose up -d
```

### Running Tests
To run the tests, use pytest:
```bash
source venv/bin/activate
pytest
```
