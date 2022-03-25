from flask import jsonify


class CustomError(Exception):
    def __init__(self, error_message="", status_code=400, suggested_action=None):
        self.error_message = error_message
        self.status_code = status_code
        self.suggested_action = suggested_action

    def to_jsonified(self):
        return jsonify(self.__dict__)


def data_not_found():
    """ No files to parse """
    return CustomError(error_message="No files to parse",
                       suggested_action="Download files form gdrive",
                       status_code=400)


def db_data_not_found():
    """ No data in DB when requesting /get_data """
    return CustomError(error_message="DB is empty",
                       suggested_action="insert data in DB",
                       status_code=400)
