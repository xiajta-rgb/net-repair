import sqlite3
import hashlib
import time

db_path = r'C:\ProgramData\Tencent\QQPCMgr\TAVWfsDB\WhiteList.db'

domains = [
    'feishu.cn',
    'www.feishu.cn',
    'xcnplmqtjyqc.feishu.cn',
    'accounts.feishu.cn',
    'open.feishu.cn',
    'larkoffice.com',
    'larksuite.com',
]

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM LocalCloudWhiteList")
    existing = cursor.fetchall()
    print(f"Existing entries: {len(existing)}")

    now = int(time.time())
    added = 0
    for domain in domains:
        md5 = hashlib.md5(domain.encode()).hexdigest()
        try:
            cursor.execute("INSERT OR REPLACE INTO LocalCloudWhiteList (MD5, AddTime) VALUES (?, ?)", (md5, now))
            added += 1
            print(f"  Added: {domain} -> {md5}")
        except Exception as e:
            print(f"  Failed: {domain} -> {e}")

    conn.commit()

    cursor.execute("SELECT * FROM LocalCloudWhiteList")
    rows = cursor.fetchall()
    print(f"\nTotal entries after: {len(rows)}")
    for row in rows:
        print(f"  {row}")

    conn.close()
    print(f"\nAdded {added} domains to whitelist. Restart QQPCRTP service to take effect.")

except Exception as e:
    print(f"Error: {e}")
