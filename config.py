import os

class Config:
    SECRET_KEY = "your_secret_key"

    # Azure SQL Database Connection
    SQLALCHEMY_DATABASE_URI = "mssql+pyodbc://your_azure_sql_connection_string"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Azure Notification Hub details
    AZURE_NOTIFICATION_HUB = "todo-hub"
    AZURE_CONNECTION_STRING = "your_notification_hub_connection_string"
