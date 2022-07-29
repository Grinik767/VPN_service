import paramiko


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

    def reload_file(self, directory, filename, filename_to):
        try:
            sftp_client = self.client.open_sftp()
            sftp_client.chdir(directory)
            f = open(filename)
            sftp_client.putfo(f, filename_to)
            f.close()
            sftp_client.close()
        except Exception as err:
            return False, err

    def close_connection(self):
        self.client.close()
