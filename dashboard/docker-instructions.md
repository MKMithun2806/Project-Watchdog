1. Prerequisites
	•	Docker installed on your system
	•	Optional: Docker Compose (if you want multi-container setup later)
2. Build & Deploy

```
docker build -t streamlit-dashboard:latest . && docker run -d -p 8501:8501 --name my-streamlit streamlit-dashboard:latest
```
Run this inthe dashboards folder btw

3.access at http://<yourip>:8501
