import json
import os

from agent import destination
from flask import Blueprint, request
from agent.api.forms.destination import DestinationForm, EditDestinationForm
from agent.modules import constants

destination_ = Blueprint('destination', __name__)


@destination_.route('/destination', methods=['GET'])
def get():
    if not destination.repository.exists():
        return 'Destination doesn\'t exist', 404
    return destination.repository.get().to_dict(), 200


@destination_.route('/destination', methods=['POST'])
def create():
    if destination.repository.exists():
        return 'Destination already exists', 400
    form = DestinationForm.from_json(request.get_json())
    if not form.validate():
        return form.errors, 400
    result = destination.manager.create(
        form.data_collection_token.data,
        form.destination_url.data,
        form.access_key.data,
        form.proxy_uri.data,
        form.proxy_username.data,
        form.proxy_password.data,
        form.host_id.data,
    )
    if result.is_err():
        return result.value, 400
    return result.value.to_dict(), 200


@destination_.route('/destination', methods=['PUT'])
def edit():
    if not destination.repository.exists():
        return 'Destination doesn\'t exist', 400
    form = EditDestinationForm.from_json(request.get_json())
    if not form.validate():
        return form.errors, 400
    result = destination.manager.edit(
        destination.repository.get(),
        form.data_collection_token.data,
        form.destination_url.data,
        form.access_key.data,
        form.proxy_uri.data,
        form.proxy_username.data,
        form.proxy_password,
        form.host_id.data,
    )
    if result.is_err():
        return result.value, 400
    return result.value.to_dict(), 200


@destination_.route('/destination', methods=['DELETE'])
def delete():
    if destination.repository.exists():
        destination.manager.delete()
    return '', 200


@destination_.route('/destination/local_fs/<file_name>', methods=['POST'])
def local_fs(file_name: str):
    if request.content_type == 'application/json':
        _write_json(file_name)
    elif request.content_type == 'application/octet-stream':
        _write_csv(file_name)
    return ''


def _write_csv(file_name: str):
    file_path = os.path.join(constants.LOCAL_DESTINATION_OUTPUT_DIR, f'{file_name}.csv')
    skip_header = os.path.isfile(file_path)
    if request.data and len(request.data) > 0:
        if not os.path.isdir(constants.LOCAL_DESTINATION_OUTPUT_DIR):
            os.mkdir(constants.LOCAL_DESTINATION_OUTPUT_DIR)
        with open(file_path, 'a') as f:
            for line in request.data.splitlines():
                if skip_header:
                    skip_header = False
                    continue
                f.write(line.decode())
                f.write("\n")


def _write_json(file_name: str):
    data = request.get_json()
    if data and len(data) > 0:
        if not os.path.isdir(constants.LOCAL_DESTINATION_OUTPUT_DIR):
            os.mkdir(constants.LOCAL_DESTINATION_OUTPUT_DIR)
        with open(os.path.join(constants.LOCAL_DESTINATION_OUTPUT_DIR, f'{file_name}.json'), 'a') as f:
            for obj in data:
                json.dump(obj, f)
                f.write(",\n")
