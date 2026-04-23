import base64
import re
import requests
import socket

OUTPUT_FILE = "sub_base64.txt"

def load_sources():
    with open("sources.txt", "r") as f:
        return [line.strip() for line in f if line.strip()]

def fetch_configs(urls):
    all_lines = []
    for url in urls:
        try:
            r = requests.get(url, timeout=10)
            text = r.text.strip()

            try:
                decoded = base64.b64decode(text).decode("utf-8")
                lines = decoded.splitlines()
            except:
                lines = text.splitlines()

            all_lines.extend(lines)
            print(f"OK: {url}")

        except:
            print(f"ERROR: {url}")

    return all_lines

def is_alive(host, port):
    try:
        socket.create_connection((host, int(port)), timeout=2)
        return True
    except:
        return False

def get_host_port(line):
    try:
        main = line.split("://")[1]
        addr = main.split("@")[1]
        host_port = addr.split("?")[0]
        host, port = host_port.split(":")
        return host, port
    except:
        return None, None

def clean_line(line):
    line = line.strip()

    if not line.startswith(("vless://", "vmess://", "trojan://")):
        return None

    if "00000000-0000" in line:
        return None

    host, port = get_host_port(line)
    if not host or not port:
        return None

    if not is_alive(host, port):
        return None

    line = re.sub(r"#.*", "", line)

    if line.startswith("vless://"):
        name = "VLESS"
    elif line.startswith("vmess://"):
        name = "VMESS"
    elif line.startswith("trojan://"):
        name = "TROJAN"
    else:
        name = "VPN"

    return f"{line}#{name} | {host}"

def main():
    urls = load_sources()
    lines = fetch_configs(urls)

    cleaned = []
    for line in lines:
        cl = clean_line(line)
        if cl:
            cleaned.append(cl)

    cleaned = list(set(cleaned))

    print(f"TOTAL: {len(cleaned)}")

    encoded = base64.b64encode("\n".join(cleaned).encode()).decode()

    with open(OUTPUT_FILE, "w") as f:
        f.write(encoded)

if __name__ == "__main__":
    main()
