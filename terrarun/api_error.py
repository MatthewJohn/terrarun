

class ApiError:

    def __init__(self, title, details, pointer=None, status=None):
        """Store member variables"""
        self._title = title
        self._details = details
        self._pointer = pointer
        self._status = status if status else 422

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
