
import logging,json,sys,os,json
from flask import jsonify, render_template, request
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
import pandas as pd
import ast
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import LabelEncoder
import base64,os
from io import BytesIO
from flask import send_file

######################################
# LOGGING LOGICS
######################################
logging.basicConfig(level=logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)

#######################################
# GLOBAL VARIABLES
#######################################

logger = logging.getLogger(__name__)
data_dir = '/home/ec2-user/data'
predict_dir = '/home/ec2-user/web-app/CloudUtilities/CloudCanvas/templates'


#######################################
# COMMON FUNCTIONS
#######################################

if not os.path.exists(data_dir):
    os.makedirs(data_dir)

def create_file_if_not_exists(file_path):
    if not os.path.exists(file_path):
        open(file_path, 'a+').close()

def fetch_logs_for_customer(customer, product):
    file_path = os.path.join(data_dir, f"{product}_data.txt")
    try:
        with open(file_path, 'r') as file:
            logs = [line.strip() for line in file if line.strip() and customer in line]
        return logs
    except FileNotFoundError:
        return []
    except Exception as e:
        logging.exception(f"Error fetching logs for customer {customer}: {str(e)}")
        return []


def get_customer_names(file_path):
    customer_names = []
    with open(file_path, 'r') as file:
        for line in file:
            try:
                data = json.loads(line)
                customer = data.get('customer')  
                if customer is not None:  
                    customer_names.append(customer)
                else:
                    logger.warning(f"Missing or null 'customer' field in line: {line.strip()}")
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON in line: {line.strip()}")
            except KeyError as e:
                logger.error(f"KeyError in line: {line.strip()}")
    return customer_names


def remove_duplicate_and_old_records(file_path, new_data):
    try:
        with open(file_path, 'r') as file:
            data = file.readlines()

        # Parse existing data and filter records older than 15 days
        customer_data = {}
        for entry in data:
            entry_data = json.loads(entry)
            customer = entry_data['customer']
            timestamp = datetime.strptime(entry_data['Timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")
            if datetime.now() - timestamp <= timedelta(days=15):
                if customer in customer_data:
                    existing_timestamp = datetime.strptime(customer_data[customer]['Timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    if timestamp > existing_timestamp:
                        customer_data[customer] = entry_data
                else:
                    customer_data[customer] = entry_data

        # Add new data
        customer = new_data['customer']
        timestamp = datetime.strptime(new_data['Timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")
        if customer not in customer_data or timestamp > datetime.strptime(customer_data[customer]['Timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ"):
            customer_data[customer] = new_data

        # Write filtered data back to the file
        with open(file_path, 'w') as file:
            filtered_data = [json.dumps(entry_data) for entry_data in customer_data.values()]
            file.write('\n'.join(filtered_data))
            file.write('\n')
            
        return 'Data stored successfully'
    except Exception as e:
        logging.exception(f"Error storing data: {str(e)}")
        return f"Error storing data: {str(e)}"
    

def get_cpu_prediction_plot(selected_customer_name, file_path,predict_dir):

    html_file_path = os.path.join(predict_dir, "cpu_prediction_plot.html")

    if os.path.exists(html_file_path):
        os.remove(html_file_path)
        print(f"Deleted existing HTML file: {html_file_path}")
    if not os.path.exists(predict_dir):
        os.makedirs(predict_dir)

    try:
        with open(file_path, 'r') as file:
            data = file.readlines()
        installed_software_data = []
        cpu_metrics_data = []
        customer_data = []

        for entry in data:
            parsed_data = ast.literal_eval(entry)
            installed_software = parsed_data.get('InstalledSoftware', [])
            cpu_metrics = parsed_data.get('CPUMetrics', [])
            customer = parsed_data.get('customer')  
            installed_software_data.extend(installed_software)
            cpu_metrics_data.extend(cpu_metrics)
            customer_data.extend([customer] * len(installed_software))

        installed_software_df = pd.DataFrame(installed_software_data)
        cpu_metrics_df = pd.DataFrame(cpu_metrics_data)
        customer_df = pd.DataFrame(customer_data, columns=['customer'])

        final_df = installed_software_df.merge(cpu_metrics_df, left_index=True, right_index=True)
        final_df['customer'] = customer_df['customer']

        label_encoder = LabelEncoder()
        final_df['Name_encoded'] = label_encoder.fit_transform(final_df['Name'])

        X = final_df[['Name_encoded']]
        y = final_df['CPUUsage']
        model = RandomForestRegressor()
        model.fit(X, y)

        selected_customer = selected_customer_name

        filtered_df = final_df[final_df['customer'] == selected_customer]

        X_selected_customer = filtered_df[['Name_encoded']]

        predicted_cpu_usage = model.predict(X_selected_customer)

        filtered_df['Predicted_CPUUsage'] = predicted_cpu_usage
        combined_df = pd.concat([filtered_df[['Name', 'CPUUsage']].rename(columns={'CPUUsage': 'Usage', 'Name': 'Software', }), 
                                filtered_df[['Name', 'Predicted_CPUUsage']].rename(columns={'Predicted_CPUUsage': 'Usage', 'Name': 'Software'})],
                                keys=['Actual', 'Predicted'])

        plt.figure(figsize=(12, 8))
        sns.barplot(data=combined_df.reset_index(), y='Software', x='Usage', hue='level_0', palette=['blue', 'orange'], orient='horizontal')
        plt.title(f'Actual vs Predicted CPU Usage for Customer: {selected_customer}')
        plt.xlabel('CPU Usage')
        plt.ylabel('Software Names')
        plt.tight_layout()
        plt.legend(title='Type')
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plot_bytes = buffer.getvalue()
        encoded_plot = base64.b64encode(plot_bytes).decode('utf-8')

        html_str = f"""
        <html>
        <head><title>CPU Prediction Plot</title></head>
        <body>
        <h2>Actual vs Predicted CPU Usage for Customer: {selected_customer}</h2>
        <img src="data:image/png;base64,{encoded_plot}">
        </body>
        </html>
        """

        html_path = os.path.join(predict_dir, "cpu_prediction_plot.html")
        with open(html_path,"w") as f:
            f.write(html_str)
        return html_path

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

#####################################
# FUNCTION FOR A4S DEV ACCOUNT
#####################################

def predict_cpu_usage(customer):
    try:
        html_path = get_cpu_prediction_plot(customer, os.path.join(data_dir, "A4S_Dev_data.txt"),predict_dir)
        return 'CPU usage prediction completed successfully', html_path
    except Exception as e:
        return f"Error in predicting the customer cpu usage: {str(e)}"

def display():
    try:
        html_path =  os.path.join(predict_dir, "cpu_prediction_plot.html")
        return send_file(html_path)
    except Exception as e:
        logger.error(f"Error in rendering the file: {str(e)}")
        return jsonify({"error": "Error rendering prediction file. No prediction are made currently for this customer"}), 500

def read_installed_software_from_file(file_path):
    installed_software_data = []

    with open(file_path, 'r') as file:
        for line in file:  # Iterate over each line in the file
            customer_data = json.loads(line)  # Load JSON data from each line
            customer_name = customer_data.get('customer')
            installed_software = customer_data.get('InstalledSoftware')

            customer_info = {
                'customer': customer_name,
                'installed_software': installed_software
            }
            installed_software_data.append(customer_info)

    return installed_software_data

def get_info_for_all_customer_in_a4s_dev():
    try:
        data = read_installed_software_from_file(os.path.join(data_dir, "A4S_Dev_data.txt"))
        customer_info_list = [] 
        software_names = set()  
        software_data = {}  

        for entry in data:
            customer_name = entry.get('customer')
            if not customer_name:
                continue  
            installed_software = entry.get('software', [])  
            customer_info_entry = {
                'customer': customer_name,
                'software': installed_software
            }
            customer_info_list.append(customer_info_entry)
            #logger.info(f"customer_info_list content :{customer_info_entry}")

            for software in installed_software:
                software_name = software.get('Name')
                software_version = software.get('Version')
                if software_name:
                    software_names.add(software_name)
                    if customer_name not in software_data:
                        software_data[customer_name] = {}
                    software_data[customer_name][software_name] = software_version

        return render_template("A4S_Dev_Compare.html", data=data, software_names=list(software_names), software_data=software_data)

    except Exception as e:
        return f"Error fetching data for all customers: {str(e)}"
   
def get_a4s_dev_account_info():
    if request.method == 'GET':
        try:
            customer_names = get_customer_names(os.path.join(data_dir, "A4S_Dev_data.txt"))
            logger.info(f"Customer Names: {customer_names}")
        except Exception as e:
            customer_names = []
            logging.error(f"Error fetching customer names: {str(e)}")
            return jsonify({"error": "Error fetching customer names"}), 500

        default_customer = customer_names[0]
        selected_customer = request.args.get('customer', default_customer)
        
        try:
            logs = fetch_logs_for_customer(selected_customer, "A4S_Dev")
            if logs:
                logs_str = logs[0]
                logs_dict = json.loads(logs_str)
            else:
                logs_dict = {}
        except Exception as e:
            logging.error(f"Error fetching logs for customer '{selected_customer}': {str(e)}")
            return jsonify({"error": "Error fetching logs"}), 500

        try:     
            installed_software = logs_dict.get('InstalledSoftware', [])
            for software in installed_software:
                name = software.get('Name')
                version = software.get('Version')
                logger.info(f"Name: {name}, Version: {version}")

            system_updates = logs_dict.get('SystemUpdates', [])
            for update in system_updates:
                description = update.get('Description')
                installed_on = update.get('InstalledOn')
                hotfix_id = update.get('HotFixID')
                logger.info(f"Description: {description}, Installed On: {installed_on}, HotFix ID: {hotfix_id}")

            cpumetric = logs_dict.get('CPUMetrics', [])
            for cpu in cpumetric:
                process_name = cpu.get('ProcessName')
                cpu_usage = cpu.get('CPUUsage')
                logger.info(f"ProcessName: {process_name}, CPUUsage: {cpu_usage}")

        except Exception as e:
            logger.error(f"Error in getting the components: {str(e)}")
            return jsonify({"error": "Error getting components"}), 500

        try:
            return render_template('A4S-Acc.html', customer_names=customer_names, logs=logs_dict, selected_customer=selected_customer, installed_software=installed_software, system_updates=system_updates, cpumetric=cpumetric)
        except Exception as e:
            logger.error(f"Error in rendering the file: {str(e)}")
            return jsonify({"error": "Error rendering file"}), 500
    elif request.method == 'POST':
        try:
            data = request.json
            create_file_if_not_exists(os.path.join(data_dir, "A4S_Dev_data.txt"))
            remove_duplicate_and_old_records(os.path.join(data_dir, "A4S_Dev_data.txt"), data)
            return 'Data stored successfully'
        except Exception as e:
            logging.exception(f"Error storing data: {str(e)}")
            return f"Error storing data: {str(e)}"



###############################################
# TO BE DONE
###############################################

def get_a4s_demo_account_info():
    aws_account_info = {
        'account_id': 'DEMO123456789012',
    }
    return jsonify(aws_account_info)

# Route for A4S Prod AWS account information
def get_a4s_prod_account_info():
    aws_account_info = {
        'account_id': 'PROD123456789012',
    }
    return jsonify(aws_account_info)
