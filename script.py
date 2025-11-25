import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import quote
import urllib3

# ---------------------------------------------------------------------------------
# FINAL EXAM RESTCONF SCRIPT – BY KASEM  (IDEMPOTENT – CLEAN – EXAM READY)
# ---------------------------------------------------------------------------------

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =========================================================
# ► AJUSTA ESTAS IPs AL INICIO DEL EXAMEN
# =========================================================
R1_IP = "192.168.1.10"      # IP de gestión de R1 (profesor la dará)
R2_IP = "192.168.1.11"      # IP de gestión de R2 (profesor la dará)

USERNAME = "cisco"
PASSWORD = "cisco123!"

# =========================================================
# ► RESTCONF HEADERS
# =========================================================
def headers():
    return {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json"
    }

# =========================================================
# ► CONFIGURAR UNA INTERFAZ
# =========================================================
def put_interface(router_ip, if_name, ip, netmask):
    encoded_if = quote(if_name, safe='')
    url = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces/interface={encoded_if}"

    payload = {
        "ietf-interfaces:interface": {
            "name": if_name,
            "type": "iana-if-type:ethernetCsmacd",
            "enabled": True,
            "ietf-ip:ipv4": {
                "address": [
                    {"ip": ip, "netmask": netmask}
                ]
            }
        }
    }

    resp = requests.put(
        url,
        auth=HTTPBasicAuth(USERNAME, PASSWORD),
        headers=headers(),
        json=payload,
        verify=False
    )

    print(f"[{router_ip}] PUT {if_name} → {resp.status_code}")

# =========================================================
# ► CONFIGURAR LOOPBACK
# =========================================================
def put_loopback(router_ip, name, ip, netmask):
    url = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces/interface={name}"

    payload = {
        "ietf-interfaces:interface": {
            "name": name,
            "type": "iana-if-type:softwareLoopback",
            "enabled": True,
            "ietf-ip:ipv4": {
                "address": [
                    {"ip": ip, "netmask": netmask}
                ]
            }
        }
    }

    resp = requests.put(
        url,
        auth=HTTPBasicAuth(USERNAME, PASSWORD),
        headers=headers(),
        json=payload,
        verify=False
    )

    print(f"[{router_ip}] PUT {name} → {resp.status_code}")

# =========================================================
# ► CONFIGURAR RUTA ESTÁTICA
# =========================================================
def put_route(router_ip, prefix, netmask, nexthop):
    key = f"{prefix},{netmask}"
    url = f"https://{router_ip}/restconf/data/Cisco-IOS-XE-native:native/ip/route/ip-route-interface-forwarding-list={key}"

    payload = {
        "Cisco-IOS-XE-native:ip-route-interface-forwarding-list": {
            "prefix": prefix,
            "mask": netmask,
            "fwd-list": [{"fwd": nexthop}]
        }
    }

    resp = requests.put(
        url,
        auth=HTTPBasicAuth(USERNAME, PASSWORD),
        headers=headers(),
        json=payload,
        verify=False
    )

    print(f"[{router_ip}] ROUTE {prefix}/{netmask} → {resp.status_code}")

# =========================================================
# ► CONFIG R1
# =========================================================
def configure_R1():
    print("\n=== CONFIGURANDO R1 ===")

    # LAN
    put_interface(R1_IP, "GigabitEthernet0/0/0", "10.10.10.1", "255.255.255.0")

    # WAN
    put_interface(R1_IP, "GigabitEthernet0/0/1", "172.16.1.1", "255.255.255.252")

    # LOOPBACK
    put_loopback(R1_IP, "Loopback1", "8.8.8.8", "255.255.255.0")

    # RUTAS
    put_route(R1_IP, "10.10.20.0", "255.255.255.0", "172.16.1.2")
    put_route(R1_IP, "0.0.0.0", "0.0.0.0", "172.16.1.2")

# =========================================================
# ► CONFIG R2
# =========================================================
def configure_R2():
    print("\n=== CONFIGURANDO R2 ===")

    # LAN
    put_interface(R2_IP, "GigabitEthernet0/0/0", "10.10.20.1", "255.255.255.0")

    # WAN
    put_interface(R2_IP, "GigabitEthernet0/0/1", "172.16.1.2", "255.255.255.252")

    # LOOPBACK
    put_loopback(R2_IP, "Loopback1", "9.9.9.9", "255.255.255.0")

    # RUTAS
    put_route(R2_IP, "10.10.10.0", "255.255.255.0", "172.16.1.1")

# =========================================================
# ► MAIN
# =========================================================
if __name__ == "__main__":
    configure_R1()
    configure_R2()

    print("\n=== CONFIGURACIÓN COMPLETADA ===\n")
