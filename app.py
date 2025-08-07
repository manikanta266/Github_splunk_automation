from flask import Flask, request, jsonify, render_template, redirect, url_for, send_file, flash
from datetime import datetime
import os
import shutil
import logging
import os
import subprocess
from flask import render_template


app = Flask(__name__)
app.secret_key = 'secret'  # Required for flashing messages

OUTPUT_DIR = os.path.abspath('output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

logger = logging.getLogger(__name__)
app.config['UPLOAD_FOLDER'] = 'C:\\Users\\IMSG\\Desktop\\projects\\dynamicui\\output'


@app.route('/', endpoint='home')
def index():
    return render_template('index_copy.html')


@app.route('/create_app', methods=['GET', 'POST'])
def create_app():
    if request.method == 'GET':
        return render_template('create_app.html')

    try:
        if request.is_json:
            data = request.get_json()
            app_name = data['app_name']
            inputs = data['inputs']
            props = data['props']
            transforms = data.get('transforms', {})
            timestamp = datetime.now().strftime("%b_%Y")
            app_id = f"{app_name.replace(' ', '_')}_{timestamp}"

        else:
            app_name = request.form.get('app_name') or "app"
            timestamp = datetime.now().strftime("%b_%Y")
            app_id = f"{app_name.replace(' ', '_')}_{timestamp}"

            inputs = []
            index = 0
            while True:
                file_path = request.form.get(f'input_{index}_filepath')
                if not file_path:
                    break
                sourcetype = request.form.get(f'input_{index}_sourcetype')
                index_name = request.form.get(f'input_{index}_index')
                input_data = {
                    "filePath": file_path,
                    "sourcetype": sourcetype,
                    "index": index_name,
                    "customFields": []
                }
                cf_idx = 0
                while True:
                    key = request.form.get(f'input_{index}_cf_{cf_idx}_key')
                    if not key:
                        break
                    value = request.form.get(f'input_{index}_cf_{cf_idx}_value')
                    input_data["customFields"].append({"key": key, "value": value})
                    cf_idx += 1
                inputs.append(input_data)
                index += 1

            props = {}
            for key, value in request.form.items():
                if key.startswith('prop_'):
                    parts = key.split('_', 2)
                    if len(parts) == 3:
                        stype, field = parts[1], parts[2]
                        props.setdefault(stype, {})[field] = value

            transforms = {}
            for key, value in request.form.items():
                if key.startswith('transform_'):
                    parts = key.split('_', 2)
                    if len(parts) == 3:
                        tname, field = parts[1], parts[2]
                        transforms.setdefault(tname, {})[field] = value

        app_path = os.path.join(OUTPUT_DIR, app_id, 'default')
        os.makedirs(app_path, exist_ok=True)

        # Write inputs.conf
        with open(os.path.join(app_path, 'inputs.conf'), 'w', encoding='utf-8') as f:
            for idx, inp in enumerate(inputs):
                f.write(f"[monitor://{inp['filePath']}]\n")
                f.write("disabled = false\n")
                f.write(f"sourcetype = {inp['sourcetype']}\n")
                if inp.get('index'):
                    f.write(f"index = {inp['index']}\n")
                for cf in inp.get('customFields', []):
                    if cf.get('key'):
                        f.write(f"{cf['key']} = {cf['value']}\n")
                f.write(f"# Input {idx+1}\n\n")

        # Write props.conf
        with open(os.path.join(app_path, 'props.conf'), 'w', encoding='utf-8') as f:
            for idx, (stype, conf) in enumerate(props.items()):
                f.write(f"[{stype}]\n")
                for key, val in conf.items():
                    f.write(f"{key} = {val}\n")
                f.write(f"# Prop {idx+1}\n\n")

        # Write transforms.conf if exists
        if transforms:
            with open(os.path.join(app_path, 'transforms.conf'), 'w', encoding='utf-8') as f:
                for idx, (name, conf) in enumerate(transforms.items()):
                    f.write(f"[{name}]\n")
                    for key, val in conf.items():
                        f.write(f"{key} = {val}\n")
                    f.write(f"# Transform {idx+1}\n\n")

        if request.is_json:
            return jsonify({
                "message": f"App '{app_id}' created successfully!",
                "path": os.path.abspath(app_path),
                "app_id": app_id
            })
        else:
            return redirect(url_for('browse_files', app_id=app_id))

    except Exception as e:
        logger.exception("Error creating app")
        if request.is_json:
            return jsonify({"error": str(e)}), 400
        else:
            return render_template('error.html', error=str(e))


@app.route('/browse_files/<app_id>/', defaults={'folder_path': ''})
@app.route('/browse_files/<app_id>/<path:folder_path>')
def browse_files(app_id, folder_path):
    base_path = os.path.join(OUTPUT_DIR, app_id)
    abs_path = os.path.normpath(os.path.join(base_path, folder_path))

    # Safety check
    if not abs_path.startswith(os.path.abspath(base_path)):
        flash("Invalid folder path", "danger")
        return redirect(url_for('browse_files', app_id=app_id))

    selected_file = None
    content = ''
    readonly = False
    folders, files = [], []

    if os.path.isfile(abs_path):
        # When a file is selected
        selected_file = os.path.basename(abs_path)
        content = ''
        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            flash(f"Error reading file: {e}", "danger")

        # Still list folder contents (for sidebar) from the file's directory
        folder_path = os.path.dirname(folder_path)
        abs_folder_path = os.path.dirname(abs_path)
    else:
        # Browsing a folder
        abs_folder_path = abs_path

    # List files and folders for the sidebar
    if os.path.isdir(abs_folder_path):
        for entry in sorted(os.listdir(abs_folder_path)):
            full = os.path.join(abs_folder_path, entry)
            rel = os.path.relpath(full, base_path)
            if os.path.isdir(full):
                folders.append({'name': entry, 'full_path': rel})
            elif os.path.isfile(full):
                files.append({'name': entry, 'full_path': rel})

    parent_path = os.path.dirname(folder_path) if folder_path else None

    return render_template(
        'browse_files.html',
        app_id=app_id,
        current_path=folder_path,
        folders=folders,
        files=files,
        parent_path=parent_path,
        selected_file=selected_file,
        content=content,
        readonly=readonly
    )
@app.route('/validate/<app_id>', methods=['POST'])
def validate_and_save(app_id):
    file_path = request.args.get('file', '').lstrip('/')
    content = request.form.get('content', '')

    base_path = os.path.abspath(os.path.join(OUTPUT_DIR, app_id))
    abs_path = os.path.abspath(os.path.normpath(os.path.join(base_path, file_path)))

    # Security check
    if not abs_path.startswith(base_path):
        flash("Invalid file path", "danger")
        return redirect(url_for('browse_files', app_id=app_id))

    # Ensure directory exists
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)

    try:
        # Save file with explicit newline handling
        with open(abs_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        flash("File saved successfully", "success")
    except Exception as e:
        flash(f"Error saving file: {e}", "danger")

    return redirect(url_for('browse_files', app_id=app_id, folder_path=os.path.dirname(file_path)))

@app.route('/browse_files/<app_id>/view/<path:file_path>')
def view_file(app_id, file_path):
    base_path = os.path.join(OUTPUT_DIR, app_id)
    abs_file_path = os.path.normpath(os.path.join(base_path, file_path))

    # Security check: file must be inside app directory
    if not abs_file_path.startswith(os.path.abspath(base_path)):
        flash("Invalid file path.", "danger")
        return redirect(url_for('browse_files', app_id=app_id))

    if not os.path.isfile(abs_file_path):
        flash("File not found.", "danger")
        return redirect(url_for('browse_files', app_id=app_id))

    with open(abs_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    folder_path = os.path.dirname(file_path)
    folders = []
    files = []
    base_folder_path = os.path.join(base_path, folder_path)

    if os.path.exists(base_folder_path):
        for entry in sorted(os.listdir(base_folder_path)):
            full_entry = os.path.join(base_folder_path, entry)
            if os.path.isdir(full_entry):
                folders.append({'name': entry, 'full_path': os.path.relpath(full_entry, base_path)})
            elif os.path.isfile(full_entry):
                files.append({'name': entry, 'full_path': os.path.relpath(full_entry, base_path)})

    parent_path = os.path.dirname(folder_path) if folder_path else None

    return render_template(
        'browse_files.html',
        app_id=app_id,
        current_path=folder_path,
        folders=folders,
        files=files,
        parent_path=parent_path,
        selected_file=file_path,
        content=content,
        readonly=False,
      
    )


@app.route('/save_file/<app_id>/<path:file_path>', methods=['POST'])
def save_file(app_id, file_path):
    base_path = os.path.join(OUTPUT_DIR, app_id)
    abs_file_path = os.path.normpath(os.path.join(base_path, file_path))

    # Security check: file inside app directory
    if not abs_file_path.startswith(os.path.abspath(base_path)):
        flash("Invalid file path.", "danger")
        return redirect(url_for('browse_files', app_id=app_id))

    content = request.form.get('content', '')

    try:
        with open(abs_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        flash(f"File '{file_path}' saved successfully.", "success")
    except Exception as e:
        flash(f"Error saving file: {str(e)}", "danger")

    return redirect(url_for('view_file', app_id=app_id, file_path=file_path))


@app.route('/download_app')
def download_app():
    app_id = request.args.get('app_id')
    if not app_id:
        return "Missing app_id", 400

    app_folder = os.path.join(OUTPUT_DIR, app_id)
    if not os.path.exists(app_folder):
        return f"App '{app_id}' does not exist.", 404

    zip_path = os.path.join(OUTPUT_DIR, f"{app_id}.zip")
    shutil.make_archive(zip_path.replace(".zip", ""), 'zip', app_folder)

    return send_file(zip_path, as_attachment=True)


# @app.route('/upload_to_splunk', methods=['POST'])
# def upload_to_splunk():
#     app_id = request.args.get('app_id')
#     if not app_id:
#         flash("Missing app_id for upload.", "danger")
#         return redirect(url_for('home'))

#     # TODO: Implement upload logic here
#     flash(f"Upload to Splunk requested for app_id: {app_id}", "success")
#     return redirect(url_for('browse_files', app_id=app_id))


@app.route('/delete_file', methods=['POST'])
def delete_file():
    app_id = request.form.get('app_id')
    file_path = request.form.get('file_path')

    if not app_id or not file_path:
        flash("Missing app_id or file_path.", "danger")
        return redirect(request.referrer or url_for('home'))

    app_folder = os.path.abspath(os.path.join(OUTPUT_DIR, app_id))
    target_path = os.path.abspath(os.path.join(app_folder, file_path))

    if not target_path.startswith(app_folder):
        flash("Invalid file path.", "danger")
        return redirect(request.referrer or url_for('home'))

    if not os.path.exists(target_path):
        flash("File does not exist.", "danger")
        return redirect(request.referrer or url_for('home'))

    try:
        if os.path.isfile(target_path):
            os.remove(target_path)
            flash(f"Deleted file: {os.path.basename(target_path)}", "success")
        elif os.path.isdir(target_path):
            shutil.rmtree(target_path)
            flash(f"Deleted folder: {os.path.basename(target_path)}", "success")
        else:
            flash("Not a file or directory.", "danger")
    except Exception as e:
        flash(f"Error deleting file: {str(e)}", "danger")

    return redirect(request.referrer or url_for('browse_files', app_id=app_id))
from flask import jsonify

from flask import jsonify
import os
import subprocess
from flask import jsonify
import time
import random

    # @app.route('/upload_to_splunk/<app_id>', methods=['POST'])
    # def upload_to_splunk(app_id):
    #     messages = []

    #     try:
    #         # Dummy delay to simulate processing
    #         time.sleep(1)

    #         # Simulate success or failure randomly (you can set it fixed for testing)
    #         success = True  # Set to False to test failure flow

    #         if success:
    #             messages.append(f"✅ Dummy: App '{app_id}' uploaded successfully!")
    #             messages.append("✅ Dummy: btool validation passed successfully!")
    #             messages.append("✅ Dummy: Splunk restarted successfully!")

    #             splunk_ui_url = "http://127.0.0.1:8000/en-GB/account/login?return_to=%2Fen-GB%2F"
    #             return jsonify(status="success", messages=messages, splunk_ui_url=splunk_ui_url)
    #         else:
    #             messages.append("❌ Dummy: Upload failed due to some error.")
    #             return jsonify(status="error", messages=messages)

    #     except Exception as e:
    #         messages.append(f"❌ Dummy: An unexpected error occurred: {str(e)}")
    #         return jsonify(status="error", messages=messages)
        

import base64, requests, time
from flask import Flask, request, jsonify

@app.route('/upload_to_github', methods=['POST'])
def upload_to_github():
    username = request.json['username']
    repo = request.json['repo']
    path = request.json.get('path', 'props.conf')
    content = request.json['content']
    commit_msg = request.json.get('message', 'Update via app')

    token = 'YOUR_GITHUB_TOKEN'
    url = f'https://api.github.com/repos/{username}/{repo}/contents/{path}'
    headers = {'Authorization': f'token {token}'}

    try:
      # Check if file exists to get SHA for update
      resp = requests.get(url, headers=headers)
      sha = resp.json().get('sha') if resp.status_code == 200 else None

      body = {
        "message": commit_msg,
        "content": base64.b64encode(content.encode('utf-8')).decode('utf-8')
      }
      if sha:
        body["sha"] = sha

      put_resp = requests.put(url, json=body, headers=headers)
      resp_json = put_resp.json()
      status = 'success' if put_resp.status_code in (200, 201) else 'error'
      message = resp_json.get('commit', {}).get('message') or resp_json.get('message')
      return jsonify(status=status, messages=[message], html_url=resp_json.get('content', {}).get('html_url'))
    except Exception as e:
      return jsonify(status='error', messages=[str(e)])


import os
import subprocess
from flask import Flask, request, jsonify

app.config['UPLOAD_FOLDER'] = r"C:\Users\Chinthala Manikanta\Downloads\Dynamic_splunk_ui\dynamicui\output"

@app.route('/upload_to_splunk/<app_id>', methods=['POST'])
def upload_to_splunk(app_id):
    messages = []

    try:
        # Define paths
        app_folder_path = os.path.join(app.config['UPLOAD_FOLDER'], app_id)
        splunk_apps_dir = r"C:\Program Files\splunk\etc\apps"
        splunk_app_path = os.path.join(splunk_apps_dir, app_id)

        # Check if the app folder exists in output
        if not os.path.exists(app_folder_path):
            messages.append(f"❌ App folder '{app_id}' not found at output directory!")
            return jsonify(status="error", messages=messages)

        # Move the app folder to Splunk's apps directory
        try:
            os.rename(app_folder_path, splunk_app_path)
            messages.append(f"✅ App '{app_id}' moved to Splunk apps directory!")
        except Exception as move_err:
            messages.append(f"❌ Failed to move app folder: {str(move_err)}")
            return jsonify(status="error", messages=messages)

        # Run btool to validate the configuration
        btool_cmd = r'"C:\Program Files\splunk\bin\splunk.exe" btool inputs list --debug'
        result = subprocess.run(btool_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode != 0:
            btool_error = result.stderr.decode(errors='replace')
            messages.append(f"❌ btool validation failed: {btool_error}")
            return jsonify(status="error", messages=messages)

        messages.append("✅ btool validation passed!")

        # Restart Splunk
        restart_cmd = r'"C:\Program Files\splunk\bin\splunk.exe" restart'
        restart_result = subprocess.run(restart_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if restart_result.returncode != 0:
            restart_error = restart_result.stderr.decode(errors='replace')
            messages.append(f"❌ Failed to restart Splunk: {restart_error}")
            return jsonify(status="error", messages=messages)

        messages.append("✅ Splunk restarted successfully!")

        # Splunk web interface URL (adjust if needed)
        splunk_ui_url = "http://127.0.0.1:8000/en-GB/account/login?return_to=%2Fen-GB%2F"

        return jsonify(status="success", messages=messages, splunk_ui_url=splunk_ui_url)

    except Exception as e:
        messages.append(f"❌ Unexpected error: {str(e)}")
        return jsonify(status="error", messages=messages)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
