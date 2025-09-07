# Campus Event Management Platform - Design Document

## 🎓 Project Overview
A comprehensive event reporting system for campus event management with admin portal and student app functionality.

## 📋 Assumptions & Decisions

### Key Assumptions
- **Scale**: System designed for ~50 colleges, 500 students each, 20 events per semester
- **Event IDs**: Unique across colleges (implemented via college_id separation)
- **Data Separation**: College data kept separate using college_id foreign keys
- **User Roles**: Simple role-based access (admin vs student)
- **Event Capacity**: Default 100 participants, configurable per event
- **Feedback System**: 1-5 star rating with optional comments
- **Duplicate Prevention**: Students cannot register twice for same event

### Technical Decisions
- **Backend**: Python Flask (lightweight, RESTful APIs)
- **Database**: SQLite (simple, no external dependencies)
- **Frontend**: HTML/CSS/JavaScript (responsive, modern UI)
- **Architecture**: MVC pattern with clear separation of concerns
- **Security**: Basic input validation and CORS enabled
- **Performance**: Efficient SQL queries with proper indexing

## 🗄️ Database Schema

### ER Diagram (Text Representation)
```
┌─────────────┐     ┌─────────────┐
│   colleges  │     │  students   │
├─────────────┤     ├─────────────┤
│ id (PK)     │     │ id (PK)     │
│ name        │     │ name        │
│ location    │     │ email       │
│ created_at  │     │ college_id  │──┘
└─────────────┘     │ created_at  │
                    └─────────────┘
                           │
                           │
                    ┌─────────────┐     ┌─────────────┐
                    │  events     │     │registrations│
                    ├─────────────┤     ├─────────────┤
                    │ id (PK)     │     │ id (PK)     │
                    │ title       │     │ student_id  │──┐
                    │ description │     │ event_id    │──┘
                    │ event_type  │     │ registered_at│
                    │ event_date  │     └─────────────┘
                    │ college_id  │            │
                    │ capacity    │            │
                    │ created_at  │            │
                    └─────────────┘            │
                           │                   │
                           │                   │
                    ┌─────────────┐     ┌─────────────┐
                    │ attendance  │     │  feedback   │
                    ├─────────────┤     ├─────────────┤
                    │ id (PK)     │     │ id (PK)     │
                    │ registration│─────┘ registration│
                    │ checked_in_at│     │ rating     │
                    └─────────────┘     │ comments    │
                                        │ submitted_at│
                                        └─────────────┘
```

### Tables Description

#### colleges
- **Purpose**: Store college/university information
- **Fields**:
  - `id`: Primary key, auto-increment
  - `name`: College name (required)
  - `location`: College location (optional)
  - `created_at`: Timestamp

#### students
- **Purpose**: Store student information
- **Fields**:
  - `id`: Primary key, auto-increment
  - `name`: Student full name (required)
  - `email`: Unique email address (required)
  - `college_id`: Foreign key to colleges (required)
  - `created_at`: Timestamp

#### events
- **Purpose**: Store event information
- **Fields**:
  - `id`: Primary key, auto-increment
  - `title`: Event title (required)
  - `description`: Event description (optional)
  - `event_type`: Type (Workshop, Hackathon, Seminar, Fest, Tech Talk)
  - `event_date`: Event date (required)
  - `college_id`: Foreign key to colleges (required)
  - `capacity`: Maximum participants (default: 100)
  - `created_at`: Timestamp

#### registrations
- **Purpose**: Track student-event registrations
- **Fields**:
  - `id`: Primary key, auto-increment
  - `student_id`: Foreign key to students (required)
  - `event_id`: Foreign key to events (required)
  - `registered_at`: Registration timestamp
- **Constraints**: Unique combination of student_id + event_id

#### attendance
- **Purpose**: Track event attendance
- **Fields**:
  - `id`: Primary key, auto-increment
  - `registration_id`: Foreign key to registrations (required)
  - `checked_in_at`: Attendance timestamp
- **Constraints**: Unique registration_id (one attendance per registration)

#### feedback
- **Purpose**: Store student feedback
- **Fields**:
  - `id`: Primary key, auto-increment
  - `registration_id`: Foreign key to registrations (required)
  - `rating`: Rating 1-5 (required)
  - `comments`: Optional feedback comments
  - `submitted_at`: Feedback submission timestamp
- **Constraints**: Unique registration_id (one feedback per registration)

## 🔌 API Design

### Base URL
```
http://localhost:5000/api
```

### Endpoints

#### Colleges
- `POST /colleges` - Create new college
  - **Body**: `{"name": "string", "location": "string"}`
  - **Response**: `{"message": "College created", "id": number}`

#### Students
- `POST /students` - Create new student
  - **Body**: `{"name": "string", "email": "string", "college_id": number}`
  - **Response**: `{"message": "Student created", "id": number}`

#### Events
- `POST /events` - Create new event
  - **Body**: `{"title": "string", "description": "string", "event_type": "string", "event_date": "YYYY-MM-DD", "college_id": number, "capacity": number}`
  - **Response**: `{"message": "Event created", "id": number}`

- `GET /events` - Get events (with optional filters)
  - **Query Params**: `college_id`, `event_type`
  - **Response**: Array of event objects with registration counts

- `POST /events/{event_id}/register` - Register student for event
  - **Body**: `{"student_id": number}`
  - **Response**: `{"message": "Registered successfully", "registration_id": number}`

#### Attendance & Feedback
- `POST /attendance/{registration_id}` - Mark attendance
  - **Response**: `{"message": "Attendance marked", "attendance_id": number}`

- `POST /feedback/{registration_id}` - Submit feedback
  - **Body**: `{"rating": number, "comments": "string"}`
  - **Response**: `{"message": "Feedback submitted", "feedback_id": number}`

#### Reports
- `GET /reports/events` - Event popularity report
  - **Response**: Events sorted by registration count with stats

- `GET /reports/students` - Student participation report
  - **Response**: Students sorted by registration count with stats

- `GET /reports/top-students` - Top 3 active students
  - **Response**: Top 3 students by registration count

## 🔄 Workflows

### Student Registration Flow
```
1. Student browses available events
2. Student selects event to register
3. System validates:
   - Event exists
   - Event has capacity
   - Student not already registered
4. System creates registration record
5. Student receives confirmation
```

### Event Attendance Flow
```
1. Admin views registered students for event
2. Admin marks attendance for each student
3. System validates:
   - Registration exists
   - Attendance not already marked
4. System creates attendance record
5. Student attendance status updated
```

### Feedback Submission Flow
```
1. Student attends event
2. Post-event, student submits feedback
3. System validates:
   - Registration exists
   - Feedback not already submitted
   - Rating is 1-5
4. System stores feedback
5. Feedback statistics updated
```

### Report Generation Flow
```
1. Admin requests specific report
2. System queries database with appropriate joins
3. System aggregates data (counts, averages)
4. System formats data for display
5. Admin views report with filtering options
```

## ⚠️ Edge Cases & Error Handling

### Registration Edge Cases
- **Duplicate Registration**: Student tries to register twice → Return error
- **Full Capacity**: Event reaches capacity → Prevent new registrations
- **Invalid Event**: Event doesn't exist → Return 404
- **Invalid Student**: Student doesn't exist → Return 404

### Attendance Edge Cases
- **Already Marked**: Attendance already recorded → Return error
- **Invalid Registration**: Registration doesn't exist → Return 404
- **Post-Event Marking**: Allow attendance marking after event date

### Feedback Edge Cases
- **Already Submitted**: Feedback already given → Return error
- **Invalid Rating**: Rating outside 1-5 range → Return error
- **No Registration**: No registration found → Return 404

### Data Integrity
- **Foreign Key Constraints**: Prevent orphaned records
- **Unique Constraints**: Prevent duplicate registrations/attendance/feedback
- **Data Validation**: Validate all input data types and ranges

## 📊 Report Specifications

### Event Popularity Report
- **Data Points**: Event name, type, date, college, registration count, attendance count, average rating
- **Sorting**: By total registrations (descending)
- **Filters**: By event type, college, date range
- **Purpose**: Identify most popular events

### Student Participation Report
- **Data Points**: Student name, email, college, registration count, attendance count, average rating
- **Sorting**: By total registrations (descending)
- **Filters**: By college, participation level
- **Purpose**: Track student engagement

### Top Students Report
- **Data Points**: Same as participation report
- **Limit**: Top 3 students
- **Purpose**: Recognize most active students

## 🔧 Implementation Notes

### Database Optimization
- **Indexes**: Primary keys automatically indexed
- **Joins**: Efficient queries using LEFT JOINs
- **Aggregation**: Use COUNT, AVG functions for reports
- **Constraints**: Foreign key and unique constraints for data integrity

### API Design Principles
- **RESTful**: Standard HTTP methods and status codes
- **JSON**: Consistent request/response format
- **Error Handling**: Meaningful error messages
- **Validation**: Input validation on all endpoints

### Frontend Architecture
- **Responsive**: Works on desktop and mobile
- **Progressive Enhancement**: Core functionality works without JavaScript
- **Accessibility**: Semantic HTML and ARIA attributes
- **Performance**: Minimal HTTP requests, efficient DOM manipulation

### Security Considerations
- **Input Sanitization**: Prevent SQL injection and XSS
- **CORS**: Properly configured for cross-origin requests
- **Data Validation**: Server-side validation for all inputs
- **Error Handling**: Don't expose sensitive information in errors

## 🚀 Deployment & Scaling

### Current Setup (Development)
- **Database**: SQLite (single file, easy setup)
- **Server**: Flask development server
- **Hosting**: Local development environment

### Production Considerations
- **Database**: PostgreSQL/MySQL for concurrent access
- **Server**: Gunicorn + Nginx for production serving
- **Caching**: Redis for session and data caching
- **Monitoring**: Logging and error tracking
- **Backup**: Regular database backups

### Scalability Features
- **Database Sharding**: By college_id for large datasets
- **API Rate Limiting**: Prevent abuse
- **Caching Layer**: Cache frequently accessed data
- **Horizontal Scaling**: Multiple application servers

## 📈 Future Enhancements

### Short Term
- User authentication and authorization
- Email notifications for registrations
- Advanced filtering and search
- Data export functionality (CSV/PDF)
- Real-time attendance updates

### Long Term
- Mobile app development
- Integration with calendar systems
- Advanced analytics and dashboards
- Multi-language support
- Integration with learning management systems

---

*This design document provides a comprehensive overview of the Campus Event Management Platform architecture, ensuring scalability, maintainability, and user experience.*
