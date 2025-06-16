from flask import Blueprint, request
from app.database.downlinks import downlinks # type: ignore

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
    return {"status": "success", "message": formatted_message(body)}, 200
    
def formatted_message(request_data: dict) -> str:
    message_ref = request_data.get("messageRef")
    arguments = request_data.get("arguments", [])

    d_message = next(
        (msg for msg in downlinks if msg.get("Ref_Num", "").replace(" ", "") == message_ref),
        None
    )

    if not d_message:
        return ""

    result = d_message.get("Message_Element", "")
    arg_index = 0

    import re
    def replacer(match):
        nonlocal arg_index
        if arg_index < len(arguments):
            value = arguments[arg_index]
            arg_index += 1
            return value
        return "[missing]"

    formatted = re.sub(r"\[.*?\]", replacer, result)

    return formatted.strip()    