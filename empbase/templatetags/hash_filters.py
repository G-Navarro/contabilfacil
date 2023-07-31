from django import template
import hashlib

register = template.Library()

@register.filter
def hash_id(id):
    # Convert the ID to a string
    id_string = str(id)
    # Create a hashlib object using the SHA256 algorithm
    hash_object = hashlib.sha256(id_string.encode())
    # Get the hexadecimal representation of the hash
    hash_value = hash_object.hexdigest()
    # Return the hash value
    return hash_value