import pickle

with open('/Users/Santosha/Documents/GitHub/dva_flightdelay/frontend/gradient_boost_model_final.pkl', 'rb') as file:
    model = pickle.load(file)
print(model.model.feature_names_in_)
