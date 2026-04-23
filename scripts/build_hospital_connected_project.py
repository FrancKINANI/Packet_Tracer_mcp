"""Build a Packet Tracer deliverable for the hospital 802.1X/RADIUS project."""

from __future__ import annotations

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.packet_tracer_mcp.domain.models.plans import DevicePlan, LinkPlan, StaticRoute, TopologyPlan
from src.packet_tracer_mcp.domain.services.validator import validate_plan
from src.packet_tracer_mcp.infrastructure.execution.manual_executor import ManualExecutor


PROJECT_NAME = "hospital_connected_8021x"
OUTPUT_ROOT = Path("projects")


def build_plan() -> TopologyPlan:
    vlan_note = (
        "VLAN 10 = MEDECINS | VLAN 20 = INFIRMIERS | VLAN 30 = VISITEURS | VLAN 99 = MANAGEMENT"
    )

    devices = [
        DevicePlan(
            name="ISP",
            model="Cloud-PT",
            category="cloud",
            x=560,
            y=40,
        ),
        DevicePlan(
            name="R1",
            model="2911",
            category="router",
            x=560,
            y=150,
            interfaces={
                "GigabitEthernet0/0": "203.0.113.2/30",
                "GigabitEthernet0/1": "10.255.255.1/30",
            },
            config_text="""
interface GigabitEthernet0/0
 description WAN vers ISP
 ip nat outside
 exit
interface GigabitEthernet0/1
 description Transit vers CORE1
 ip nat inside
 exit
access-list 10 permit 192.168.10.0 0.0.0.255
access-list 10 permit 192.168.20.0 0.0.0.255
access-list 10 permit 192.168.30.0 0.0.0.255
access-list 10 permit 192.168.99.0 0.0.0.255
ip nat inside source list 10 interface GigabitEthernet0/0 overload
""".strip(),
        ),
        DevicePlan(
            name="CORE1",
            model="3650-24PS",
            category="switch",
            x=560,
            y=280,
            interfaces={
                "GigabitEthernet1/0/1": "10.255.255.2/30",
                "Vlan10": "192.168.10.1/24",
                "Vlan20": "192.168.20.1/24",
                "Vlan30": "192.168.30.1/24",
                "Vlan99": "192.168.99.1/24",
            },
            config_text="""
ip routing
vlan 10
 name MEDECINS
vlan 20
 name INFIRMIERS
vlan 30
 name VISITEURS
vlan 99
 name MANAGEMENT
interface GigabitEthernet1/0/1
 no switchport
 ip address 10.255.255.2 255.255.255.252
 no shutdown
 exit
interface GigabitEthernet1/0/2
 description Trunk vers ACCESS1
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30,99
 no shutdown
 exit
interface GigabitEthernet1/0/3
 description Serveur RADIUS
 switchport mode access
 switchport access vlan 99
 no shutdown
 exit
interface Vlan10
 description Passerelle Medecins
 ip address 192.168.10.1 255.255.255.0
 no shutdown
 exit
interface Vlan20
 description Passerelle Infirmiers
 ip address 192.168.20.1 255.255.255.0
 no shutdown
 exit
interface Vlan30
 description Passerelle Visiteurs
 ip address 192.168.30.1 255.255.255.0
 no shutdown
 exit
interface Vlan99
 description Management
 ip address 192.168.99.1 255.255.255.0
 no shutdown
 exit
ip access-list extended ACL_VISITEURS
 deny ip 192.168.30.0 0.0.0.255 192.168.10.0 0.0.0.255
 deny ip 192.168.30.0 0.0.0.255 192.168.20.0 0.0.0.255
 permit ip 192.168.30.0 0.0.0.255 any
exit
interface Vlan30
 ip access-group ACL_VISITEURS in
 exit
ip route 0.0.0.0 0.0.0.0 10.255.255.1
""".strip(),
        ),
        DevicePlan(
            name="ACCESS1",
            model="2960-24TT",
            category="switch",
            x=560,
            y=430,
            gateway="192.168.99.1",
            config_text="""
vlan 10
 name MEDECINS
vlan 20
 name INFIRMIERS
vlan 30
 name VISITEURS
vlan 99
 name MANAGEMENT
interface Vlan99
 ip address 192.168.99.2 255.255.255.0
 no shutdown
 exit
ip default-gateway 192.168.99.1
interface GigabitEthernet0/1
 description Trunk vers CORE1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30,99
 no shutdown
 exit
aaa new-model
aaa authentication dot1x default group radius
dot1x system-auth-control
radius-server host 192.168.99.10 auth-port 1812 key MonSharedSecret2024
interface FastEthernet0/2
 description AP Zone A - Urgences
 switchport mode access
 switchport access vlan 99
 authentication port-control auto
 dot1x pae authenticator
 authentication event fail action authorize vlan 99
 spanning-tree portfast
 exit
interface FastEthernet0/3
 description AP Zone B - Consultation
 switchport mode access
 switchport access vlan 99
 authentication port-control auto
 dot1x pae authenticator
 authentication event fail action authorize vlan 99
 spanning-tree portfast
 exit
interface FastEthernet0/4
 description AP Zone C - Hall
 switchport mode access
 switchport access vlan 99
 authentication port-control auto
 dot1x pae authenticator
 authentication event fail action authorize vlan 99
 spanning-tree portfast
 exit
interface FastEthernet0/5
 description Reserve management
 switchport mode access
 switchport access vlan 99
 spanning-tree portfast
 exit
""".strip(),
        ),
        DevicePlan(
            name="RADIUS1",
            model="Server-PT",
            category="server",
            x=860,
            y=280,
            interfaces={"FastEthernet0": "192.168.99.10/24"},
            gateway="192.168.99.1",
            config_text="""
Packet Tracer - Server AAA/DHCP

Desktop > IP Configuration
- IP address: 192.168.99.10
- Subnet mask: 255.255.255.0
- Default gateway: 192.168.99.1
- DNS: 8.8.8.8

Services > AAA
- Service: On
- Authentication: 802.1X
- RADIUS shared secret: MonSharedSecret2024
- User: dr.martin / Pass_Med2024 / VLAN 10
- User: inf.dupont / Pass_Inf2024 / VLAN 20
- User: visiteur / Visit123 / VLAN 30

Services > DHCP
- Pool MEDECINS: Network 192.168.10.0 /24, Default Gateway 192.168.10.1, DNS 8.8.8.8
- Pool INFIRMIERS: Network 192.168.20.0 /24, Default Gateway 192.168.20.1, DNS 8.8.8.8
- Pool VISITEURS: Network 192.168.30.0 /24, Default Gateway 192.168.30.1, DNS 8.8.8.8

RADIUS attributes to return on Access-Accept
- Tunnel-Type = VLAN
- Tunnel-Medium-Type = 802
- Tunnel-Private-Group-ID = role VLAN
""".strip(),
        ),
        DevicePlan(
            name="AP_URG",
            model="AccessPoint-PT",
            category="accesspoint",
            x=250,
            y=560,
            config_text=_ap_instructions("Zone A - Urgences", "192.168.99.20"),
        ),
        DevicePlan(
            name="AP_CONS",
            model="AccessPoint-PT",
            category="accesspoint",
            x=560,
            y=560,
            config_text=_ap_instructions("Zone B - Consultation", "192.168.99.21"),
        ),
        DevicePlan(
            name="AP_HALL",
            model="AccessPoint-PT",
            category="accesspoint",
            x=870,
            y=560,
            config_text=_ap_instructions("Zone C - Hall", "192.168.99.22"),
        ),
        DevicePlan(
            name="PC_DOC1",
            model="PC-PT",
            category="pc",
            x=180,
            y=700,
            config_text=_wifi_client_instructions(
                "PC_DOC1",
                "Medecin",
                "dr.martin",
                "Pass_Med2024",
                "VLAN 10 attendu",
            ),
        ),
        DevicePlan(
            name="PC_DOC2",
            model="PC-PT",
            category="pc",
            x=320,
            y=700,
            config_text=_wifi_client_instructions(
                "PC_DOC2",
                "Medecin",
                "dr.martin",
                "Pass_Med2024",
                "VLAN 10 attendu",
            ),
        ),
        DevicePlan(
            name="LT_INF1",
            model="Laptop-PT",
            category="laptop",
            x=490,
            y=700,
            config_text=_wifi_client_instructions(
                "LT_INF1",
                "Infirmier",
                "inf.dupont",
                "Pass_Inf2024",
                "VLAN 20 attendu",
            ),
        ),
        DevicePlan(
            name="LT_INF2",
            model="Laptop-PT",
            category="laptop",
            x=630,
            y=700,
            config_text=_wifi_client_instructions(
                "LT_INF2",
                "Infirmier",
                "inf.dupont",
                "Pass_Inf2024",
                "VLAN 20 attendu",
            ),
        ),
        DevicePlan(
            name="PHONE_VIS",
            model="SMARTPHONE-PT",
            category="phone",
            x=870,
            y=700,
            config_text="""
Smartphone visiteur
- SSID: HOPITAL_SECURE
- Security: WPA2-Enterprise
- EAP method: PEAP
- Username: visiteur
- Password: Visit123
- VLAN attendu apres authentification: 30
""".strip(),
        ),
    ]

    links = [
        LinkPlan(
            device_a="ISP",
            port_a="Ethernet6",
            device_b="R1",
            port_b="GigabitEthernet0/0",
            cable="straight",
        ),
        LinkPlan(
            device_a="R1",
            port_a="GigabitEthernet0/1",
            device_b="CORE1",
            port_b="GigabitEthernet1/0/1",
            cable="straight",
        ),
        LinkPlan(
            device_a="CORE1",
            port_a="GigabitEthernet1/0/2",
            device_b="ACCESS1",
            port_b="GigabitEthernet0/1",
            cable="cross",
        ),
        LinkPlan(
            device_a="ACCESS1",
            port_a="FastEthernet0/2",
            device_b="AP_URG",
            port_b="Port 0",
            cable="straight",
        ),
        LinkPlan(
            device_a="ACCESS1",
            port_a="FastEthernet0/3",
            device_b="AP_CONS",
            port_b="Port 0",
            cable="straight",
        ),
        LinkPlan(
            device_a="ACCESS1",
            port_a="FastEthernet0/4",
            device_b="AP_HALL",
            port_b="Port 0",
            cable="straight",
        ),
        LinkPlan(
            device_a="CORE1",
            port_a="GigabitEthernet1/0/3",
            device_b="RADIUS1",
            port_b="FastEthernet0",
            cable="straight",
        ),
    ]

    static_routes = [
        StaticRoute(
            router="R1",
            destination="192.168.10.0",
            mask="255.255.255.0",
            next_hop="10.255.255.2",
        ),
        StaticRoute(
            router="R1",
            destination="192.168.20.0",
            mask="255.255.255.0",
            next_hop="10.255.255.2",
        ),
        StaticRoute(
            router="R1",
            destination="192.168.30.0",
            mask="255.255.255.0",
            next_hop="10.255.255.2",
        ),
        StaticRoute(
            router="R1",
            destination="192.168.99.0",
            mask="255.255.255.0",
            next_hop="10.255.255.2",
        ),
    ]

    plan = TopologyPlan(
        name=PROJECT_NAME,
        devices=devices,
        links=links,
        static_routes=static_routes,
        warnings=[vlan_note],
    )
    return plan


def _ap_instructions(zone: str, mgmt_ip: str) -> str:
    return f"""
Access Point {zone}
- Management IP: {mgmt_ip} /24
- Default gateway: 192.168.99.1
- SSID: HOPITAL_SECURE
- Security: WPA2-Enterprise
- EAP method: PEAP
- RADIUS server: 192.168.99.10
- RADIUS port: 1812
- Shared secret: MonSharedSecret2024

Roaming note
- Tous les APs portent le meme SSID et pointent vers le meme serveur RADIUS.
- Le VLAN est attribue dynamiquement par le RADIUS selon le role.
""".strip()


def _wifi_client_instructions(name: str, role: str, username: str, password: str, expected_vlan: str) -> str:
    return f"""
Client WiFi {name}
- Role: {role}
- SSID: HOPITAL_SECURE
- Security: WPA2-Enterprise
- EAP method: PEAP
- Username: {username}
- Password: {password}
- Addressing: DHCP
- Verification: obtenir une IP du sous-reseau correspondant ({expected_vlan})
""".strip()


def write_readme(project_dir: Path) -> None:
    readme = f"""# Projet HOPITAL CONNECTE

Topologie generee pour le sujet AAA / RADIUS / 802.1X.

## Architecture retenue

- `R1` (`2911`) : sortie WAN et NAT.
- `CORE1` (`3650-24PS`) : coeur L3, SVIs et filtrage visiteurs.
- `ACCESS1` (`2960-24TT`) : acces, trunk, `dot1x`, serveur RADIUS.
- `RADIUS1` : AAA + DHCP.
- `AP_URG`, `AP_CONS`, `AP_HALL` : meme SSID `HOPITAL_SECURE`.
- Clients : 2 PC medecins, 2 laptops infirmiers, 1 smartphone visiteur.

## Adressage

- Transit `R1` <-> `CORE1` : `10.255.255.0/30`
- VLAN 10 MEDECINS : `192.168.10.0/24`
- VLAN 20 INFIRMIERS : `192.168.20.0/24`
- VLAN 30 VISITEURS : `192.168.30.0/24`
- VLAN 99 MANAGEMENT : `192.168.99.0/24`

## Fichiers utiles

- `topology.js` : script PTBuilder pour poser les equipements et les liens.
- `full_build.js` : topologie + blocs de configuration.
- `*_config.txt` : configuration ou instructions par equipement.
- `anomaly_detection.py` : exemple simple de detection d'anomalies demande en partie 5.

## Hypothese de conception

Le sujet melange le role du `2911` et du `3650`. Cette version prend une option coherente :
le `2911` sert de routeur WAN/NAT, et le `3650` assure le coeur L3 et les gateways des VLANs.
"""
    (project_dir / "README.md").write_text(readme, encoding="utf-8")


def write_anomaly_detector(project_dir: Path) -> None:
    code = '''"""Simple anomaly detection for hospital WiFi logins."""\n\nROLE_ALLOWED_ZONES = {\n    "MEDECIN": {"Zone A", "Zone B"},\n    "INFIRMIER": {"Zone A", "Zone B"},\n    "VISITEUR": {"Zone C"},\n}\n\n\ndef detect_anomaly_rules(login_event: dict) -> list[str]:\n    alerts: list[str] = []\n\n    hour = login_event.get("hour", 12)\n    if hour < 6 or hour > 22:\n        alerts.append("HORAIRE_SUSPECT")\n\n    role = login_event.get("role", "VISITEUR")\n    zone = login_event.get("zone", "Zone C")\n    if zone not in ROLE_ALLOWED_ZONES.get(role, set()):\n        alerts.append("ZONE_INTERDITE")\n\n    failed_attempts = login_event.get("failed_attempts", 0)\n    if failed_attempts > 5:\n        alerts.append("BRUTE_FORCE")\n\n    time_delta_s = login_event.get("time_delta_s", 0)\n    distance_km = login_event.get("distance_km", 0.0)\n    if time_delta_s > 0:\n        speed = distance_km / (time_delta_s / 3600)\n        if speed > 50:\n            alerts.append("IMPOSSIBLE_TRAVEL")\n\n    return alerts\n\n\nif __name__ == "__main__":\n    event = {\n        "user": "dr.martin",\n        "role": "MEDECIN",\n        "hour": 3,\n        "zone": "Zone C",\n        "failed_attempts": 0,\n        "time_delta_s": 30,\n        "distance_km": 0.5,\n    }\n    print(detect_anomaly_rules(event))\n'''
    (project_dir / "anomaly_detection.py").write_text(code, encoding="utf-8")


def write_layout_annotations(project_dir: Path) -> None:
    js = r'''var lw = ipc.appWindow().getActiveWorkspace().getLogicalWorkspace();
lw.addNote("HOPITAL CONNECTE\nAAA / RADIUS / 802.1X", 455, 5);
lw.addNote("Internet / WAN", 535, 5);
lw.addNote("R1 - Routeur WAN / NAT", 505, 120);
lw.addNote("CORE1 - Switch coeur L3\nSVI VLAN 10 / 20 / 30 / 99", 410, 245);
lw.addNote("RADIUS1\n192.168.99.10:1812\nshared secret", 900, 250);
lw.addNote("ACCESS1 - Switch acces L2\n802.1X dot1x + VLAN dynamique", 430, 390);
lw.addNote("AP Zone A\nUrgences", 205, 520);
lw.addNote("AP Zone B\nConsultation", 515, 520);
lw.addNote("AP Zone C\nHall / Visiteurs", 825, 520);
lw.addNote("VLAN 10 - MEDECINS\n192.168.10.0/24", 130, 760);
lw.addNote("VLAN 20 - INFIRMIERS\n192.168.20.0/24", 455, 760);
lw.addNote("VLAN 30 - VISITEURS\n192.168.30.0/24", 810, 760);
reportResult("annotations added");'''
    (project_dir / "layout_annotations.js").write_text(js, encoding="utf-8")


def main() -> None:
    plan = build_plan()
    validation = validate_plan(plan)
    if validation.errors:
        raise SystemExit(f"Plan invalide: {validation.error_messages()}")

    executor = ManualExecutor(output_dir=OUTPUT_ROOT)
    result = executor.execute(plan, project_name=PROJECT_NAME)
    project_dir = Path(result["project_dir"])

    write_readme(project_dir)
    write_anomaly_detector(project_dir)
    write_layout_annotations(project_dir)

    print(f"Project exported to: {project_dir}")
    print(f"Devices: {len(plan.devices)}")
    print(f"Links: {len(plan.links)}")
    print(f"Files: {len(result['files']) + 3}")


if __name__ == "__main__":
    main()
