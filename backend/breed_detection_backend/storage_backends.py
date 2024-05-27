from storages.backends.azure_storage import AzureStorage

class UploadsStorage(AzureStorage):
    location = 'uploads'
    default_acl = 'public-read'
    file_overwrite = False
    