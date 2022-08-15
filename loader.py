import os
import time
from bash import Bash
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
bash = Bash(host=os.environ['HOST'], user=os.environ['USER'], password=os.environ['PASSWORD'])
bash.exec_command('systemctl stop tgbot')
time.sleep(3)
bash.exec_command('systemctl start tgbot')
time.sleep(3)
bash.exec_command('systemctl enable tgbot')
