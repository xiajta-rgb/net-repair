import socket
import ssl
import os
import sys

def test_https(host, port=443, timeout=10):
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ssock = ctx.wrap_socket(sock, server_hostname=host)
        version = ssock.version()
        ssock.close()
        sock.close()
        return True, version
    except Exception as e:
        return False, str(e)

print("=" * 60)
print("  网络诊断测试")
print("=" * 60)
print(f"\n当前进程: {os.path.basename(sys.executable)} (PID: {os.getpid()})")
print()

test_cases = [
    ("www.baidu.com", "百度"),
    ("www.feishu.cn", "飞书官网"),
    ("xcnplmqtjyqc.feishu.cn", "飞书多维表格"),
]

print("--- TLS 连接测试 ---")
for host, name in test_cases:
    ok, data = test_https(host)
    if ok:
        print(f"  {name} ({host}): OK ({data})")
    else:
        print(f"  {name} ({host}): FAIL - {data}")

print()
print("如果所有测试都OK，说明网络正常。")
print("如果飞书FAIL但百度OK，说明存在WFP进程名拦截。")