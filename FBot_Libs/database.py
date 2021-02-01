from datetime import datetime
import sqlite3

path = f"./Info/FBot.db"
conn = sqlite3.connect(path)

class db:

    def __init__(self):
        
        self.conn = conn # For sharing with other cogs/files
        c = conn.cursor()
        
        c.execute("""CREATE TABLE IF NOT EXISTS guilds (
                          guild_id integer NOT NULL,
                          modtoggle string NOT NULL,
                          prefix string NOT NULL,
                          priority string NOT NULL,
                          multiplier integer NOT NULL
                          )""")

        c.execute("""CREATE TABLE IF NOT EXISTS channels (
                          guild_id integer NOT NULL,
                          channel_id integer NOT NULL,
                          status string NOT NULL
                          )""")

        c.execute("""CREATE TABLE IF NOT EXISTS users (
                          user_id integer NOT NULL,
                          ppsize integer NOT NULL,
                          multiplier integer NOT NULL,
                          fbux integer NOT NULL,
                          debt integer NOT NULL,
                          netfbux integer NOT NULL,
                          netdebt integer NOT NULL,
                          job string NOT NULL,
                          jobs string NOT NULL,
                          degree string NOT NULL,
                          lastwork integer NOT NULL,
                          laststudy integer NOT NULL,
                          degreeprogress integer NOT NULL
                          )""")

        c.execute("""CREATE TABLE IF NOT EXISTS counter (
                          guild_id integer NOT NULL,
                          channel_id integer NOT NULL,
                          number integer NOT NULL,
                          user_id integer NOT NULL,
                          record integer NOT NULL
                          )""")
        
        conn.commit()
        print(" > Connected to FBot.db")

    def Check_Guilds(self, guilds):
        c = conn.cursor()
        discord_guild_ids = [guild.id for guild in guilds]

        for guild_id in discord_guild_ids:
            t = (guild_id,)
            try:
                c.execute(f"SELECT * FROM guilds where guild_id=?", t)
                c.fetchone()[0]
            except:
                self.Add_Guild(guild_id)

        count = 0
        c.execute(f"SELECT guild_id FROM guilds")
        for guild_id in c.fetchall():
            if not (guild_id[0] in discord_guild_ids):
                count += 1
                c.execute("DELETE FROM guilds WHERE guild_id=?", guild_id)
        print("Deleted", count, "guilds from 'guilds'")

        count = 0
        c.execute(f"SELECT guild_id FROM channels")
        for guild_id in c.fetchall():
            if not (guild_id[0] in discord_guild_ids):
                count += 1
                c.execute("DELETE FROM channels WHERE guild_id=?", guild_id)
        print("Deleted", count, "guild channels from 'channels'")

        count = 0
        c.execute(f"SELECT guild_id FROM counter")
        for guild_id in c.fetchall():
            if not (guild_id[0] in discord_guild_ids):
                count += 1
                c.execute("DELETE FROM counter WHERE guild_id=?", guild_id)
        print("Deleted", count, "guilds from 'counter'\n")
                
        conn.commit()

    # General

    def Add_Guild(self, guild_id):
        c = conn.cursor()
        t = (guild_id,)
        c.execute("INSERT INTO guilds VALUES(?, 'off', 'fbot', 'all', 1000000);", t)
        c.execute("INSERT INTO counter VALUES(?, 0, 0, 0, 0)", t)
        conn.commit()

    def Remove_Guild(self, guild_id):
        c = conn.cursor()
        t = (guild_id,)
        c.execute("DELETE FROM guilds WHERE guild_id=?;", t)
        c.execute("DELETE FROM channels WHERE guild_id=?;", t)
        c.execute("DELETE FROM counter WHERE guild_id=?", t)
        conn.commit()

    def Add_Channel(self, channel_id, guild_id):
        c = conn.cursor()
        t = (guild_id, channel_id)
        try:
            c.execute("SELECT * FROM channels where channel_id=?", [t[1]])
            c.fetchone()[1]
        except:
            c.execute("INSERT INTO channels VALUES (?, ?, 'off')", t)
            conn.commit()

    # Status

    def Change_Modtoggle(self, guild_id, modtoggle):
        c = conn.cursor()
        t = (modtoggle, guild_id)
        c.execute("UPDATE guilds SET modtoggle=? WHERE guild_id=?", t)
        conn.commit()

    def Get_Modtoggle(self, guild_id):
        c = conn.cursor()
        t = (guild_id,)
        c.execute("SELECT modtoggle FROM guilds WHERE guild_id=?", t)
        return c.fetchone()[0]

    def Change_Status(self, channel_id, status):
        c = conn.cursor()
        t = (status, channel_id)
        c.execute("UPDATE channels SET status=? WHERE channel_id=?", t)
        conn.commit()

    def Get_Status(self, channel_id):
        c = conn.cursor()
        t = (channel_id,)
        c.execute("SELECT status FROM channels WHERE channel_id=?", t)
        return c.fetchone()[0]

    def Get_All_Status(self, guild_id):
        c = conn.cursor()
        t = (guild_id,)
        c.execute("SELECT channel_id, status FROM channels WHERE guild_id=?", t)
        newdata = []
        for channel in c.fetchall():
            newdata.append((channel[0], channel[1]))
        return newdata


    # Economy

    def register(self, user_id):
        c = conn.cursor()
        t = (user_id,)
        c.execute("SELECT user_id FROM users WHERE user_id=?", t)
        if c.fetchone() is None:
            t = (user_id,-1,10000,0,0,0,0,'None', '{}', 'None',0,0,0)
            marks = ",".join(["?"] * 13)
            c.execute(f"INSERT INTO users VALUES({marks})", t)
            conn.commit()

    def increasemultiplier(self, user_id, guild_id, number):
        c = conn.cursor()
        t = (number, user_id)
        c.execute("UPDATE users SET multiplier=multiplier+? WHERE user_id=?;", t)
        t = (number, guild_id)
        c.execute("UPDATE guilds SET multiplier=multiplier+? WHERE guild_id=?", t)
        conn.commit()

    def getprofile(self, user_id):
        c = conn.cursor()
        t = (user_id,)
        c.execute("SELECT fbux, netfbux, debt, netdebt, job, degree, degreeprogress FROM users WHERE user_id=?", t)
        return c.fetchone()

    def getbal(self, user_id):
        c = conn.cursor()
        t = (user_id,)
        c.execute("SELECT fbux, debt FROM users WHERE user_id=?", t)
        return c.fetchone()

    def getmultis(self, user_id, guild_id):
        usermulti = self.getusermulti(user_id)
        c = conn.cursor()
        t = (guild_id,)
        c.execute("SELECT multiplier FROM guilds WHERE guild_id=?", t)
        return (usermulti, round(c.fetchone()[0]/(10**6), 2))

    def getusermulti(self, user_id):
        c = conn.cursor()
        t = (user_id,)
        c.execute("SELECT multiplier FROM users WHERE user_id=?", t)
        return round(c.fetchone()[0]/(10**4), 2)

    def getjobs(self, user_id):
        c = conn.cursor()
        t = (user_id,)
        c.execute("SELECT jobs FROM users WHERE user_id=?", t)
        return eval(c.fetchone()[0])

    def getjob(self, user_id):
        c = conn.cursor()
        t = (user_id,)
        c.execute("SELECT job FROM users WHERE user_id=?", t)
        return c.fetchone()[0]

    def changejob(self, user_id, job):
        c = conn.cursor()
        t = (job, user_id)
        c.execute("UPDATE users SET job=? WHERE user_id=?", t)
        conn.commit()

    def getdegree(self, user_id):
        c = conn.cursor()
        t = (user_id,)
        c.execute("SELECT degree FROM users WHERE user_id=?", t)
        return c.fetchone()[0]

    def changedegree(self, user_id, degree):
        c = conn.cursor()
        t = (degree, user_id)
        c.execute("UPDATE users SET degree=? WHERE user_id=?", t)
        conn.commit()

    def work(self, user_id, job, income):
        c = conn.cursor()
        balance = self.updatebal(user_id, income)
        t = (user_id,)
        c.execute("SELECT jobs FROM users WHERE user_id=?", t)
        jobs = eval(c.fetchone()[0])
        if job != "Unemployed": jobs[job] += 1
        t = (str(jobs), user_id)
        c.execute("UPDATE users SET jobs=? WHERE user_id=?", t)
        conn.commit()
        self.worked(user_id)
        return balance

    def study(self, user_id, debt):
        c = conn.cursor()
        self.updatedebt(user_id, debt)
        t = (user_id,)
        c.execute("UPDATE users SET degreeprogress=degreeprogress+1 WHERE user_id=?", t)
        conn.commit()
        t = (user_id,)
        c.execute("SELECT degreeprogress FROM users WHERE user_id=?", t)
        return c.fetchone()[0]

    def canwork(self, user_id):
        c = conn.cursor()
        t = (user_id,)
        c.execute("SELECT lastwork FROM users WHERE user_id=?", t)
        return c.fetchone()[0] <= datetime.now().timestamp() / 60

    def canstudy(self, user_id):
        c = conn.cursor()
        t = (user_id,)
        c.execute("SELECT laststudy FROM users WHERE user_id=?", t)
        return c.fetchone()[0] <= datetime.now().timestamp() / 60

    def lastwork(self, user_id):
        c = conn.cursor()
        t = (user_id,)
        c.execute("SELECT lastwork FROM users WHERE user_id=?", t)
        return round(c.fetchone()[0] - datetime.now().timestamp() / 60)

    def laststudy(self, user_id):
        c = conn.cursor()
        t = (user_id,)
        c.execute("SELECT laststudy FROM users WHERE user_id=?", t)
        return round(c.fetchone()[0] - datetime.now().timestamp() / 60)

    def worked(self, user_id):
        c = conn.cursor()
        t = (datetime.now().timestamp() / 60 + 60, user_id)
        c.execute("UPDATE users SET lastwork=? WHERE user_id=?", t)
        conn.commit()

    def studied(self, user_id):
        c = conn.cursor()
        t = (datetime.now().timestamp() / 60 + 60, user_id)
        c.execute("UPDATE users SET laststudy=? WHERE user_id=?", t)
        conn.commit()

    def resign(self, user_id):
        c = conn.cursor()
        t = (user_id,)
        c.execute("UPDATE users SET job='Unemployed' WHERE user_id=?", t)
        conn.commit()

    def drop(self, user_id):
        c = conn.cursor()
        t = (user_id,)
        c.execute("UPDATE users SET degree='None', degreeprogress=0 WHERE user_id=?", t)
        conn.commit()

    def updatebal(self, user_id, income):
        c = conn.cursor()
        t = (income, income, user_id)
        c.execute("UPDATE users SET fbux=fbux+?, netfbux=netfbux+? WHERE user_id=?", t)
        conn.commit()
        t = (user_id,)
        c.execute("SELECT fbux FROM users WHERE user_id=?", t)
        return c.fetchone()[0]

    def updatedebt(self, user_id, debt):
        c = conn.cursor()
        t = (debt, debt, user_id)
        c.execute("UPDATE users SET debt=debt+?, netdebt=netdebt+? WHERE user_id=?", t)
        conn.commit()
        t = (user_id,)
        c.execute("SELECT debt FROM users WHERE user_id=?", t)
        return c.fetchone()[0]

    def finishdegree(self, user_id):
        c = conn.cursor()
        t = (user_id,)
        c.execute("UPDATE users SET degree='None', degreeprogress=0 WHERE user_id=?", t)
        conn.commit()

    def startjob(self, user_id, job):
        c = conn.cursor()
        t = (user_id,)
        c.execute("SELECT jobs FROM users WHERE user_id=?", t)
        jobs = eval(c.fetchone()[0])
        jobs[job] = 100
        t = (str(jobs), user_id)
        c.execute("UPDATE users SET jobs=? WHERE user_id=?", t)
        conn.commit()

    def gettop(self, tt):
        if tt == "bal": tt = "fbux"
        elif tt == "netbal": tt = "netfbux"
        c = conn.cursor()
        c.execute(f"SELECT user_id, {tt} FROM users ORDER BY {tt} DESC LIMIT 15")
        return enumerate(c)        

    # Prefix

    def Change_Prefix(self, guild_id, prefix):
        c = conn.cursor()
        t = (prefix, guild_id)
        c.execute("UPDATE guilds SET prefix=? WHERE guild_id=?", t)
        conn.commit()

    def Get_Prefix(self, guild_id):
        c = conn.cursor()
        t = (guild_id,)
        c.execute("SELECT prefix FROM guilds WHERE guild_id=?", t)
        return c.fetchone()[0]

    def Change_Priority(self, guild_id, priority):
        c = conn.cursor()
        t = (priority, guild_id)
        c.execute("UPDATE guilds SET priority=? WHERE guild_id=?", t)
        conn.commit()

    def Get_Priority(self, guild_id):
        c = conn.cursor()
        t = (guild_id,)
        c.execute("SELECT priority FROM guilds WHERE guild_id=?", t)
        return c.fetchone()[0]

    # ppsize

    def getppsize(self, user_id):
        c = conn.cursor()
        t = (user_id,)
        c.execute("SELECT ppsize FROM users WHERE user_id=?", t)
        return c.fetchone()[0]

    def updateppsize(self, user_id, size):
        c = conn.cursor()
        t = (size, user_id)
        c.execute("UPDATE users SET ppsize=? WHERE user_id=?", t)
        conn.commit()

    # Counting
        
    def ignorechannel(self, guild_id, channel_id):
        c = conn.cursor()
        t = (guild_id,)
        c.execute("SELECT channel_id FROM counter WHERE guild_id=?", t)
        if channel_id != c.fetchone()[0]: return True
        return False

    def checkdouble(self, guild_id, user_id):
        c = conn.cursor()
        t = (guild_id,)
        c.execute("SELECT user_id FROM counter WHERE guild_id=?", t)
        if user_id == c.fetchone()[0]:
            t = (guild_id,)
            c.execute("UPDATE counter SET number=0, user_id=0 WHERE guild_id=?", t)
            conn.commit()
            return True
        return False

    def getnumber(self, guild_id):
        c = conn.cursor()
        t = (guild_id,)
        c.execute("SELECT number FROM counter WHERE guild_id=?", t)
        return int(c.fetchone()[0])

    def getuser(self, guild_id):
        c = conn.cursor()
        t = (guild_id,)
        c.execute("SELECT user_id FROM counter WHERE guild_id=?", t)
        return int(c.fetchone()[0])

    def gethighscore(self, guild_id):
        c = conn.cursor()
        t = (guild_id,)
        c.execute("SELECT record FROM counter WHERE guild_id=?", t)
        return c.fetchone()[0]

    def gethighscores(self):
        c = conn.cursor()
        c.execute("SELECT guild_id, record FROM counter ORDER BY record DESC LIMIT 5")
        return c.fetchall()

    def resetnumber(self, guild_id):
        c = conn.cursor()
        t = (guild_id,)
        c.execute("UPDATE counter SET number=0, user_id=0 WHERE guild_id=?", t)
        conn.commit()

    def updatenumber(self, number, author_id, guild_id):
        c = conn.cursor()
        t = (number, author_id, guild_id,)
        c.execute("UPDATE counter SET number=?, user_id=? WHERE guild_id=?", t)
        conn.commit()

    def highscore(self, number, guild_id):
        c = conn.cursor()
        t = (guild_id,)
        c.execute("SELECT record FROM counter WHERE guild_id=?", t)
        if number > c.fetchone()[0]:
            t = (number, guild_id,)
            c.execute("UPDATE counter SET record=? WHERE guild_id=?", t)
            conn.commit()
        
    def setcountingchannel(self, channel_id, guild_id):	
        c = conn.cursor()
        t = (channel_id, guild_id)	
        c.execute("UPDATE counter SET channel_id=? WHERE guild_id=?", t)	
        conn.commit()
