# Description
Flight Delay Assistant is a predictive tool that helps passengers make smarter flight choices by estimating the probability of delays. Built using over 28 million U.S. flight operation records, our model predicts whether a selected flight will arrive on time, late (15–45 minutes delay), or very late (over 45 minutes delay). Unlike most existing tools that only report historical averages, we classify delays into these actionable time ranges and provide probability estimates for each class. The model uses a multiclass classification approach to produce probabilities across these three categories.

Unlike many solutions that rely on weather forecasts, our model avoids weather data — focusing instead on robust operational features like flight timing, aircraft type, and airport performance to ensure reliability for advance bookings. The user-facing app, developed with Streamlit, allows travelers to input a flight number, date, and time to instantly see delay probabilities in an intuitive bar chart format.

Developed by Team 115: Scott Crabtree, Rodrigo González, Prabakaran Rajagopal, Santosha Spickard, and Bruce Volpe.

# Installation

## Directions for Windows Users
Create the virtual environment by running the following:

1. Create the virtual environment flight_pred
- First, create a virtual environment named flight_pred: `python -m venv flight_pred`
- Activate the environment:`code\flight_pred\Scripts\activate`
2. Install Dependencies
- Navigate to the `code/frontend` folder and install the necessary packages: `pip install -r requirements.txt`
3. Run the Flask App
- Start the Flask backend from the `code/frontend` folder: `python model_flask.py`
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
- Navigate to the `code/frontend` folder and install the necessary packages: `pip install -r requirements.txt`
3. Run the Flask App
- Start the Flask backend from the `code/frontend` folder: `python model_flask.py`
4. Launch the Streamlit App
- Open a new terminal tab, activate the environment again, and navigate to the same `code/frontend` folder
  - launch the same environemnt: `source flight_pred/bin/activate`
  - Launch the strealit app: `streamlit run streamlit_app.py`
5. Access the app
- Once the Streamlit server is running, you can access the app in your browser at http://localhost:8501

# Execution
Once you have completed the installation steps, you can access the app by navigating to http://localhost:8501 in your browser.

With this tool, you can:
- Explore airport statistics by hovering over airports on the map to view the airport name, city, state, number of flights, percentage of delayed flights, and average delay time.
- Predict flight delays by selecting a flight date, time, and flight number. After clicking the search button, the app will display the predicted probabilities for the flight arriving:
  - On time (≤15 minutes late)
  - Late (>15 minutes and ≤45 minutes late)
  - Very late (>45 minutes late)
