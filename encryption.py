from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
from Crypto.Random import get_random_bytes
import sqlite3


class Interface:
    def __init__(self):
        self.calc_man = AESdata()
        self.text1 = 'Please input number:'
        self.text2 = '1. En/Decrypt Center\n2. Database Center'
        self.text3 = '1. Encrypt\n2. Decrypt'
        self.text4 = '1. Create a new DB\n2. Select current DB'
        self.text5 = '1. Insert\n2. update\n3. read\n4. delete\n5. move'
        print('--------------------------------')
        print('|           Database            |')
        print('|      Infomation Center        |')
        print('--------------------------------')

    def select(self, show_info):
        print(show_info)
        num = input(self.text1)
        return int(num)

    def run(self):
        num1 = self.select(self.text2)
        if num1 == 1:
            num2 = self.select(self.text3)
            if num2 == 1:
                path = input('File path: ')
                self.calc_man.encrypt_data(path)
            elif num2 == 2:
                path = input('File path: ')
                self.calc_man.decrypt_data(path)
        elif num1 == 2:
            num3 = self.select(self.text4)
            if num3 == 1:
                db_man = MyDB(input('Please input file name: ')).cDB()
            elif num3 == 2:
                db_man = MyDB(input('Please input file name: '))
                num4 = self.select(self.text5)
                if num4 == 1:
                    db_man.wDB()
                elif num4 == 2:
                    db_man.uDB()
                elif num4 == 3:
                    db_man.rDB()
                elif num4 == 4:
                    db_man.dDB()
                elif num4 == 5:
                    db_man.mDB()


class AESdata:
    def __init__(self):
        # 密钥key 长度必须为16（AES-128）、24（AES-192）或 32（AES-256）字节
        self.key = b'1234567890ABCDEF'

    def encrypt_data(self, path):
        # 实例化加密套件，使用CBC模式
        encrypt_cipher = AES.new(self.key, AES.MODE_CBC)
        with open(path, 'rb') as f:
            data = f.read()
            # 对内容进行加密，pad函数用于分组和填充
            encrypted_data = encrypt_cipher.encrypt(pad(data, AES.block_size))
            new_path = F"{path}.bin"
            with open(new_path, 'wb') as h:
                # 在文件中依次写入iv和密文encrypted_data
                [h.write(content) for content in (encrypt_cipher.iv, encrypted_data)]
        print('Encrypted.')

    def decrypt_data(self, path):
        with open(path, 'rb') as f:
            # 依次读取iv和密文encrypted_data，最后的-1则表示读取到文件末尾
            iv, encrypted_data = [f.read(content) for content in (AES.block_size, -1)]
            # 实例化加密套件
            decrypt_cipher = AES.new(self.key, AES.MODE_CBC, iv)
            # 解密
            try:
                decrypted_data = unpad(decrypt_cipher.decrypt(encrypted_data), AES.block_size)
                new_path = F"{path.replace('.bin', '')}"
                with open(new_path, 'wb') as h:
                    h.write(decrypted_data)
                print('Decrypted.')
            except ValueError as reason:
                print(reason)


class MyDB:
    def __init__(self, name):
        self.name = name

    def cDB(self):
        # create a database
        table_num = int(input('How many table would you want: '))
        count_1 = 1
        while count_1 <= table_num:
            table= input(F"Please input table_{count_1}'s name: ")
            columns = []
            columns_num = int(input('How many columns would you want: '))
            count_2 = 1
            while count_2 <= columns_num:
                text = F"Please complete column_{count_2} [format: name type (primary key)]:\n==>"
                columns.append(input(text))
                count_2 += 1
            conn = sqlite3.connect(self.name)
            man = conn.cursor()
            columns_new = ""
            for each in columns:
                columns_new += F"{each}, "
            add_time = "date timestamp not null default(datetime('now', 'localtime'))"
            command = F"CREATE TABLE {table}({columns_new}{add_time})"
            try:
                man.execute(command)
                conn.commit()
                print(F'TABLE {table} created.')
            except sqlite3.OperationalError as reason:
                print(reason)
            conn.close()
            count_1 += 1
        print(F'{self.name} created.')

    def wDB(self):
        # write values into database
        self.rDB(0)
        table = input("Which table would you want to write: ")
        self.rDB(1, table)
        content = input('Please input values [format: col_1 val_1, col_2 val_2, ...]:\n==>')
        col_val = content.split(', ')
        columns = ''
        values = ''
        conn = sqlite3.connect(self.name)
        man = conn.cursor()
        for each in col_val:
            columns += F"{each.split(' ')[0]}, "
            values += F"{each.split(' ')[1]}, "
        columns = columns[:-2]
        values = values[:-2]
        command = F"INSERT INTO {table}({columns}) VALUES({values})"
        try:
            man.execute(command)
            conn.commit()
            print('Data Inserted.')
        except sqlite3.IntegrityError as reason:
            print(reason)
        conn.close()

    def uDB(self):
        # update data in database with primary key
        conn = sqlite3.connect(self.name)
        man = conn.cursor()
        self.rDB(0)
        table = input("Which table would you want to update: ")
        self.rDB(1, table)
        content = input("Please input values [format: key='val'|col_1='val_1', col_2='val_2', ...]:\n==>")
        key = content.split('|')[0]
        values = content.split('|')[1]
        command = F"UPDATE {table} set {values} where {key}"
        try:
            man.execute(command)
            conn.commit()
            print('Data Updated.')
        except sqlite3.OperationalError as reason:
            print(reason)
        conn.close()

    def rDB(self, num=0, table=''):
        # read data from database
        conn = sqlite3.connect(self.name)
        man = conn.cursor()
        if num == 0:
            # show all tables
            command = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        elif num == 1:
            # show a table's volumns
            command = F"pragma table_info({table})"
        elif num == -1:
            self.rDB(0)
            table = input("Which table would you want to show: ")
            command = F"SELECT * FROM {table}"
        try:
            for each in man.execute(command):
                print(F'{each}')
        except sqlite3.OperationalError as reason:
            print(reason)
        conn.close()

    def dDB(self, table='example'):
        # delete a database
        conn = sqlite3.connect(self.name)
        man = conn.cursor()
        command = F"DROP TABLE '{table}'"
        try:
            man.execute(command)
            conn.commit()
            print('Delete successfully')
        except sqlite3.OperationalError as reason:
            print(reason)
        conn.close()

    def mDB(self):
        # move data from one to another
        pass


if __name__ == '__main__':
    iron_man = Interface()
    iron_man.run()

    
