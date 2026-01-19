# DBE62A

This project is a RESTful API developed using FastAPI and MongoDB Atlas.
It manages events, attendees, venues, bookings, and multimedia assets
including event posters, promotional videos, and venue photos.

## Technologies Used
- Python 3.11
- FastAPI
- MongoDB Atlas
- Motor (Async MongoDB Driver)
- Pydantic
- Uvicorn
- Postman
- Python-dotenv

  ## Environment Setup
1. Create a virtual environment:
   python -m venv .venv

2. Activate the environment:
   .venv\Scripts\activate  (Windows)

3. Install dependencies:
   pip install -r requirements.txt


   ## Environment Variables
Create a .env file with the following variable:
MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/event_management_db
Note: The .env file is excluded from version control for security reasons.

## Running the Application
uvicorn main:app --reload

## web access
https://dbe-62-mxr9cfr4x-denzils-projects-a9f6c0bc.vercel.app/docs




## API Endpoints

POST /events
GET /events

POST /attendees
GET /attendees

POST /venues
GET /venues

POST /bookings
GET /bookings

POST /upload_event_poster/{event_id}
GET /get_event_poster/{event_id}

POST /upload_promo_video/{event_id}
GET /get_promo_video/{event_id}

POST /upload_venue_photo/{venue_id}
GET /get_venue_photo/{venue_id}
