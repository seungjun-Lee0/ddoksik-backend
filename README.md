# Ddoksik Backend

This repository contains the backend services for the Ddoksik platform, which provides personalized diet and meal planning services. The backend is built using FastAPI, supports Swagger UI for API documentation, and follows a microservice architecture to ensure scalability and maintainability.

## Table of Contents

- [Project Overview](#project-overview)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Microservices](#microservices)
- [Usage](#usage)
- [Docker Setup](#docker-setup)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

The Ddoksik backend is structured into multiple services that handle authentication, user management, diet recommendations, and meal planning. Each service is stored in its own branch and can be run independently as a FastAPI application. The services use a shared database and are designed to interact through HTTP requests.

Key Features:
- **User Authentication**: Secure user login and registration.
- **Diet Recommendations**: Provides personalized diet recommendations based on user health data.
- **Meal Planning**: Allows users to create and manage meal plans.
- **Swagger UI**: Each service exposes a Swagger UI for interactive API documentation.

## Technologies Used

- **FastAPI**: Modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.
- **Swagger UI**: Interactive API documentation automatically generated from FastAPI.
- **SQLAlchemy**: ORM for database interactions.
- **PostgreSQL**: Relational database management system.
- **Docker**: Containerization for deployment.
- **GitLab CI/CD**: Continuous integration and deployment pipelines.

## Installation

### Prerequisites

- Python 3.7+
- PostgreSQL
- Docker (optional, for containerized deployment)

### Clone the Repository

```bash
git clone https://github.com/seungjun-Lee0/ddoksik-backend.git
cd ddoksik-backend
```

Install Dependencies
```bash
pip install -r requirements.txt
```
Set Up Environment Variables
Create a .env file in the root directory with the following variables:

```bash
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your_secret_key
```
Project Structure
```bash
ddoksik-backend/
├── auth/                     # Authentication service (main branch)
│   ├── auth.py               # Authentication logic (login, registration)
│   └── models.py             # User and authentication-related database models
├── diet/                     # Diet recommendation service (diet branch)
│   ├── __init__.py
│   ├── main.py               # Entry point for the diet microservice
│   ├── schemas.py            # Pydantic models for diet-related data
│   └── services.py           # Diet recommendation business logic
├── user/                     # User management service (user branch)
│   ├── __init__.py
│   ├── main.py               # Entry point for the user microservice
│   ├── schemas.py            # Pydantic models for user-related data
│   └── services.py           # User profile and management business logic
├── database.py               # Database configuration and connection setup
├── models.py                 # Shared models across services
├── requirements.txt          # Python dependencies
└── .gitlab-ci.yml            # GitLab CI/CD pipeline configuration
```
Microservices
The backend is split into several microservices, each stored in a separate branch. These services handle different aspects of the system.

Auth Service (main branch):

Provides authentication and authorization services, including user registration, login, and token management.
Key file: auth/auth.py
Diet Service (diet branch):

Handles diet recommendations based on user health profiles.
Provides APIs for retrieving recommended diets and managing diet plans.
Key files:
diet/main.py (FastAPI entry point)
diet/services.py (Business logic for diet recommendations)
User Service (user branch):

Manages user profiles and health information.
Provides APIs for retrieving and updating user data.
Key files:
user/main.py (FastAPI entry point)
user/services.py (Business logic for user data management)
Usage
Running the Application Locally
Each microservice is stored in its own branch and can be run independently. To switch to a specific service branch, use the following commands:

Auth Service (Main Branch)
```bash
git checkout main
cd auth
uvicorn auth:app --reload
```
Diet Service (Diet Branch)
```bash
git checkout diet
cd diet
uvicorn main:app --reload
```
User Service (User Branch)
```bash
git checkout user
cd user
uvicorn main:app --reload
```
Once the services are running, you can access the Swagger UI documentation at:

Auth Service: http://localhost:8000/docs
Diet Service: http://localhost:8000/docs
User Service: http://localhost:8000/docs
API Documentation
Each service exposes interactive API documentation via Swagger UI at /docs.

Docker Setup
Each service comes with a Dockerfile for containerized deployment. To build and run the services using Docker, follow these steps:

Build Docker Images
Navigate to the specific service directory (e.g., auth, diet, or user), and run:

```bash
docker build -t ddoksik-service-name .
```
Run Docker Containers
```bash
docker run -p 8000:8000 ddoksik-service-name
```
This will start the service on http://localhost:8000.

Contributing
We welcome contributions to the Ddoksik backend! Please follow these steps to contribute:

Fork the repository.
Create a new branch for your feature/bugfix (git checkout -b feature-name).
Commit your changes (git commit -m 'Add some feature').
Push to the branch (git push origin feature-name).
Open a pull request.
Ensure that your code follows the project's coding standards and passes all tests.

License
This project is licensed under the MIT License. See the LICENSE file for more details.
