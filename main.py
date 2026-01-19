import os 
from fastapi import FastAPI, File, UploadFile, HTTPException 
from fastapi.responses import StreamingResponse 
from pydantic import BaseModel 
from typing import Optional 
from datetime import datetime 
from dotenv import load_dotenv 
import motor.motor_asyncio 
import io 
from bson import ObjectId 

# Load environment variables from .env file 
load_dotenv(dotenv_path=".env") 
 
app = FastAPI() 
 
# Connect to MongoDB Atlas 
# gets the mongo_uri from the .env
client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URI")) 
db = client.event_management_db 
 
# Data Models 
class Event(BaseModel): 
    name: str 
    description: str 
    date: str 
    venue_id: str 
    max_attendees: int 
 
class Attendee(BaseModel): 
    name: str 
    email: str 
    phone: Optional[str] = None 
 
class Venue(BaseModel): 
    name: str 
    address: str 
    capacity: int 
 
class Booking(BaseModel): 
    event_id: str 
    attendee_id: str 
    ticket_type: str 
    quantity: int 
 
# Event Endpoints 
@app.post("/events") 
async def create_event(event: Event): 
    event_doc = event.dict() 
    result = await db.events.insert_one(event_doc) 
    return {"message": "Event created", "id": str(result.inserted_id)} 
 
@app.get("/events") 
async def get_events(): 
    events = await db.events.find().to_list(100) 
    for event in events: 
        event["_id"] = str(event["_id"]) 
    return events 
 
# Upload Event Poster (Image) 
@app.post("/upload_event_poster/{event_id}") 
async def upload_event_poster(event_id: str, file: UploadFile = File(...)): 
    content = await file.read() 
    poster_doc = { 
        "event_id": event_id, 
        "filename": file.filename, 
        "content_type": file.content_type, 
        "content": content, 
        "uploaded_at": datetime.utcnow() 
    } 
    result = await db.event_posters.insert_one(poster_doc) 
    return {"message": "Event poster uploaded", "id": str(result.inserted_id)}

#Downlaod Event
@app.get("/get_event_poster/{event_id}")
async def get_event_poster(event_id: str):
    poster = await db.event_posters.find_one({"event_id": event_id})
    if not poster:
        raise HTTPException(status_code=404, detail="Event poster not found")

    return StreamingResponse(
        io.BytesIO(poster["content"]),
        media_type=poster["content_type"],
        headers={"Content-Disposition": f"attachment; filename={poster['filename']}"}
    )

# Venue Endpoints
@app.post("/venues")#Creates a new venue in database which takes in the venue object
async def create_venue(venue: Venue):
    venue_doc = venue.dict()  # Convert Pydantic model to dictionary
    result = await db.venues.insert_one(venue_doc)  # Insert into MongoDB
    return {"message": "Venue created", "id": str(result.inserted_id)} #Success message with venue ID
@app.get("/venues") #Retrieves all venues from the database
async def get_venues():
    venues = await db.venues.find().to_list(100)  # Fetch up to 100 venues
    # Convert MongoDB ObjectId to string for JSON serialization
    for venue in venues:
        venue["_id"] = str(venue["_id"])
    return venues #Return list of venues

# Attendee Endpoints
@app.post("/attendees")#Creates a new attendee in database which takes in the attendee object
async def create_attendee(attendee: Attendee):
    attendee_doc = attendee.dict()  # Convert Pydantic model to dictionary
    result = await db.attendees.insert_one(attendee_doc)  # Insert into MongoDB
    return {"message": "Attendee created", "id": str(result.inserted_id)} #Success message with attendee ID
@app.get("/attendees")#Retrieves all attendees from the database
async def get_attendees():
    attendees = await db.attendees.find().to_list(100)  # Fetch up to 100 attendees
    # Convert MongoDB ObjectId to string for JSON serialization
    for attendee in attendees:
        attendee["_id"] = str(attendee["_id"])
    return attendees #Return list of attendees

# UPDATE an attendee
@app.put("/attendees/{attendee_id}")
async def update_attendee(attendee_id: str, attendee: Attendee):
    # Update attendee details using their ID
    result = await db.attendees.update_one(
        {"_id": ObjectId(attendee_id)},  # Match attendee by ID
        {"$set": attendee.dict()}        # Update attendee data
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Attendee not found")

    return {"message": "Attendee updated"}
# DELETE an attendee
@app.delete("/attendees/{attendee_id}")
async def delete_attendee(attendee_id: str):
    # Delete attendee record from the database
    result = await db.attendees.delete_one(
        {"_id": ObjectId(attendee_id)}
    )

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Attendee not found")

    return {"message": "Attendee deleted"}


# Booking Endpoints
@app.post("/bookings")#Creates a new booking in database which takes in the booking object
async def create_booking(booking: Booking):
    booking_doc = booking.dict()  # Convert Pydantic model to dictionary
    result = await db.bookings.insert_one(booking_doc)  # Insert into MongoDB
    return {"message": "Booking created", "id": str(result.inserted_id)} #Success message with booking ID
@app.get("/bookings")#Retrieves all bookings from the database
async def get_bookings():
    bookings = await db.bookings.find().to_list(100)  # Fetch up to 100 bookings
    # Convert MongoDB ObjectId to string for JSON serialization
    for booking in bookings:
        booking["_id"] = str(booking["_id"])
    return bookings #Return list of bookings

# Upload Event Poster (Image)
@app.post("/upload_event_poster/{event_id}") #Upload an image file as event poster which takes the id of the event poster and the uploaded image file
async def upload_event_poster(event_id: str, file: UploadFile = File(...)):
    content = await file.read()  # Read the file content as bytes
    # Create document with file metadata and content
    poster_doc = {
        "event_id": event_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "content": content,  # Store binary content in MongoDB
        "uploaded_at": datetime.utcnow()
    }
    result = await db.event_posters.insert_one(poster_doc)
    return {"message": "Event poster uploaded", "id": str(result.inserted_id)} #Success message with poster ID

# Upload Venue Photo (Image)
@app.post("/upload_venue_photo/{venue_id}") #Upload an image file as venue photo which takes the id of the venue and the uploaded image file
async def upload_venue_photo(venue_id: str, file: UploadFile = File(...)):
    content = await file.read()  # Read the file content as bytes
    # Create document with file metadata and content
    poster_doc = {
        "venue_id": venue_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "content": content,  # Store binary content in MongoDB
        "uploaded_at": datetime.utcnow()
    }
    result = await db.venue_photos.insert_one(poster_doc)
    return {"message": "Venue photo uploaded", "id": str(result.inserted_id)} #Success message with photo ID

# Download Venue Photo (Image)
@app.get("/get_venue_photo/{venue_id}")
async def get_venue_photo(venue_id: str):
    photo = await db.venue_photos.find_one({"venue_id": venue_id})
    if not photo:
        raise HTTPException(status_code=404, detail="Venue photo not found")

    return StreamingResponse(
        io.BytesIO(photo["content"]),
        media_type=photo["content_type"],
        headers={"Content-Disposition": f"attachment; filename={photo['filename']}"}
    )


# Upload Promo Video (Video)
@app.post("/upload_promo_video/{event_id}") #Upload a video file as promotional video which takes the id of the event and the uploaded video file
async def upload_promo_videos(event_id: str, file: UploadFile = File(...)):
    content = await file.read()  # Read the file content as bytes
    # Create document with file metadata and content
    poster_doc = {
        "event_id": event_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "content": content,  # Store binary content in MongoDB
        "uploaded_at": datetime.utcnow()
    }
    result = await db.promo_videos.insert_one(poster_doc)
    return {"message": "Promo video uploaded", "id": str(result.inserted_id)} #Success message with video ID

# Display Promo Video (Video)
@app.get("/get_promo_video/{event_id}")
async def get_promo_video(event_id: str):
    video = await db.promo_videos.find_one({"event_id": event_id})
    if not video:
        raise HTTPException(status_code=404, detail="Promo video not found")

    return StreamingResponse(
        io.BytesIO(video["content"]),
        media_type=video["content_type"],
        headers={"Content-Disposition": f"inline; filename={video['filename']}"}
    )
