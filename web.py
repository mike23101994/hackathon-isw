########################################################
# CREATED BY MAINAK CHAKRABARTY
# INTENTION OF THIS WEBSITE TO GET A CONSOLIDATED INFO IN JUST A FEW CLICKS WITH NO COST INCURING FOR US.
# LEVERAGING HTML AND CSS TO GET THE METRICS ONTO UI AND USING API TO PUSH REQUIRED DATA
# SAVES LOT OF COST PER PRODUCT IF WE CAN USE THIS PORTAL TO GET THE BASIC INFO WHICH WILL OTHERWISE INCUR COST IF 
# MONITORING TOOL IS USED
########################################################



import sys , logging
from flask import Flask, jsonify, render_template, request
from logging.handlers import RotatingFileHandler
from a4sutils import display,predict_cpu_usage,get_info_for_all_customer_in_a4s_dev,get_a4s_dev_account_info, get_a4s_demo_account_info, get_a4s_prod_account_info

# Configure root logger
logging.basicConfig(level=logging.INFO)

# Add additional logging handler (e.g., stdout)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)

# Create logger
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/product/A4S', methods=['GET'])
def get_a4s_logs():
    if request.method == 'GET':
        return render_template('A4S.html')

@app.route('/product/A4O', methods=['GET'])
def get_a4o_logs():
    if request.method == 'GET':
        return render_template('A4S.html')

@app.route('/product/SCC', methods=['GET'])
def get_scc_logs():
    if request.method == 'GET':
        return render_template('A4S.html')

@app.route('/product/Angles-Pro', methods=['GET'])
def get_angles_pro_logs():
    if request.method == 'GET':
        return render_template('A4S.html')

#############################
# ROUTES FOR A4S RPODUCT
#############################

@app.route('/product/A4S/A4S-Dev-Acc', methods=['GET', 'POST'])
def get_a4s_dev_account_info_route():
    return get_a4s_dev_account_info()

@app.route('/product/A4S/A4S-Dev-Acc/Compare', methods=['GET'])
def get_all_info_a4s_dev():
    return get_info_for_all_customer_in_a4s_dev()

@app.route('/product/A4S/A4S-Dev-Acc/Predict', methods=['POST'])
def predict_cpu_usage_route():
    try:
        selected_customer = request.form.get('selected_customer')
        html_path = predict_cpu_usage(selected_customer)  
        return jsonify({'html_path': html_path})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/product/A4S/A4S-Dev-Acc/Predict/Display', methods=['GET'])
def display_chart():
    return display()

@app.route('/product/A4S/A4S-Demo-Acc', methods=['GET', 'POST'])
def get_a4s_demo_account_info_route():
    return get_a4s_demo_account_info()

# Route for A4S Prod AWS account information
@app.route('/product/A4S/A4S-Prod-Acc', methods=['GET', 'POST'])
def get_a4s_prod_account_info_route():
    return get_a4s_prod_account_info()

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0")
    except Exception as e:
        # Log any errors or exceptions that occur during application startup or execution
        logging.exception("An error occurred during Flask application execution: %s", str(e))
