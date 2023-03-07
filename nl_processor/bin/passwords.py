import splunklib

passwords_realm = "nl_processor"


def _get_password_key(field_name):
    return (
        splunklib.binding.UrlEncoded(passwords_realm, encode_slash=True)
        + ":"
        + splunklib.binding.UrlEncoded(field_name, encode_slash=True)
    )


def decode_password(service, field_name):
    key = _get_password_key(field_name)
    if key in service.storage_passwords:
        storage_password = service.storage_passwords[key]
        return storage_password.clear_password
    return None


def encode_password(service, field_name, password):
    key = _get_password_key(field_name)
    if key in service.storage_passwords:
        storage_password = service.storage_passwords[key]
        if storage_password.clear_password != password:
            # password exists and it got changed, update it
            service.storage_passwords.delete(field_name, passwords_realm)
            storage_password = service.storage_passwords.create(
                password, field_name, passwords_realm
            )
    else:
        service.storage_passwords.create(password, field_name, passwords_realm)
