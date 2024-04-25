from flask import Flask, request, jsonify, send_from_directory, url_for
from flask_httpauth import HTTPTokenAuth
from flask_cors import CORS  # Import CORS
import os
import time
import subprocess
import shlex
from flask_rq2 import RQ
from flask_socketio import SocketIO, emit
from rq.job import Job, get_current_job
from rq import Queue
from werkzeug.middleware.proxy_fix import ProxyFix
import requests

MIME_TYPES_TO_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "video/mp4": ".mp4",
}

# Initialize Flask app and HTTP auth handler
app = Flask(__name__)
RQ_REDIS_URL = "redis://redis:6379/0"
app.config["RQ_REDIS_URL"] = (
   RQ_REDIS_URL
)
# Initialize RQ
rq = RQ(app)
socketio = SocketIO(app, message_queue=RQ_REDIS_URL)
socketio.init_app(app, cors_allowed_origins=["https://phh.internal"])

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1, x_for=1)
auth = HTTPTokenAuth(scheme="Bearer")

CORS(app,supports_credentials=True, origins=["https://phh.internal"])

API_KEY = os.environ.get("API_KEY")
SOURCE_DIR = "/usr/src/app/source"
TARGET_DIR = "/usr/src/app/target"
OUTPUT_DIR = "/usr/src/app/output"

DIRS = {
    "source": SOURCE_DIR,
    "target": TARGET_DIR,
    "output": OUTPUT_DIR,
}


# Token verification function
@auth.verify_token
def verify_token(token):
    return token == API_KEY


def map_jobs(job):
    return {"job_id": job.id, "output_file": job.kwargs.get("output_file")}


@app.route("/auth", methods=["GET"])
@auth.login_required
def check_auth():
    started_job_ids = rq.get_queue().started_job_registry.get_job_ids()
    job_ids = rq.get_queue().job_ids + started_job_ids
    jobs = list(
        map(
            map_jobs,
            Job.fetch_many(job_ids, connection=rq.connection),
        )
    )

    return (
        jsonify({"jobs": jobs}),
        200,
    )


@app.route("/download_target", methods=["POST"])
@auth.login_required
def download_file():
    # Check if a file is part of the request
    if 'media' not in request.files:
        return jsonify({"error": "No media file provided"}), 400

    file = request.files['media']

    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:

        mime_type = file.content_type
        file_extension =  MIME_TYPES_TO_EXTENSIONS.get(mime_type, "")

        # If the file type is not supported, return an error
        if not file_extension:
            return jsonify({"error": "Unsupported file type"}), 400

        # Construct the new filename using a timestamp
        timestamp = int(time.time())
        new_filename = f"{timestamp}{file_extension}"

        # Save the file
        file.save(os.path.join(TARGET_DIR, new_filename))

        # Construct URL for the saved file
        file_url = url_for('serve_file', dir="target", filename=new_filename, _external=True),

        return jsonify({"name": new_filename, "url": file_url[0]}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download_source", methods=["POST"])
@auth.login_required
def download_source():
    # Check if a file is part of the request
    if 'media' not in request.files:
        return jsonify({"error": "No media file provided"}), 400

    file = request.files['media']

    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        mime_type = file.content_type
        file_extension =  MIME_TYPES_TO_EXTENSIONS.get(mime_type, "")

        if not file_extension:
            return jsonify({"error": "Unsupported file type"}), 400

        
        timestamp = int(time.time())
        new_filename = f"{timestamp}{file_extension}"

        
        file.save(os.path.join(SOURCE_DIR, new_filename))

        
        file_url = url_for('serve_file', dir="source", filename=new_filename, _external=True),

        return jsonify({"name": new_filename, "url": file_url[0]}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

import base64
@app.route("/inpaint", methods=["POST"])
@auth.login_required
def inpaint():
    data = request.json
    source = data['source']
    image = data['image']
    mask = data['mask']
    width = data['width']
    height = data['height']
    prompt = data['prompt']
    negative_prompt = data['negative_prompt']


    payload = {
        "init_images": [image],
        "resize_mode": 1,
        "width": width,
        "height": height,
        "denoising_strength": 0.9,
        "mask": mask,
        "mask_blur": 5,
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "steps": 26,
        "sampler_index": "DPM++ 2M Karras",
        "inpaint_full_res": False,
    }

    api_url = "https://sd.phh.internal/sdapi/v1/img2img"

    try:
        # Make the POST request to the next API
        response = requests.post(api_url, json=payload)

        result = response.json()
        image = result['images'][0]

        if not image.startswith('data:image'):
            # If not, prepend the data URL prefix
            image = 'data:image/png;base64,' + image

        # The incoming Base64 string has a prefix that needs to be removed before decoding
        header, encoded = image.split(",", 1)

        # Decode the Base64 string, correcting padding issues
        if len(encoded) % 4:
            encoded += '=' * (4 - len(encoded) % 4)
        decoded = base64.b64decode(encoded)

        output_file_name = f"{int(time.time())}_{source}"

        # Save the image
        with open(os.path.join(OUTPUT_DIR, output_file_name), 'wb') as f:
            f.write(decoded)

        file_url = url_for('serve_file', dir="output", filename=output_file_name, _external=True),

        return jsonify({"name": output_file_name, "url": file_url[0]}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to delete a file
@app.route("/delete_file", methods=["DELETE"])
@auth.login_required
def delete_file():
    dir = request.json.get("dir")
    filename = request.json.get("name")

    if not filename:
        return jsonify({"error": "Missing file name"}), 400

    # Construct the full file path
    dir_path = DIRS.get(dir)
    if not dir_path:
        return jsonify({"error": "Wrong dir"}), 400

    file_path = os.path.join(dir_path, filename)

    # Check if the file exists
    if not os.path.exists(file_path):
        return jsonify({"error": "File does not exist"}), 404

    try:
        # Remove the file
        os.remove(file_path)
        return jsonify({"message": "File deleted successfully"}), 200
    except Exception as e:
        # Return an error message if something goes wrong
        return jsonify({"error": str(e)}), 500


# Route to list files in the output directory
@app.route("/list-output", methods=["GET"])
@auth.login_required
def list_output():
    files = [
        {"name": file, "url": url_for('serve_file', dir="output", filename=file, _external=True)}
        for file in os.listdir(OUTPUT_DIR)
    ]
    return jsonify({"data": files})


@app.route("/list-source", methods=["GET"])
@auth.login_required
def list_source():
    files = [
        {"name": file, "url": url_for('serve_file', dir="source", filename=file, _external=True)}
        for file in os.listdir(SOURCE_DIR)
    ]
    return jsonify({"data": files})


@app.route("/list-target", methods=["GET"])
@auth.login_required
def list_target():
    files = [
        {"name": file, "url": url_for('serve_file', dir="target", filename=file, _external=True)}
        for file in os.listdir(TARGET_DIR)
    ]
    return jsonify({"data": files})


# Route to serve files from the output directory
@app.route("/files/<dir>/<filename>", methods=["GET"])
# @auth.login_required
def serve_file(dir, filename):
    dir_path = DIRS.get(dir)
    if not dir_path:
        return jsonify({"error": "Wrong dir"}), 400

    return send_from_directory(dir_path, filename)

from rq.command import send_kill_horse_command
from rq.worker import Worker, WorkerStatus
# Route to serve files from the output directory
@app.route("/stop-all", methods=["POST"])
# @auth.login_required
def stop_all():
    rq.get_queue().empty()
    workers = Worker.all(rq.connection)
    for worker in workers:
        if worker.state == WorkerStatus.BUSY:
            send_kill_horse_command(rq.connection, worker.name)

    return jsonify({"success": True})


def run_job(command, output_file):
    job = get_current_job(connection=rq.connection)
    print(f"PROCESSING JOB ID: {job.id} for OUTPUT_FILE: {output_file}")

    socketio = SocketIO(message_queue=RQ_REDIS_URL)
    socketio.emit(
        "job_start",
        {
            "job_id": job.id,
            "output_file": output_file,
        },
    )

    # Execute the command
    try:
        subprocess.run(shlex.split(command), check=True)
        print(f"JOB COMPLETED: {job.id} for OUTPUT_FILE: {output_file}")
    except subprocess.CalledProcessError as e:
        socketio.emit(
            "job_failed",
            {
                "job_id": job.id,
                "output_file": output_file,
            },
        )
        return False

    socketio.emit(
        "job_completed",
        {
            "job_id": job.id,
            "output_file": output_file,
        },
    )

    return True


@app.route("/run-script", methods=["POST"])
@auth.login_required
def run_script():
    queued_jobs = rq.get_queue().jobs  # Get all jobs in the default queue
    print("JOBS:", [job.id for job in queued_jobs])  # Print all job IDs
    
    data = request.json
    source_file_name = data["source"]
    targets = data["targets"]
    other_args = data["other_args"]  # String

    output_results = []
    source_file_path = os.path.join(SOURCE_DIR, source_file_name)

    jobsData = []
    

    for idx, target_file_name in enumerate(targets):
        
        target_file_path = os.path.join(TARGET_DIR, target_file_name)
        output_file_name = f"{int(time.time()) + idx}_{source_file_name.split('.')[0]}_{target_file_name}"
        output_file_path = f"{os.path.join(OUTPUT_DIR, output_file_name)}"

        # Construct the command
        command = f"python /usr/src/app/run.py --headless \
                  --source {source_file_path} --target {target_file_path} --output {output_file_path} \
                  --execution-providers cuda \
                  --execution-thread-count 2 \
                  {other_args} \
                  --output-image-quality 100 \
                  --output-video-quality 100 \
                  --output-video-encoder h264_nvenc \
                  --face-mask-types box occlusion"
        #command = f"cp {source_file_path} {output_file_path}"
        jobsData.append(
            Queue.prepare_data(
                "api.run_job",
                timeout=-1,
                kwargs=(
                    {
                        "command": command,
                        "output_file": {
                            "name": output_file_name,
                            "url": url_for('serve_file', dir="output", filename=output_file_name, _external=True),
                        },
                    }
                ),
            )
        )

    jobs = rq.get_queue().enqueue_many(jobsData)
    output_results = list(map(map_jobs, jobs))

    return jsonify(output_results)


if __name__ == "__main__":
    #socketio.run(app, allow_unsafe_werkzeug=True, port=5000)
    socketio.run(app, allow_unsafe_werkzeug=True, host="0.0.0.0", port=5000)
