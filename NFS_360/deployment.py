import os 
from .settings import *
from .settings import BASE_DIR


# SECRET_KEY = os.environ['SECRET']
# ALLOWED_HOSTS = [os.environ['Hostname_Neucode']]
# CSRF_TRUSTED_ORIGINS = ['https://' + os.environ['Hostname_Neucode']]
# DEBUG = False

SECRET_KEY = os.environ.get('SECRET', 'qy6%-%f%kd6p+9g7c=u)j3v+zs3h0h*u(mhx+(vss=tnx)!s)c')  # Provide a default for safety
ALLOWED_HOSTS = [os.environ.get('Hostname_Neucode', 'ncstage-heebdjh6bmfweahn.eastus2-01.azurewebsites.net')]
CSRF_TRUSTED_ORIGINS = ['https://' + os.environ.get('Hostname_Neucode', 'ncstage-heebdjh6bmfweahn.eastus2-01.azurewebsites.net')]

# WhiteNoise configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
] 

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = 'static/'
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'App_Admin/static'),  # Ensure this matches your project structure
# ]

# Database configuration using environment variables
DATABASES = {
    'default': {
        'ENGINE': 'mssql',  # Adjust as needed for your backend
        'NAME': os.environ.get('DATABASE_NAME', 'neucode-sql-dev'),
        'USER': os.environ.get('DATABASE_USER', 'neucodeadmin'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', 'AASU@123'),
        'HOST': os.environ.get('DATABASE_HOST', 'neucode-server-dev.database.windows.net'),
        'PORT': os.environ.get('DATABASE_PORT', '1433'),  # Default MSSQL port
        'OPTIONS': {
            'driver': 'ODBC Driver 18 for SQL Server',
            'Encrypt': 'yes',
            'TrustServerCertificate': 'yes',
        },
    }
}

# Email Configuration using environment variables
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.office365.com')  # Replace with a default if needed
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))  # Default to port 587
EMAIL_USE_TLS = True
# EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'anantsol@neucodetalent.com')
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'AgtQb@24')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'mylearning@neucodetalent.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'JulNeu$25')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# # Parse the Azure MSSQL connection string from environment variables
# conn_str = os.environ['AZURE_MSSQL_CONNECTIONSTRING']
# conn_str_params = {pair.split('=')[0]: pair.split('=')[1] for pair in conn_str.split(';') if '=' in pair}

# DATABASES = {
#     'default': {
#         'ENGINE': 'mssql',  # Django MSSQL backend
#         'NAME': conn_str_params['Database'],  # Use 'Database' instead of 'dbname' for MSSQL
#         'HOST': conn_str_params['Server'],    # Use 'Server' instead of 'host' for MSSQL
#         'USER': conn_str_params['User Id'],   # Use 'User Id' instead of 'user'
#         'PASSWORD': conn_str_params['Password'],  # Use 'Password' instead of 'password'
#         'OPTIONS': {
#             'driver': 'ODBC Driver 18 for SQL Server',  # Use the appropriate ODBC driver
#             'Encrypt': 'yes',  # Ensure encryption for Azure MSSQL
#             'TrustServerCertificate': 'yes',  # Trust server certificate if needed
#         },
#     }
# }


# from decouple import config

# DATABASES = {
#     'default': {
#         'ENGINE': 'mssql',
#         'NAME': config('DATABASE_NAME'),
#         'USER': config('DATABASE_USER'),
#         'PASSWORD': config('DATABASE_PASSWORD'),
#         'HOST': config('DATABASE_HOST'),
#         'PORT': config('DATABASE_PORT'),
#         'OPTIONS': {
#             'driver': 'ODBC Driver 18 for SQL Server',
#             'Encrypt': 'yes',  # Use encryption for Azure MSSQL
#             'TrustServerCertificate': 'yes',  # Trust server certificate if needed
#         },
#     }
# }

# # Email Configuration
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = config('EMAIL_HOST')
# EMAIL_PORT = config('EMAIL_PORT', cast=int)
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = config('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
# DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
