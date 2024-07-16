## GIT STRUCTURE TO BE FOLLOWED:
<div align="center">
   <img src= "https://github.com/Asoft-Consulting-LLC/demohub-ai/blob/main/git_structure.png" width="300" height="300" alt="git structure">
</div>

- The nomenclature of all feature branches should reflect their functionality
- Each feature branch should be pushed to respective branches and closed after development
- Pull from main/development branch before working on a new feature
- Merge conflicts to be resolved only in team meetings

# Pre-requisites 
- [Git](https://git-scm.com/downloads)
- [Git setup - username and password](https://docs.github.com/en/get-started/getting-started-with-git/setting-your-username-in-git)
- [Python (version 3.12)](https://www.python.org/downloads/release/python-3120/)

- Clone the repository to your local machine:

 ```sh
 git clone git@github.com:Asoft-Consulting-LLC/demohub-ai.git
 ```
- Create and Ensure backend/.env file has the following environment variables set:
```sh
AUTH_SECRET_KEY="YOUR_AUTH_SECRET_KEY"
AUTH_ALGORITHM="YOUR_AUTH_ALGORITHM"
``` 
- Create a json file called db.json in backend folder with an empty list intialized, i.e, content of db.json intially should be 
```
[]
```
 
# Initial setup

## Back-end 
1. Navigate to `backend` directory

2.  Run the following command to create a new virtual environment called `venv`:
```sh
python3 -m venv venv
```

3.  Activate virtual environment on Windows:
```sh
 venv\Scripts\activate
```
or on Linux/macOS:
```sh
source venv/bin/activate
```
4. Install requirements:
```sh
pip install -r requirements.txt
```
5. Run FastAI application:
```sh
uvicorn main:app --reload --log-config=log_conf.yaml
```
6. To access back-end routes directly using FastAPI's Swagger, go to the URL:
```sh
http://127.0.0.1:8000/docs
```
