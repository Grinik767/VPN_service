import paramiko
from dotenv import load_dotenv
import os


class Bash:
    def __init__(self, host, user, password):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname=host, username=user, password=password)

    def exec_command(self, *commands):
        try:
            stdin, stdout, stderr = self.client.exec_command(f'{commands[0]}\n')
            if len(commands) > 1:
                for command in commands[1:]:
                    stdin.write(f'{command}\n')
            return True, (stdout.read() + stderr.read()).strip().decode('utf-8')
        except Exception as err:
            return False, err

    def download_file(self, directory, filename):
        try:
            sftp_client = self.client.open_sftp()
            sftp_client.chdir(directory)
            sftp_client.get(filename, filename)
            sftp_client.close()
        except Exception as err:
            return False, err

    def upload_file(self, directory, filename):
        try:
            sftp_client = self.client.open_sftp()
            sftp_client.chdir(directory)
            f = open(filename)
            sftp_client.putfo(f, filename)
            sftp_client.close()
        except Exception as err:
            return False, err

    def close_connection(self):
        self.client.close()


if __name__ == '__main__':
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    bash = Bash(host=os.environ['HOST'], user=os.environ['USER'], password=os.environ['PASSWORD'])
    bash.upload_file('/etc/pivpn/wireguard', 'TV.conf')