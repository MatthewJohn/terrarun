

class ApiError:

    def __init__(self, title, details, pointer):
        """Store member variables"""
        self._title = title
        self._details = details
        self._pointer = pointer

    def get_api_details(self):
        """Return API details for error"""
        return {
            "status": "422",
            "title": self._title,
            "detail": self._details,
            "source": {
                "pointer": self._pointer
            }
        }
