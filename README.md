# DHCP-STARVATION

> **Autor:** Randy Nin **Laboratorio de Seguridad de Redes | GNS3**

Script de Python que realiza un ataque de Denegación de Servicio (DoS) contra el servidor DHCP de la red mediante el envío masivo de mensajes DHCP Discover con direcciones MAC de origen completamente aleatorias. Cada solicitud fuerza al servidor a crear un binding y consumir una IP del pool, hasta agotarlo por completo e impedir que cualquier cliente legítimo obtenga configuración de red.

---

## Contenido del repositorio

```
DHCP-STARVATION/
├── dhcp_starvation.py
├── Documentación Tecnica Profesional DHCP-STARVATION (Randy Nin -- 2025-0660).pdf
└── README.md
```

---

## Documentación técnica

La documentación técnica completa de este laboratorio está disponible en:

**[Documentación Tecnica Profesional DHCP-STARVATION (Randy Nin -- 2025-0660).pdf](Documentación%20Tecnica%20Profesional%20DHCP-STARVATION%20(Randy%20Nin%20--%202025-0660).pdf)**

Incluye contexto técnico del ataque, topología y configuración del entorno, análisis completo del script, evidencia del agotamiento del pool con capturas, demostración del impacto en nuevos clientes y contramedidas con DHCP Snooping.

---

## Requisitos

**Sistema:** ParrotSec OS, Kali Linux o cualquier distribución Linux con soporte para envío de paquetes raw.

**Python:** 3.x con permisos de superusuario (`sudo`).

**Dependencias externas:**

|Librería|Instalación|
|:--|:--|
|`scapy`|`pip install scapy`|
|`pwntools`|`pip install pwntools`|

**Instalación rápida:**

```bash
pip install scapy pwntools
```

---

## Uso

```bash
sudo python3 dhcp_starvation.py -i <interfaz>
```

**Parámetros:**

|Flag|Descripción|
|:--|:--|
|`-i` / `--interface`|Interfaz de red desde la que se envían los Discovers falsificados|

**Ejemplo usado en el laboratorio:**

```bash
sudo python3 dhcp_starvation.py -i ens4
```

El ataque corre durante 60 segundos y termina automáticamente. También puede detenerse con `Ctrl+C`.

---

## Cómo funciona

Por cada iteración durante 60 segundos, el script genera un mensaje DHCP Discover con una MAC de origen completamente aleatoria y lo envía en broadcast a la red:

```
Ethernet (src=MAC_aleatoria, dst=ff:ff:ff:ff:ff:ff)
  └── IP (src=0.0.0.0, dst=255.255.255.255)
        └── UDP (sport=68, dport=67)
              └── BOOTP + DHCP Discover (chaddr=MAC_aleatoria)
```

El servidor DHCP no puede distinguir estas solicitudes de las legítimas y responde a cada una completando el ciclo DORA, registrando un binding y consumiendo una IP del pool por transacción. Cuando el pool queda exhausto, cualquier solicitud de un cliente real falla silenciosamente.

> **Nota:** En VPCS/GNS3 el mensaje `Can't find dhcp server` no indica que el servidor sea inalcanzable. El servidor sigue activo pero sin IPs disponibles para asignar.

---

## Entorno de laboratorio

|Dispositivo|Rol|IP|MAC|
|:--|:--|:--|:--|
|R-1|Gateway / DHCP (víctima) / NAT|20.25.6.60/24|0c:16:94:84:00:00|
|PC1|Cliente legítimo|20.25.6.61/24 (DHCP)|00:50:79:66:68:00|
|PC2|Cliente legítimo (agregado luego)|Variable (DHCP)|00:50:79:66:68:01|
|Parrot-1|Atacante|20.25.6.63/24 (DHCP)|0c:db:b8:ad:00:00|
|Sw-1|Switch capa 2|N/A|N/A|

> Red de laboratorio: 20.25.6.0/24. Pool DHCP disponible: 20.25.6.61 a 20.25.6.254 (194 IPs).

---

## Impacto observado

- Pool DHCP completamente agotado en menos de 60 segundos
- El router registra cientos de bindings con MACs falsas desde la .61 hasta la .254
- Nuevos clientes no pueden obtener dirección IP
- Clientes con lease previo mantienen conectividad hasta que su lease expire o lo liberen
- Al liberar una IP existente, esta queda disponible y puede ser tomada por otro cliente

---

## Mitigación

DHCP Snooping con limitación de tasa en el puerto del atacante. Al superar el límite, el switch pone el puerto en `err-disable` automáticamente:

**Puerto confiable (uplink al router):**

```
Switch(config)# ip dhcp snooping
Switch(config)# ip dhcp snooping vlan 1
Switch(config)# no ip dhcp snooping information option
Switch(config)# interface GigabitEthernet1/0
Switch(config-if)# ip dhcp snooping trust
Switch(config-if)# exit
```

**Rate limit en puerto de acceso no confiable:**

```
Switch(config)# interface GigabitEthernet0/0
Switch(config-if)# ip dhcp snooping limit rate 5
Switch(config-if)# exit
```

**Recuperación manual del puerto err-disable:**

```
Switch(config)# interface GigabitEthernet0/0
Switch(config-if)# shutdown
Switch(config-if)# no shutdown
```

---

## Video demostrativo

**Enlace:** [https://youtu.be/j5divLirQGg](https://youtu.be/j5divLirQGg)

---

## Disclaimer

Este script fue desarrollado con fines exclusivamente académicos y educativos. Su uso está permitido únicamente en entornos propios o autorizados como GNS3, EVE-NG o laboratorios internos de prueba. El uso en redes de terceros sin autorización expresa constituye una violación legal.

---

_Randy Nin / Matrícula 2025-0660_
