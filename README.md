# **Chatrooms (Discord Clone)**

Chatrooms is a full-stack web application that replicates Discord's core functionality, allowing users to create dedicated servers, join real-time chat channels, and communicate with other members. Built with Django for backend logic and PostgreSQL for data persistence, the application features a containerized architecture using Docker for consistent development and deployment. The project demonstrates user authentication systems, database management, environment configuration, and production-ready implementation with Gunicorn and Whitenoise for static file serving.

### **1. Cloning the Repository**
```bash
git clone https://github.com/nonso-uj/chatrooms-discord-clone.git
cd chatrooms-discord-clone
```

---

### **2. Local Setup (Without Docker)**
#### **Create a Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
```

#### **Install Dependencies**
```bash
pip install -r requirements.txt
```

#### **Run the App**
```bash
python manage.py runserver
```
> ⚠ Access at: http://127.0.0.1:8000/

---

### **3. Docker Setup (Recommended)**
#### **Prerequisites**
- Install [Docker](https://docs.docker.com/get-docker/)
- Install [Docker Compose](https://docs.docker.com/compose/install/)

#### **Steps**
1. **Build and Start Containers**
   ```bash
   docker-compose build
   docker-compose up
   ```
   - This will:
     - Start a **PostgreSQL** container (`db`).
     - Run Django migrations automatically.
     - Start the server at `http://localhost:8000`.

2. **Optional Commands**
   - Run migrations manually:
     ```bash
     docker-compose exec web python manage.py migrate
     ```
   - Create a superuser:
     ```bash
     docker-compose exec web python manage.py createsuperuser
     ```
   - Stop containers:
     ```bash
     docker-compose down
     ```

---

### **4. Environment Variables**
Create a `.env` file in the project root:
```ini
# PostgreSQL
DATABASE_URL=your_database_url

# Django
SECRET_KEY=yoursecretkey
DEBUG=1  # Set to 0 in production
```

---

### **5. Access the App**
- **Without Docker**: http://127.0.0.1:8000/
- **With Docker**: http://localhost:8000/

---

### **Troubleshooting**
| Issue | Solution |
|-------|----------|
| **Docker build fails** | Check `requirements.txt` and rebuild (`docker-compose build --no-cache`). |
| **Database connection error** | Ensure `DB_HOST=db` in Django settings. |
| **Port already in use** | Stop other services using ports `8000` or `5432`. |

---

🚀 **Happy Coding!**
