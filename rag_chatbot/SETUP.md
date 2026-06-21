# Setup Instructions

## Local Development

1. **Get a Groq API Key**
   - Visit [Groq Console](https://console.groq.com)
   - Sign up/Login and create an API key

2. **Create `.env` file**
   ```
   GROQ_API_KEY=your_api_key_here
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**
   ```bash
   streamlit run app.py
   ```

## Deployment on Streamlit Cloud

1. **Push your repo** to GitHub (without `.env` file - it's in `.gitignore`)

2. **Connect to Streamlit Cloud**
   - Go to [Streamlit Cloud](https://share.streamlit.io)
   - Deploy your GitHub repo

3. **Set the API Key**
   - In your app dashboard, click **Settings** (gear icon)
   - Go to **Secrets**
   - Paste the following and fill in your key:
     ```toml
     GROQ_API_KEY = "your_groq_api_key_here"
     ```
   - Click **Save**

4. **Reboot the app** - it will now have access to `GROQ_API_KEY`

## Why `.env` is not uploaded

The `.env` file is listed in `.gitignore` for security reasons - never commit API keys to version control. Streamlit Cloud provides a secure Secrets manager for this purpose.
