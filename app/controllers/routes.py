from flask import Blueprint, request
from app.classes.log_entry.log_entry import LogEntry
from app.database.data_store import data_store

general_bp = Blueprint('general', __name__)

@general_bp.route('/logs', methods=['POST'])
def logs():
    """
    DEFINITION DE LA REQUETE
    """
    return {"status": "success", "message": "Log received"}, 200


@general_bp.route('/formattedMessage', methods=['POST'])
def formatMessage():
    body = request.get_json()
    formatted = LogEntry.formatted_message(body, data_store)
    return {"status": "success", "message": formatted}, 200


@general_bp.route('/supported-codes', methods=['GET'])
def supported_codes():
    return {"codes": data_store.supported_codes}, 200
    

# @general_bp.route('/filterLogsArray', methods=['POST'])
# def formatMessage():
#     body = request.get_json()
#     formatted = LogsManager.filter_by(body)
#     return {"status": "success", "message": formatted}, 200
