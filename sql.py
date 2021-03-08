import sqlite3
import hashlib
from datetime import datetime
def log_wrapper(func):
    def inner(self):
        now = datetime.now().strftime("%y/%m/%d %H:%M")
        func(self)
        with open("./log.txt", "a") as log:
            log.write(f"This person id={self._id} has made smth in DB {func.__name__} at {now} \r \n")
    return inner
#access lvl 1
class AL_1:
    def __init__(self, cursor, id, access):
        self._id = id
        self._cursor = cursor
        self._access = access

    def show_worker_by_id(self):
        try:
            id_worker = int(input("Input id worker which u want to see"))
        except ValueError:
            print("ID must be a number!")
            id_worker = int(input("Input id worker which u want to see"))
        self._cursor.execute("""
        SELECT name, surname, age, posiition, boss_id FROM workers WHERE id=?
        """, (id_worker,))
        print(self._cursor.fetchone())

    def show_boss_workers_by_id(self):
        try:
            boss_id = int(input("Input bosses id for searching"))
        except ValueError:
            print("ID must be a number!")
            boss_id = int(input("Input bosses id for searching"))
        self._cursor.execute("""
            SELECT name, surname, age, posiition FROM workers WHERE boss_id=?
        """, (boss_id,))
        res = self._cursor.fetchall()
        for i in res:
            print(i)

#access lvl 2
class AL_2(AL_1):
    @log_wrapper
    def change_pass_by_id(self):
         try:
            change_id = int(input("Input id to change pass"))
         except ValueError:
            print("id must be int!")
         self._cursor.execute("""
            SELECT access FROM workers WHERE id=?
         """, (change_id,))
         access_lvl = self._cursor.fetchone()
         if access_lvl > self._access:
             print("Sorry, we haven't got needful access to do this action")
         else:
             print("Success pls input new password")
             HASH = hashlib.md5(input().encode()).hexdigest()
             self._cursor.execute("""
                UPDATE workers SET hash=? WHERE id=?
             """, (HASH, change_id))
    @log_wrapper
    def add_user(self):
        try:
            id_user = int(input("Input ID of the new worker "))
        except ValueError:
            print("id must be int")
            id_user = int(input("Input ID of the new worker "))
        name_user = input("Input name  ")
        surname_user = input("Input surname ")
        age_user = input("Input age ")
        position = input("Input position ")
        try:
            access = int(input("Input lvl of access "))
        except ValueError:
            print("access lvl must be int and 0<=access lvl<4")
            access = int(input("Input lvl of access "))
        if access > self._access:
            access = self._access - 1
        try:
            boss_id = int(input("Input boss id "))
        except ValueError:
            print("Id must be int")
        if access > 0:
            HASH = hashlib.md5(input("Input ur password ").encode()).hexdigest()
        else :
            HASH = "NULL"
        self._cursor.execute("""
            INSERT INTO workers VALUES(?,?,?,?,?,?,?,?)
        """, (id_user, name_user, surname_user, age_user, position, access, boss_id, HASH))

#access lvl 3(BOSS)
class AL_3(AL_2):
    def show_all_workers(self):
        self._cursor.execute("""
        SELECT id, name, surname, age, posiition, access, boss_id FROM workers WHERE boss_id > 0 
        """)
        table = self._cursor.fetchall()
        for worker in table :
            print(worker)
    
    @log_wrapper
    def access_lvl_up(self):
         try:
            id_user = int(input("Input user id which u want to change lvl access "))
         except ValueError:
             print("ID must be a number")
             id_user = int(input("Input user id which u want to change lvl access "))
         new_access = int(input("Input new access lvl "))
         self._cursor.execute("""
            UPDATE workers SET access=? WHERE id=?
        """, (new_access, id_user))

    @log_wrapper
    def delete_worker(self):
        id_user = int(input("Input worker id who u will delete "))
        confirmation = input(" Are u sure? [Y,n] ")
        if confirmation == "Y" or confirmation == "y":
            self._cursor.execute("""
            DELETE FROM workers WHERE id=?
            """,(id_user,))
        else:
            print("Maybe in the next time...")

if __name__ == "__main__":
    QUIT = False
    connect = sqlite3.connect("workers.db", timeout=10)
    cursor = connect.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workers(
            id integer unique, name text, surname text, age integer, posiition text, access lvl integer, boss_id integer, hash text
        )
    """)
    try:
        id = int(input("Hi. Input ur id "))
    except ValueError:
        print("ID must be int!")
        connect.close()
        exit(0)
    password = hashlib.md5(input("Input ur password ").encode()).hexdigest()
    try:
        cursor.execute("""
            SELECT hash, access FROM workers WHERE id=?
        """,(id,))
        answer = cursor.fetchone()
    except TypeError:
        print("Whoops... Smth went wrong!")
    if password != answer[0]:
        print("Whoops... Smth went wrong!")
        connect.close()
        exit(0)

    if answer[1] == 1:
        worker = AL_1(cursor, id, 1)
        print("""
            Hi. U can search another worker by id (input 1)
            U also can look at all workers in ur bosses by id(input 2)
            And u can go out(exit)(input 3)
            Sorry, but this is all. Have a nice day.
            """)
        while not QUIT:
            action = int(input("What do u want?"))
            if action == 1:
                worker.show_worker_by_id()
            elif action == 2:
                worker.show_boss_workers_by_id()
            elif action == 3:
                QUIT = True
        connect.close()
        exit(0)
    
    elif answer[1] == 2:
        worker = AL_2(cursor, id, 2)
        print("""
            Hi. U can search anouther worker by id (input 1)
            U also can look at all workers in ur bosses by id(input 2)
            Next u can change password for anouther worker (input 3)
            And add new worker (input 4)
            And u can go out(exit)(input 5)
            Sorry, but this is all. Have a nice day.
            """)
        while not QUIT:
            action = int(input("What do u want?"))
            if action == 1:
                worker.show_worker_by_id()
            elif action == 2:
                worker.show_boss_workers_by_id()
            elif action == 3:
                worker.change_pass_by_id()
                connect.commit()
            elif action == 4:
                worker.add_user()
                connect.commit()
            elif action == 5:
                QUIT = True
        connect.close()
        exit(0)

    elif answer[1] == 3:
        worker = AL_3(cursor, id, 3)
        print("""
            Welcome our sir. U can search slave by id (input 1)
            U also can look at all slaves in ur older slaves by id(input 2)
            Next u can change password for anouther slave (input 3)
            And add after buying new slave (input 4)
            U can watch at list of ur slaves(input 5)
            U can make from simple slave to older(input 6)
            U can expel bad slave(delete)(input 7)
            If u want to go, we will expect(input 8)
            Sorry, but this is all. Have a nice day.
            """)
        while not QUIT:
            action = int(input("What do u want?"))
            if action == 1:
                worker.show_worker_by_id()
            elif action == 2:
                worker.show_boss_workers_by_id()
            elif action == 3:
                worker.change_pass_by_id()
                connect.commit()
            elif action == 4:
                worker.add_user()
                connect.commit()
            elif action == 5:
                worker.show_all_workers()
            elif action == 6:
                worker.access_lvl_up()
                connect.commit()
            elif action == 7:
                worker.delete_worker()
                connect.commit()
            elif action == 8:
                QUIT = True
        connect.close()
        exit(0)

    else:
        print("Excuse me, but u can't check this database, because u haven't access.")
        connect.close()
        exit(0)

