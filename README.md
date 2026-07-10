# 🌍 Voyager — AI-Powered Travel Planner

> A full-stack Flask + IBM Watsonx.ai application that plans personalized travel itineraries,
> recommends destinations, estimates budgets, and provides real-time AI travel guidance via
> IBM Granite models.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 **AI Chat** | Conversational travel assistant powered by IBM Granite |
| 🗺️ **Itinerary Planner** | Day-by-day AI itineraries with cost, food & packing tips |
| 🧭 **Destination Explorer** | Personalized destination recommendations |
| 💰 **Budget Calculator** | Detailed trip cost breakdown (transport, hotel, food, activities) |
| 👥 **Traveler Profiles** | Manage a group of travelers with ages, dietary needs & travel style |
| 📚 **Trip History** | Save, view, and delete previously generated itineraries |
| 🌦️ **Weather Insights** | AI-generated seasonal weather guidance |
| 🌙 **Dark / Light Mode** | Persistent theme toggle |
| 📱 **Mobile Responsive** | Bootstrap 5 — works on any screen size |

---

## 🗂️ Project Structure

```
travel_planner/
├── app.py                        # Flask application + all API routes
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variable template
├── .env                          # Your local secrets (not committed)
│
├── modules/
│   ├── __init__.py
│   ├── agent_instructions.py     # ← CUSTOMIZE AGENT BEHAVIOR HERE
│   ├── watsonx_client.py         # IBM Watsonx.ai Granite client
│   ├── prompt_builder.py         # Structured prompt constructors
│   └── data_store.py             # In-memory trip & profile storage
│
├── templates/
│   ├── base.html                 # Sidebar + topbar layout
│   ├── index.html                # Landing page
│   ├── dashboard.html            # Main dashboard
│   ├── chat.html                 # AI chat interface
│   ├── itinerary.html            # Itinerary generator
│   ├── destinations.html         # Destination explorer
│   ├── budget.html               # Budget calculator + weather
│   ├── profiles.html             # Traveler profile management
│   └── history.html              # Trip history
│
└── static/
    ├── css/
    │   └── style.css             # Full custom theme (dark + light)
    └── js/
        ├── main.js               # Global utilities, theme, toast, markdown
        ├── chat.js               # Chat UI logic
        ├── itinerary.js          # Itinerary form & result
        ├── destinations.js       # Destination form & result
        ├── budget.js             # Budget form, result, weather
        ├── profiles.js           # Profile CRUD
        └── history.js            # Trip history CRUD + modal
```

---

## ⚙️ Setup Instructions

### 1 — Prerequisites

- Python 3.10+ (3.11 recommended)
- An IBM Cloud account with Watsonx.ai access
- A Watsonx.ai Project ID

### 2 — Get IBM Credentials

1. Log in to [IBM Cloud](https://cloud.ibm.com)
2. Go to **Manage → Access (IAM) → API Keys** → create a new key → copy it
3. Open [IBM Watsonx.ai](https://dataplatform.cloud.ibm.com/wx/home) → open your project → copy the **Project ID** from Settings

### 3 — Clone & Install

```bash
# Clone / download the project
cd travel_planner

# Create virtual environment
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate (macOS / Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4 — Configure Environment

```bash
# Copy the example file
copy .env.example .env          # Windows
cp  .env.example .env           # macOS / Linux
```

Edit `.env` and fill in your real values:

```dotenv
IBM_API_KEY=your_ibm_cloud_api_key_here
IBM_PROJECT_ID=your_watsonx_project_id_here
IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
FLASK_SECRET_KEY=any_long_random_string
```

> 💡 If your Watsonx instance is in a different region, update `IBM_WATSONX_URL`:
> - Dallas (us-south): `https://us-south.ml.cloud.ibm.com`
> - Frankfurt (eu-de): `https://eu-de.ml.cloud.ibm.com`
> - Tokyo (jp-tok): `https://jp-tok.ml.cloud.ibm.com`
> - London (eu-gb): `https://eu-gb.ml.cloud.ibm.com`

### 5 — Run Locally

```bash
python app.py
```

Open your browser at **http://localhost:5000**

---

## 🎛️ Customizing the AI Agent

Open [`modules/agent_instructions.py`](modules/agent_instructions.py) and edit the clearly labelled sections:

| Section | What to change |
|---|---|
| `AGENT_NAME` | Agent's display name |
| `AGENT_PERSONALITY` | Tone, style, persona description |
| `RESPONSE_TONE` | Formatting rules, units, response length |
| `ACTIVE_SPECIALIZATIONS` | Budget, luxury, adventure, pilgrimage, etc. |
| `REGIONAL_FOCUS` | Which countries/regions the agent knows best |
| `ITINERARY_RULES` | What every itinerary must include |
| `BUDGET_RULES` | How costs are broken down and formatted |
| `SAFETY_GUIDELINES` | What safety/legal reminders to always include |
| `WEATHER_GUIDELINES` | Seasonal travel advice rules |
| `CULTURAL_GUIDELINES` | Etiquette and cultural sensitivity rules |
| `FAMILY_PROFILE_RULES` | Age-based recommendations for groups |

No restart is needed for prompt-only changes — they're applied on the next API call.

---

## 🚀 Production Deployment

### Option A — Gunicorn (Linux / macOS)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Option B — IBM Cloud Code Engine

1. Install IBM Cloud CLI: https://cloud.ibm.com/docs/cli
2. Log in and target your project:
   ```bash
   ibmcloud login
   ibmcloud ce project select --name my-travel-planner
   ```
3. Deploy as a Code Engine application:
   ```bash
   ibmcloud ce app create \
     --name voyager \
     --image icr.io/myns/voyager:latest \
     --env IBM_API_KEY=<key> \
     --env IBM_PROJECT_ID=<id> \
     --env IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com \
     --env FLASK_SECRET_KEY=<secret>
   ```

### Option C — IBM Cloud Foundry

Create a `manifest.yml`:
```yaml
applications:
  - name: voyager-travel-planner
    memory: 512M
    instances: 1
    buildpack: python_buildpack
    command: gunicorn -b 0.0.0.0:$PORT app:app
    env:
      IBM_API_KEY: your_key_here
      IBM_PROJECT_ID: your_project_id
      IBM_WATSONX_URL: https://us-south.ml.cloud.ibm.com
      FLASK_SECRET_KEY: your_secret_here
```

Then deploy:
```bash
ibmcloud cf push
```

### Option D — Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
```

```bash
docker build -t voyager .
docker run -p 5000:5000 \
  -e IBM_API_KEY=... \
  -e IBM_PROJECT_ID=... \
  -e IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com \
  -e FLASK_SECRET_KEY=... \
  voyager
```

---

## 🔌 Weather API Integration

The weather feature currently uses Watsonx AI for seasonal summaries.
To connect live weather data, edit the `/api/weather` route in [`app.py`](app.py):

```python
# Replace the AI prompt with a real API call, e.g. OpenWeatherMap:
import requests
OWM_KEY = os.environ.get("OPENWEATHERMAP_API_KEY")
url = f"https://api.openweathermap.org/data/2.5/forecast?q={destination}&appid={OWM_KEY}"
```

---

## 💾 Production Data Storage

The default in-memory store in [`modules/data_store.py`](modules/data_store.py) resets on restart.
For production, swap the store functions with SQLite / PostgreSQL calls:

```python
# Example: replace get_trips() with a DB query
def get_trips(session_id: str) -> list[dict]:
    return db.execute("SELECT * FROM trips WHERE session_id=?", session_id).fetchall()
```

---

## 🔒 Security Notes

- Never commit `.env` to version control (`.gitignore` it)
- Rotate `FLASK_SECRET_KEY` before any public deployment
- For multi-user production apps, replace the in-memory store with a persistent DB and proper auth

---

## 📜 License

MIT — free to use, modify, and deploy.

---

*Powered by IBM Watsonx.ai · IBM Granite · Flask · Bootstrap 5*
