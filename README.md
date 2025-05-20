# IT-Tickets

A robust, Django-based web application for managing IT support tickets, deployed with PostgreSQL. Features interactive Chart.js visualizations, real-time search, staff authentication, and data export capabilities—built to showcase full-stack development skills with a focus on usability and scalability.

## Demo Video

[![IT-Tickets Demo](https://img.youtube.com/vi/xgoSJBTjM2s/0.jpg)](https://youtu.be/XxfaHredDv4)

*Click the thumbnail above to watch a demo of the app in action!*

## Live Deployment

Explore the app live at: [https://ittickets.example.com/](https://ittickets.example.com/)

*Staff Login: Username: `test`, Password: `testpassword` (demo purposes only)*

## Features

- **Ticket Management**: Add, edit, view detailed ticket records (title, description, status, priority, assignee) with staff-only access.
- **Interactive Charts**: Visualize data with Chart.js—bar (tickets by status), pie (tickets by priority), line (tickets created over time), and heatmap (priority by status), switchable via dropdown.
- **Real-Time Insights**: Sidebar with recently viewed tickets (top 5) and recent actions (last 7: add/edit/view logs).
- **Search Functionality**: Filter tickets by title, description, status, or priority.
- **Data Export**: Download ticket records as CSV (staff-only).
- **Edit History**: Track changes to ticket records with user and timestamp logs (last 5 per ticket).
- **Dashboard Widgets**: Quick stats on ticket list—total tickets, average resolution time, top priority.
- **Responsive Design**: Bootstrap-powered UI for accessibility.

## Tech Stack

- **Backend**: Django, PostgreSQL, WhiteNoise (static file serving)
- **Frontend**: Bootstrap 5, Chart.js, HTML/CSS/JavaScript
- **Deployment**: Django Authentication
- **Tools**: Python, Gunicorn

## Setup Instructions

### Prerequisites
- Python 3.11+
- PostgreSQL 16+
- Git

### Local Setup
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/IT-Tickets.git
   cd IT-Tickets
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure PostgreSQL**:
   - Create a database named `ticket_tracker` in PostgreSQL
   - Update settings.py with your local DB credentials if needed

5. **Run Migrations & Create Superuser**:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser  # Create admin user
   ```

6. **Start the Server**:
   ```bash
   python manage.py runserver
   ```
   Visit http://127.0.0.1:8000/ in your browser.

## Project Highlights
- **Scalability**: Modular Django structure, ready for additional features or API integration
- **User Experience**: Responsive UI, interactive charts, and real-time feedback enhance usability
- **Data Integrity**: Edit history and action logs ensure traceability

## Automation
CSV export streamlines reporting and data management.

## Future Enhancements
- REST API with Django REST Framework for third-party integration
- Role-based access control (e.g., admin vs. staff permissions)
- Real-time search with AJAX for instant filtering
- Notifications for staff actions (e.g., "Ticket added" alerts)

### Contact
Built by Brayden Smith. Reach out at jbrayden35@gmail.com or LinkedIn https://www.linkedin.com/in/braydenjsmith22/ for questions or collaboration!
