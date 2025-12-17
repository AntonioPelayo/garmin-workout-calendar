def create_activity_hash(start_utc, elapsed_time, sport, distance):
    from hashlib import sha1
    return sha1(f"{start_utc}|{elapsed_time}|{sport}|{distance}".encode("utf-8")).hexdigest()


def get_event_hash(event) -> str:
    description = event.get("description", "")
    if "Activity hash: " in description:
        return description.split("Activity hash: ")[-1]
    return ""


def hash_match(hash1: str, hash2: str) -> bool:
    return hash1 == hash2
