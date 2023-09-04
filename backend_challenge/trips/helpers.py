from django.utils.crypto import get_random_string
from sequences import Sequence

from .models import Trip


class TripGenerationService:
    """Trip Generation Service

    Generate a unique code for the Trip.
    """

    @staticmethod
    def generate_trip_code(*, instance: Trip) -> str:
        """Generate a unique code for the Trip

        Args:
            instance (Trip): The Trip instance.

        Returns:
            str: Trip code
        """
        trip_ids = Sequence("trips")
        seq = trip_ids.get_next_value()
        code = f"TRI-{seq + 1:06d}"
        return code


def generate_order_code():
    """Generate a unique tracking  number, should be population
     from organization short form and  random string

    Returns:
        str: The generated reference number.
    """
    # Exclude o,0,1,i,l to avoid confusion with bad fonts/printers
    allowed_chars = "abcdefghjkmnpqrstuvwxyz23456789"
    code = get_random_string(length=9, allowed_chars=allowed_chars)

    return code.upper()
