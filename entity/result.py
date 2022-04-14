class AppConfigResult:

    def __init__(self, version, application_id, profile_name, profile_id, state, error_message, key):
        self.version = version
        self.application_id = application_id
        self.profile_name = profile_name
        self.profile_id = profile_id
        # 'COMPLETE'|'ROLLED_BACK' 'VERIFY_ERROR' 'ERROR'
        self.state = state
        self.error_message = error_message
        self.key = key

    def convert2json(self):
        return {
            'version': self.version,
            'application_id': self.application_id,
            'profile_name': self.profile_name,
            'profile_id': self.profile_id,
            'state': self.state,
            'error_message': self.error_message,
            'key': self.key
        }

    def __str__(self) -> str:
        return {'key': self.key, 'state': self.state, 'error_message': self.error_message,
                'profile_id': self.profile_id, 'profile_name': self.profile_name,
                'application_id': self.application_id, 'version': self.version}.__str__()
