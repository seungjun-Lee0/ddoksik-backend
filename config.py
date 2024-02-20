import os

APP_ENV = os.getenv('APP_ENV', 'development')
DATABASE_USERNAME = os.getenv('DATABASE_USERNAME', 'postgres')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'avocado1')
DATABASE_HOST = os.getenv('DATABASE_HOST', 'ddoksik1.cricim2es6bi.ap-northeast-2.rds.amazonaws.com')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'ddoksik')
TEST_DATABASE_NAME = os.getenv('DATABASE_NAME', 'test_health-care')