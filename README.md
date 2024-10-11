## Overview

This backend service supports the frontend application by providing RESTful APIs to handle user authentication, book uploads, text extraction from PDFs, and TTS operations. It leverages a relational database for data storage and integrates with external TTS services.

## Features

- **User Authentication**: Secure user registration and login with JWT-based token authentication.
- **PDF Management**: Upload, delete, and retrieve PDF books.
- **Text Extraction**: Extract and chunk text from uploaded PDF books.
- **TTS Model Management**: Update TTS models for different books.
- **API-based Architecture**: RESTful API for seamless interaction with the frontend.

## API Endpoints

### User Authentication
- **`POST /register`**: Register a new user.
- **`POST /token`**: Obtain an access token for a registered user.

### PDF Book Management
- **`POST /add_book`**: Upload a new PDF book.
- **`DELETE /delete_book`**: Delete a PDF book from the server.
- **`GET /books`**: Retrieve all books associated with the current user.
- **`GET /get_book`**: Get the extracted text from a specific PDF book.
- **`GET /get_image`**: Retrieve the JPEG image of the first page of a book.
- **`GET /get_pages_num`**: Retrieve the total number of pages for a specific PDF book.

### Text-to-Speech Operations
- **`POST /chunk_text`**: Divide text into smaller chunks based on specified size.
- **`POST /update_tts_model`**: Update the TTS model for a specific book.
- **`GET /tts_model`**: Retrieve the current TTS model configuration for a book.

## Technologies Used

- **FastAPI**: High-performance web framework for building APIs with Python.
- **SQLAlchemy**: ORM for database operations.
- **Pydantic**: Data validation using Python's type annotations.
- **JWT (JSON Web Tokens)**: Secure token-based authentication.
- **Docker**: Containerization for development and deployment.
- **Uvicorn**: ASGI server for serving the FastAPI application.
