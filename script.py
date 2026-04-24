import base64
import re
import requests
import socket

OUTPUT_FILE = "sub_base64.txt"

# 🔗 загрузка источников
def load_sources():
    with open("sources.txt", "r") as f:
        return [line.strip() for line in f if line.strip()]

# 🌐 получение конфигов
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

# 🔌 проверка порта
def is_alive(host, port):
    try:
        socket.create_connection((host, int(port)), timeout=3)
        return True
    except:
        return False

# 📦 достаём host и port
def get_host_port(line):
    try:
        main = line.split("://")[1]
        addr = main.split("@")[1]
        host_port = addr.split("?")[0]
        host, port = host_port.split(":")
        return host, port
    except:
        return None, None

# 🌍 страна по IP
def get_country(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
        return r.get("country", "Unknown"), r.get("countryCode", "")
    except:
        return "Unknown", ""

# 🇫🇮 флаг
def get_flag(code):
    if len(code) != 2:
        return "🌍"
    return chr(127397 + ord(code[0])) + chr(127397 + ord(code[1]))

# 🧹 очистка
def clean_line(line):
    line = line.strip()

    if not line.startswith(("vless://", "vmess://", "trojan://")):
        return None

    if "00000000-0000" in line:
        return None

    host, port = get_host_port(line)
    if not host or not port:
        return None

    # 🌍 определяем страну
    if re.match(r"\d+\.\d+\.\d+\.\d+", host):
        country, code = get_country(host)
        flag = get_flag(code)
    else:
        country = "Domain"
        flag = "🌐"

    # убираем старое имя
    line = re.sub(r"#.*", "", line)

    if line.startswith("vless://"):
        proto = "VLESS"
    elif line.startswith("vmess://"):
        proto = "VMESS"
    elif line.startswith("trojan://"):
        proto = "TROJAN"
    else:
        proto = "VPN"

    name = f"{flag} {country} | {proto}"

    return f"{line}#{name}"

# 🚀 основной запуск
def main():
    urls = load_sources()
    lines = fetch_configs(urls)

    alive = []
    maybe = []

    for line in lines:
        cl = clean_line(line)
        if not cl:
            continue

        host, port = get_host_port(cl)

        try:
            if is_alive(host, port):
                alive.append(cl)
            else:
                maybe.append(cl)
        except:
            maybe.append(cl)

    # 🔥 сначала живые
    result = alive + maybe

    # 🔥 ограничение количества (можешь менять)
    result = result[:10111]

    print(f"ALIVE: {len(alive)} | TOTAL USED: {len(result)}")

    encoded = base64.b64encode("\n".join(result).encode()).decode()

    with open(OUTPUT_FILE, "w") as f:
        f.write(encoded)

if __name__ == "__main__":
    main()
