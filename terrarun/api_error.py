
from terrarun.errors import TerrarunError


class ApiError(TerrarunError):

    def __init__(self, title, details, pointer=None, status=None):
        """Store member variables"""
        self._title = title
        self._details = details
        self._pointer = pointer
        self._status = status if status else 422

        super(ApiError, self).__init__(details)

    def get_api_details(self):
        """Return API details for error"""
        return {
            "status": str(self._status),
            "title": self._title,
            "detail": self._details,
            "source": {
                "pointer": self._pointer
            } if self._pointer else {}
        }


def api_error_response(api_error):
    return api_error.get_api_details(), api_error._status
