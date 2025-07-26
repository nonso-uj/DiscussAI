# **DiscussAI || AI-Powered Chatrooms**

DiscussAI transforms your chatrooms with an on-demand AI assistant. Users trigger the bot by mentioning **@ai** in messages, and it will thoughtfully respond. Smart summarisation is built-in and used internally to manage token limits, but it's just a behind-the-scenes efficiency tool, not a main feature.

Under the hood:

* **Django** powers the backend logic
* **PostgreSQL** ensures data persistence (external service to reduce docker image size)
* **Docker** offers containerized development and deployment
* **Hugging Face Inference API** (using Meta LLaMA‑3.1) drives the AI assistant, and (facebook/bart-large-cnn) drives messages summarization

---

### 🚀 Key Features

* 🗨️ Real-time chatrooms and conversations
* 🔍 **@ai Mention Detection**: Users type `@ai`, and the assistant jumps in
* 🧠 **Internal Summarization**: Automatically condenses history to stay within LLM token limits
* 🔐 Secure authentication, PostgreSQL data storage
* ⚙️ Deployed via Docker (dev/prod) and hosted on **Render**

---

### 1. Clone the Repository

```bash
git clone https://github.com/nonso-uj/DiscussAI.git
cd DiscussAI.git
```

---

### 2. Local Development (No Docker)

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

pip install -r requirements.txt
python manage.py runserver
```

> 📎 Visit: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

### 3. Docker Setup (Recommended)

#### Requirements:

* [Docker](https://docs.docker.com/get-docker/)
* [Docker Compose](https://docs.docker.com/compose/install/)

#### Initialize Containers:

```bash
docker-compose build
docker-compose up
```

#### Helpful Commands:

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose down
```

---

### 4. Environment Variables

Create `.env` in the project root:

```ini
DATABASE_URL=postgres://...
DB_HOST=host://...
SECRET_KEY=your-secret-key
DEBUG=1
#HUGGINGFACE_API_KEY
HF_TOKEN=hf_......
```

---

### 5. AI Assistant Behavior

* The assistant **only responds when mentioned** using `@ai` in a message.
* Internally, older conversation messages are **summarized** to reduce token usage in API calls.
* Summaries ensure efficient context passing to the LLaMA‑3.1 model— the summarization logic is **background optimization**, not the main user feature.
* Users can request a summary explicitly (e.g. “@ai summarize”), but it's **not the assistant's primary duty**.

---

### 6. Deployment on Render

* A Docker-ready `Dockerfile` and `docker-compose.yml` are provided.
* Easily deploy by connecting your GitHub repo to Render and setting env variables.
* Chatrooms plus AI assistant will be live without additional infra.

---

### 7. Troubleshooting

| Issue                   | Solution                                   |
| ----------------------- | ------------------------------------------ |
| **Docker build errors** | Use `docker-compose build --no-cache`      |
| **DB connection error** | Ensure `DB_HOST=db` matches docker-compose |
| **Port conflicts**      | Free up ports 8000 or 5432                 |
| **AI calls failing**    | Check `HUGGINGFACE_API_KEY` validity       |

---

### 8. Contributing & Roadmap

* ✅ Pull requests welcome!
* 💡 Roadmap:

  * Smarter mention detection and handling
  * Persistent conversation memory
  * Optional RAG support with document uploads
  * Personality profiles per chatroom

---

### 🧠 How the AI is Prompted

We dynamically build the chat context:

1. **System message** defines the assistant’s role in the current room.
2. We optionally **prepend a summary** of older messages if the conversation is too long using facebook/bart-large-cnn.
3. We add the **most recent few messages**, then the **user’s current input**.
4. We send it all to LLaMA‑3.1‑8B and return the assistant’s reply.

This framing strategy reflects best practices—defining system roles and including relevant context to get focused, coherent responses.

---

### 🧾 Summary

DiscussAI is not just a chat clone—it’s a **smart environment-enhanced chat experience**. With **@ai-triggered conversational responses**, behind-the-scenes summarization for efficiency, and friendly deployment on Render, it’s a showcase-ready portfolio project.
