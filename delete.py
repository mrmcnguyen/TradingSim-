import sqlite3

conn = sqlite3.connect('trading_simulator.db')
cursor = conn.cursor()
symbol_to_delete = "NVDA"
cursor.execute('DELETE FROM Holdings WHERE symbol = ?', (symbol_to_delete,))
conn.commit()
conn.close()