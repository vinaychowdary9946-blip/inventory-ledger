"""Transactional event ledger with optimistic versions and idempotent commands."""
import json
import sqlite3


class Ledger:
    def __init__(self, path='inventory.db'):
        self.db = sqlite3.connect(path, timeout=10, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.executescript('''CREATE TABLE IF NOT EXISTS events(
        sequence INTEGER PRIMARY KEY AUTOINCREMENT, command TEXT UNIQUE NOT NULL,
        sku TEXT NOT NULL, delta INTEGER NOT NULL, version INTEGER NOT NULL,
        reason TEXT NOT NULL, created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(sku,version)); CREATE INDEX IF NOT EXISTS by_sku ON events(sku,version);''')

    def close(self):
        self.db.close()

    def state(self, sku):
        r = self.db.execute('SELECT COALESCE(SUM(delta),0),COUNT(*) FROM events WHERE sku=?', (sku,)).fetchone()
        return {'sku': sku, 'quantity': r[0], 'version': r[1]}

    def adjust(self, command, sku, delta, expected_version, reason):
        if any(not isinstance(s,str) or not s.strip() or len(s)>200 for s in [command,sku,reason]):
            raise ValueError('Command, SKU and reason must contain 1–200 characters')
        if type(delta) is not int or delta == 0 or abs(delta)>1000000 or type(expected_version) is not int or expected_version<0:
            raise ValueError('Nonzero integer delta and nonnegative version required')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            old = self.db.execute('SELECT * FROM events WHERE command=?', (command,)).fetchone()
            if old:
                if (old['sku'],old['delta'],old['version']-1,old['reason']) != (sku,delta,expected_version,reason):
                    raise ValueError('Command ID reused with different request')
                result = dict(old)
            else:
                current = self.state(sku)
                if current['version'] != expected_version:
                    raise ValueError('Version conflict: refresh inventory before retrying')
                if current['quantity']+delta<0:
                    raise ValueError('Insufficient stock')
                self.db.execute('INSERT INTO events(command,sku,delta,version,reason) VALUES(?,?,?,?,?)',(command,sku,delta,expected_version+1,reason))
                result = dict(self.db.execute('SELECT * FROM events WHERE command=?',(command,)).fetchone())
            self.db.execute('COMMIT')
            return result
        except Exception:
            self.db.execute('ROLLBACK')
            raise

    def events(self, sku=None):
        sql = 'SELECT * FROM events' + (' WHERE sku=?' if sku else '') + ' ORDER BY sequence'
        return [dict(r) for r in self.db.execute(sql, (sku,) if sku else ())]


if __name__ == '__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db', default='inventory.db')
    p.add_argument('action', choices=['adjust','state','events'])
    p.add_argument('--sku',default='SENSOR-01')
    p.add_argument('--command',default='receipt-001')
    p.add_argument('--delta',type=int,default=10)
    p.add_argument('--version',type=int,default=0)
    p.add_argument('--reason',default='Supplier receipt')
    a=p.parse_args(); ledger=Ledger(a.db)
    try:
        result=ledger.adjust(a.command,a.sku,a.delta,a.version,a.reason) if a.action=='adjust' else ledger.state(a.sku) if a.action=='state' else ledger.events()
        print(json.dumps(result,indent=2))
    finally:
        ledger.close()
