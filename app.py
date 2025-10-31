# Copyright 2025 Copyright 2025 The CoHDI Authors.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os, json
import shutil
from flask import Flask

app = Flask(__name__)


def load_file(path):
    if not os.path.exists(path):
        return None, ('{"error":"not found"}', 404)
    data = json.load(open(path))
    body = json.dumps(data, ensure_ascii=False)
    return data, (body, 200)


def get_and_allocate_next_resource(incoming_dir, allocated_dir):
    available_files_names = [f for f in os.listdir(incoming_dir) if f.endswith(".json")]
    if not available_files_names:
        return {
            "error": "no_available_resources",
            "message": f"No resources in '{incoming_dir}' left to allocate.",
        }, 404

    file_to_allocate_name = available_files_names[0]
    source_file_path = os.path.join(incoming_dir, file_to_allocate_name)
    destination_file_path = os.path.join(allocated_dir, file_to_allocate_name)

    resource_data = json.load(open(source_file_path))
    resource_body = json.dumps(resource_data, ensure_ascii=False)

    shutil.move(source_file_path, destination_file_path)

    return resource_body, 200


@app.route(
    "/cluster_manager/cluster_autoscaler/v3/tenants/<t>/clusters/<c>/machines/<m>",
    methods=["GET"],
)
def get_node_detail(t, c, m):
    _, (body, st) = load_file(f"./in/machines/{m}/detail.json")
    return body, st, {"Content-Type": "application/json"}


@app.route(
    "/cluster_manager/cluster_autoscaler/v3/tenants/<t>/clusters/<c>/machines/<m>/actions/resize",
    methods=["POST"],
)
def resize_node_devices(t, c, m):
    _, (body, st) = (None, ('{"status":"success"}', 200))
    return body, st, {"Content-Type": "application/json"}


@app.route(
    "/cluster_manager/cluster_autoscaler/v2/tenants/<t>/clusters/<c>/nodegroups",
    methods=["GET"],
)
def get_nodegroup_list(t, c):
    _, (body, st) = load_file("./in/nodegroups/list.json")
    return body, st, {"Content-Type": "application/json"}


@app.route(
    "/cluster_manager/cluster_autoscaler/v2/tenants/<t>/clusters/<c>/nodegroups/<ng>",
    methods=["GET"],
)
def get_nodegroup_detail(t, c, ng):
    _, (body, st) = load_file(f"./in/nodegroups/{ng}/detail.json")
    return body, st, {"Content-Type": "application/json"}


@app.route("/fabric_manager/api/v1/machines", methods=["GET"])
def get_machine_list():
    _, (body, st) = load_file("./in/machines/list.json")
    return body, st, {"Content-Type": "application/json"}


@app.route("/fabric_manager/api/v1/machines/<m>", methods=["GET"])
def get_machine(m):
    _, (body, st) = load_file(f"./in/machines/{m}/fm_get_response.json")
    return body, st, {"Content-Type": "application/json"}


@app.route(
    "/fabric_manager/api/v1/machines/<m>/available-reserved-resources", methods=["GET"]
)
def get_available_machines(m):
    _, (body, st) = load_file(f"./in/machines/{m}/available.json")
    return body, st, {"Content-Type": "application/json"}


@app.route("/fabric_manager/api/v1/machines/<m>/update", methods=["PATCH"])
def patch_devices_fm(m):
    os.makedirs(f"./in/machines/{m}/fm_patch_response/allocated", exist_ok=True)

    body, st = get_and_allocate_next_resource(
        f"./in/machines/{m}/fm_patch_response",
        f"./in/machines/{m}/fm_patch_response/allocated",
    )
    return body, st, {"Content-Type": "application/json"}


@app.route("/fabric_manager/api/v1/machines/<m>/update", methods=["DELETE"])
def delete_devices_fm(m):
    _, (body, st) = (None, ('{"status":"success"}', 200))
    return body, st, {"Content-Type": "application/json"}

@app.route("/id_manager/realms/<realm>/protocol/openid-connect/token", methods=["POST"])
def get_token(realm):
    response = {
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOiAzMjUwMzY4MDAwMCwgInByZWZlcnJlZF91c2VybmFtZSI6ICJ0ZXN0In0K.dGVzdAo",
        "expires_in": 300,
        "refresh_expires_in": 2,
        "refresh_token": "token2",
        "token_type": "Bearer",
        "id_token": "token3",
        "not-before-policy": 3,
        "session_state": "efffca5t4",
        "scope": "test profile"
    }
    return json.dumps(response, ensure_ascii=False), 200, {"Content-Type": "application/json"}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=443, ssl_context=('certs/server.crt', 'certs/server.key'))
