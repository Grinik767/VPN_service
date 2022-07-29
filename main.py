import paramiko
import os
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

host, user, password = os.environ['HOST'], os.environ['USER'], os.environ['PASSWORD']

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname=host, username=user, password=password, port=22)
stdin, stdout, stderr = client.exec_command('pwd\n')
data = stdout.read() + stderr.read()
print(data.strip().decode('utf-8'))
client.close()