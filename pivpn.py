import os
import yadisk
from dotenv import load_dotenv
from openpyxl import load_workbook
from bash import Bash
from txt_to_img import textfile_to_image


class Pivpn:
    def __init__(self, bash, disk):
        self.bash = bash
        self.disk = disk

    def get_list_users(self, numbers=False):
        data = self.bash.exec_command('pivpn -l')
        if data[0]:
            data = data[1]
        data = [line.split()[0] for line in data.split('\n')[2:-1]]
        if numbers:
            data = [f'{line[0] + 1}. {line[1]}' for line in list(enumerate(data))]
        return data

    def add_new_user(self, name, date_s, date_f, cost, count, count_max=0, platform='Авито', phone='', qr=True):
        try:
            self.disk.download(src_path='/VPN/Clients.xlsx', path_or_file='Clients.xlsx')
            wb = load_workbook('Clients.xlsx')
            ws = wb.active
            new = len(ws['A']) + 1
            nickname = f"Client{new}"
            if count_max == 0:
                count_max = count
            ws.append([name, nickname, platform, phone, date_s, date_f, cost, count, count_max])
            wb.save('Clients.xlsx')
            self.disk.upload(path_or_file='Clients.xlsx', dst_path='/VPN/Clients.xlsx', overwrite=True)
            os.remove('Clients.xlsx')
            num = len(self.get_list_users())
            for i in range(1, count + 1):
                self.bash.exec_command('pivpn add', f"{nickname}_{i}")
                num += 1
                if qr:
                    data = self.bash.exec_command('pivpn -qr', f"{num}")
                    data = '\n'.join(
                        [line.split('1m')[1:][0].strip('\x1b[0m') for line in data[1].split('\n')[num + 3:-1]])
                    with open(f"{nickname}_{i}.txt", mode='wb') as f:
                        f.write(data.encode('utf-8'))
                    textfile_to_image(f"{nickname}_{i}.txt").save(f"{nickname}_{i}.jpg")
                    os.remove(f"{nickname}_{i}.txt")
                else:
                    pass
        except Exception as err:
            return False, err

    def delete_user(self):
        pass


if __name__ == '__main__':
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    bash = Bash(host=os.environ['HOST'], user=os.environ['USER'], password=os.environ['PASSWORD'])
    disk = yadisk.YaDisk(id=os.environ['DISK_ID'], secret=os.environ['DISK_SECRET'], token=os.environ['DISK_TOKEN'])
    vpn = Pivpn(bash, disk)
    vpn.add_new_user('Григорий', '30.07.2022', '1', '1', 1)
