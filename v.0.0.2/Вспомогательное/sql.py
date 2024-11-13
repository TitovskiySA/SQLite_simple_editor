import sqlite3

""" CREATE TABLE """

try:
	
	conn = sqlite3.connect('test.db')
	conn.execute('''CREATE TABLE COMPANY
         (ID INT PRIMARY KEY     NOT NULL,
         NAME           TEXT    NOT NULL,
         STUDENTID            INT     NOT NULL,
         ADDRESS        CHAR(50),
         SCORE         REAL);''')
	conn.execute('''CREATE TABLE COMPANY2
         (ID INT PRIMARY KEY     NOT NULL,
         NAME           TEXT    NOT NULL,
         STUDENTID            INT     NOT NULL,
         ADDRESS        CHAR(50),
         SCORE         REAL);''')
	print ("Table created successfully")
	conn.close()
except:
	raise Exception

""" INSERT DATA INTO TABLE """
try:
 
	conn = sqlite3.connect('test.db')
	conn.execute("delete from COMPANY")
	conn.execute("INSERT INTO COMPANY (ID,NAME,STUDENTID,ADDRESS,SCORE) VALUES (1, " + "'AAA', 32, 'UK', 20000.00 )");
	conn.execute("INSERT INTO COMPANY (ID,NAME,STUDENTID,ADDRESS,SCORE) VALUES (2, 'BBB', 25, 'Canada', 15000.00 )");
	conn.execute("INSERT INTO COMPANY (ID,NAME,STUDENTID,ADDRESS,SCORE) VALUES (3, 'CCC', 23, 'China', 20000.00 )");
	#conn.execute("INSERT INTO COMPANY (ID,NAME,STUDENTID,ADDRESS,SCORE) VALUES (9, 'DDD', 25, 'Mont Blanc ', 65000.00 )");
	conn.execute("INSERT INTO COMPANY (ID,NAME,STUDENTID,ADDRESS) VALUES (9, 'DDD', 25, 'Mont Blanc ')")
	conn.commit()
	conn.close()
except:
	raise Exception

""" PRINT TABLE """

conn = sqlite3.connect('test.db')
cursor = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table';")
tables = [table[0] for table in cursor.fetchall()]
#tables = []
#for table in cursor.fetchall():
#        tables.append(table[0])
print("NAME = " + str(tables))
#cursor = conn.execute("SELECT ID, NAME, STUDENTID, ADDRESS, SCORE from COMPANY")
cursor = conn.execute("SELECT * from " + tables[0])
names = [description[0] for description in cursor.description]
print(str(names))
for row in cursor:
        print(str(row))

cursor = conn.execute("SELECT name, type FROM pragma_table_info('" + tables[0] + "')")
print("here types")
for row in cursor:
        #print(str(row))
        lable = row[0] + "\n<" + row[1] + ">"
        print(lable)


        
#for name in names:
#        cursor = conn.execute("SELECT name, type FROM pragma_table_info('" + name + "')")
#        for row in cursor:
#                print(str(row))
#for row in cursor:
#   print ("ID = ", row[0])
#   print ("NAME = ", row[1])
#   print ("STUDENT ID = ", row[2])
#   print ("ADDRESS = ", row[3])
#   print ("SCORE = ", row[4], "\n")
#print("Records created successfully")
conn.close()
# visit pyshine.com for more detail
""" UPDATE TABLE """

conn = sqlite3.connect('test.db')
conn.execute("UPDATE COMPANY set SCORE = 25000.00 where ID = 1")
#conn.execute("UPDATE COMPANY set SCORE = 77777.00 where STUDENTID = 25")
#conn.execute("UPDATE COMPANY delete SCORE where STUDENTID = 25")
conn.commit()
conn.close()

""" PRINT TABLE """

conn = sqlite3.connect('test.db')
#cursor = conn.execute("SELECT ID, NAME, STUDENTID,  ADDRESS, SCORE from COMPANY")
cursor = conn.execute("SELECT * from COMPANY")
print(cursor)
for row in cursor:
   print(str(row))
   print ("ID = ", row[0])
   print ("NAME = ", row[1])
   print ("STUDENT ID = ", row[2])
   print ("ADDRESS = ", row[3])
   print ("SCORE = ", row[4], "\n")
print("Records created successfully")
conn.close()


