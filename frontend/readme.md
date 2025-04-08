# Setup


## Directions for Windows Users
Create the virtual environment by running the following:

1. Create the virtual environment flight_pred
- First, create a virtual environment named flight_pred: `python -m venv flight_pred`
- Activate the environment:`flight_pred\Scripts\activate`
2. Install Dependencies
- Navigate to the frontend folder and install the necessary packages: `pip install -r requirements.txt`
3. Run the Flask App
- Start the Flask backend from the frontend folder: `python model_flask.py`
4. Launch the Streamlit App
- Open a new terminal tab, activate the environment again, and navigate to the same frontend folder
  - launch the same environemnt: `flight_pred\Scripts\activate`
  - Launch the strealit app: `streamlit run streamlit_app.py`
5. Access the app
- Once the Streamlit server is running, you can access the app in your browser at http://localhost:8501


## Directions for Mac Users
Create the virtual environment by running the following:

1. Create the virtual environment flight_pred
- First, create a virtual environment named flight_pred: `python3 -m venv flight_pred`
- Activate the environment:`source flight_pred/bin/activate`
2. Install Dependencies
- Navigate to the frontend folder and install the necessary packages: `pip install -r requirements.txt`
3. Run the Flask App
- Start the Flask backend from the frontend folder: `python model_flask.py`
4. Launch the Streamlit App
- Open a new terminal tab, activate the environment again, and navigate to the same frontend folder
  - launch the same environemnt: `source flight_pred/bin/activate`
  - Launch the strealit app: `streamlit run streamlit_app.py`
5. Access the app
- Once the Streamlit server is running, you can access the app in your browser at http://localhost:8501
