from flask import Blueprint, request
from app.classes.log_entry.log_entry import LogEntry
from app.database.mongo_db import MongoDb

general_bp = Blueprint('general', __name__)
mongodb = MongoDb()

@general_bp.route('/logs', methods=['POST'])
def logs():
    """
    DEFINITION DE LA REQUETE
    """
    return {"status": "success", "message": "Log received"}, 200


@general_bp.route('/formattedMessage', methods=['POST'])
def formatMessage():
    body = request.get_json()
    formatted = LogEntry.formatted_message(body, mongodb)
    return {"status": "success", "message": formatted}, 200
    

# @general_bp.route('/filterLogsArray', methods=['POST'])
# def formatMessage():
#     body = request.get_json()
#     formatted = LogsManager.filter_by(body)
#     return {"status": "success", "message": formatted}, 200