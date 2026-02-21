from flask import Flask, request, render_template
import pickle
import pandas as pd

app = Flask(__name__, static_url_path='/static', static_folder='templates', template_folder='templates')

# Load the model from the pickle file
with open('model.pkl', 'rb') as file:
    pipeline = pickle.load(file)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Retrieve input data from the form
        input_data = {
            'Age': [int(request.form['Age'])],
            'Gender': [request.form['Gender']],
            'HeartRate': [int(request.form['HeartRate'])],
            'Symptoms': [request.form['Symptoms']],
            'MedicalHistory': [request.form['MedicalHistory']],
            'Smoker': [request.form['Smoker']],
            'Drinker': [request.form['Drinker']],
            'Exercise': [request.form['Exercise']],
            'SleepHours': [int(request.form['SleepHours'])],
            'Weight': [int(request.form['Weight'])],
            'BodyTemperature': [float(request.form['BodyTemperature'])],
            'Lifestyle': [request.form['Lifestyle']],
            'SystolicPressure': [int(request.form['SystolicPressure'])],
            'DiastolicPressure': [int(request.form['DiastolicPressure'])]
        }

        # Create a DataFrame from the input data
        input_df = pd.DataFrame(input_data)
        
        # Ensure that all expected columns are present
        expected_columns = ['Age', 'Gender', 'HeartRate', 'Symptoms', 'MedicalHistory', 'Smoker', 
                            'Drinker', 'Exercise', 'SleepHours', 'Weight', 'BodyTemperature', 
                            'Lifestyle', 'SystolicPressure', 'DiastolicPressure']
        
        if not all(col in input_df.columns for col in expected_columns):
            return "Missing input columns"

        # Predict using the loaded model
        prediction = pipeline.predict(input_df)

        # Construct the response
        report = str(prediction[0][0]).strip()
        suggestions = str(prediction[0][1]).strip()
        habit = str(prediction[0][2]).strip()
        food = str(prediction[0][3]).strip()

        # Add some quick analytics based on inputs
        systolic = int(request.form['SystolicPressure'])
        diastolic = int(request.form['DiastolicPressure'])
        heart_rate = int(request.form['HeartRate'])
        sleep_hours = int(request.form['SleepHours'])

        bp_status = "Normal"
        bp_color = "#34d399" # green
        if systolic >= 140 or diastolic >= 90:
            bp_status = "Hypertension Stage 2"
            bp_color = "#ef4444" # red
        elif systolic >= 130 or diastolic >= 80:
            bp_status = "Hypertension Stage 1"
            bp_color = "#f97316" # orange
        elif systolic >= 120 and diastolic < 80:
            bp_status = "Elevated"
            bp_color = "#eab308" # yellow

        hr_status = "Normal"
        hr_color = "#34d399"
        if heart_rate > 100:
            hr_status = "High (Tachycardia)"
            hr_color = "#f97316"
        elif heart_rate < 60:
            hr_status = "Low (Bradycardia)"
            hr_color = "#38bdf8"

        sleep_status = "Optimal"
        sleep_color = "#34d399"
        if sleep_hours < 7:
            sleep_status = "Insufficient"
            sleep_color = "#f97316"
        elif sleep_hours > 9:
            sleep_status = "Excessive"
            sleep_color = "#eab308"

        vitals = {
            'bp': f"{systolic}/{diastolic}",
            'bp_status': bp_status,
            'bp_color': bp_color,
            'hr': f"{heart_rate} bpm",
            'hr_status': hr_status,
            'hr_color': hr_color,
            'sleep': f"{sleep_hours} hrs",
            'sleep_status': sleep_status,
            'sleep_color': sleep_color
        }

        # Analyze Smoking and Drinking Days
        risk_assessment = []
        is_smoker = request.form['Smoker'] == '1'
        is_drinker = request.form['Drinker'] == '1'
        
        smoker_days_str = request.form.get('SmokerDays', '0')
        drinker_days_str = request.form.get('DrinkerDays', '0')
        
        # Safely parse
        smoker_days = int(smoker_days_str) if smoker_days_str.isdigit() else 0
        drinker_days = int(drinker_days_str) if drinker_days_str.isdigit() else 0

        if is_smoker and smoker_days > 0:
            years = smoker_days / 365.25
            if years > 5:
                risk_assessment.append(f"⚠️ High Risk: Smoking for ~{years:.1f} years drastically increases respiratory and cardiovascular risks. Cumulative lung damage is significant. Immediate cessation is strongly advised.")
            elif years > 1:
                risk_assessment.append(f"⚠️ Moderate Risk: Smoking for ~{years:.1f} years has started to impact lung capacity and blood pressure. Quitting now will begin immediate recovery.")
            else:
                risk_assessment.append(f"⚠️ Early Risk: You started smoking {smoker_days} days ago. Quitting right now will reverse nearly all potential damage within a few months.")

        if is_drinker and drinker_days > 0:
            years = drinker_days / 365.25
            if years > 5:
                risk_assessment.append(f"⚠️ High Risk: Regular heavy drinking for ~{years:.1f} years highly impacts liver enzyme function (AST/ALT), resting heart rate, and metabolic rate.")
            elif years > 1:
                risk_assessment.append(f"⚠️ Moderate Risk: Regular drinking over ~{years:.1f} years places strain on the liver and digestive system. Reduction is key.")
            else:
                risk_assessment.append(f"⚠️ Early Risk: You started drinking {drinker_days} days ago. Ensure adherence to minimal recommended weekly limits to prevent long-term complications.")

        risk_assessment_text = "\n\n".join(risk_assessment) if risk_assessment else "No severe historical lifestyle risks detected from current inputs."

        # Render the result template and pass the output data
        return render_template('result.html', report=report, suggestions=suggestions, habit=habit, food=food, vitals=vitals, risk_assessment=risk_assessment_text)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return str(e)

if __name__ == '__main__':
    print(" Flask server is starting... Open http://127.0.0.1:5000/ in your browser.")
    app.run(debug=True)
