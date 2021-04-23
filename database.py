import sqlite3

def ensureConnection(func):
	def inner(*args, **kwargs):
		with sqlite3.connect("database.db") as conn:
			kwargs["conn"] = conn
			res = func(*args, **kwargs)
		return res
	return inner

@ensureConnection
def initDB(conn, force: bool = False):
	c = conn.cursor()
	if force:
		c.execute("DROP TABLE IF EXISTS userFiles")
		c.execute("DROP TABLE IF EXISTS userList")
		c.execute("DROP TABLE IF EXISTS userLanguage")
	c.execute("""
		CREATE TABLE IF NOT EXISTS userFiles (
			userID          INTEGER NOT NULL,
			inputFileSize   TEXT NOT NULL,
			outputFileSize  TEXT NOT NULL,
			timeNow         TEXT NOT NULL,
			dayNow          TEXT NOT NULL,
			processing      TEXT NOT NULL
		)
	""")
	c.execute("""
		CREATE TABLE IF NOT EXISTS userList (
			userID          INTEGER PRIMARY KEY,
			timeNow         TEXT NOT NULL,
			dayNow          TEXT NOT NULL
		)
	""")
	c.execute("""
		CREATE TABLE IF NOT EXISTS userLanguage (
			userID          INTEGER PRIMARY KEY,
			language        TEXT NOT NULL
		)
	""")
	conn.commit()

@ensureConnection
def saveFile(conn, userID: int, inputFileSize: str, outputFileSize: str, timeNow: str, dayNow: str, processing: str):
	c = conn.cursor()
	c.execute("INSERT INTO userFiles (userID, inputFileSize, outputFileSize, timeNow, dayNow, processing) VALUES (?, ?, ?, ?, ?, ?)", (userID, inputFileSize, outputFileSize, timeNow, dayNow, processing))
	conn.commit()

@ensureConnection
def userList(conn, userID: int, timeNow: str, dayNow: str):
	c = conn.cursor()
	c.execute("INSERT OR IGNORE INTO userList (userID, timeNow, dayNow) VALUES (?, ?, ?)", (userID, timeNow, dayNow))
	conn.commit()

@ensureConnection
def userLanguage(conn, userID: int, language: str):
	c = conn.cursor()
	c.execute("INSERT INTO userLanguage (userID, language) VALUES (?, ?)", (userID, language))
	conn.commit()

@ensureConnection
def userLanguageChange(conn, userID: int, language: str):
	c = conn.cursor()
	c.execute("UPDATE userLanguage SET language = ? WHERE userID = ?", (language, userID))
	conn.commit()

@ensureConnection
def userLanguageGet(conn, userID: int):
	c = conn.cursor()
	c.execute("SELECT language FROM userLanguage WHERE userID = ?", (userID, ))
	result = c.fetchone()
	if result:
		return result[0]