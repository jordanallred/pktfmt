"""Built-in protocol definitions for common network protocols."""

from typing import Dict, List, Tuple

# Protocol definitions: (description, field_spec)
# field_spec is in the inline format "Name:bits,Name:bits,..."
PROTOCOLS: Dict[str, Tuple[str, str]] = {
    # Layer 2
    "ethernet": (
        "Ethernet II Frame",
        "Destination MAC:48,Source MAC:48,EtherType:16,Payload:*"
    ),
    "8021q": (
        "IEEE 802.1Q VLAN Tag",
        "Destination MAC:48,Source MAC:48,TPID:16,PCP:3,DEI:1,VLAN ID:12,EtherType:16,Payload:*"
    ),
    "arp": (
        "Address Resolution Protocol",
        "Hardware Type:16,Protocol Type:16,HW Addr Len:8,Proto Addr Len:8,Operation:16,Sender HW Addr:48,Sender Proto Addr:32,Target HW Addr:48,Target Proto Addr:32"
    ),

    # Layer 3
    "ipv4": (
        "Internet Protocol version 4",
        "Version:4,IHL:4,DSCP:6,ECN:2,Total Length:16,Identification:16,Flags:3,Fragment Offset:13,TTL:8,Protocol:8,Header Checksum:16,Source Address:32,Destination Address:32,Options:*"
    ),
    "ip": (
        "Internet Protocol version 4 (alias)",
        "Version:4,IHL:4,DSCP:6,ECN:2,Total Length:16,Identification:16,Flags:3,Fragment Offset:13,TTL:8,Protocol:8,Header Checksum:16,Source Address:32,Destination Address:32,Options:*"
    ),
    "ipv6": (
        "Internet Protocol version 6",
        "Version:4,Traffic Class:8,Flow Label:20,Payload Length:16,Next Header:8,Hop Limit:8,Source Address:128,Destination Address:128"
    ),
    "icmp": (
        "Internet Control Message Protocol",
        "Type:8,Code:8,Checksum:16,Rest of Header:32,Data:*"
    ),
    "icmpv6": (
        "ICMPv6",
        "Type:8,Code:8,Checksum:16,Message Body:*"
    ),

    # Layer 4
    "tcp": (
        "Transmission Control Protocol",
        "Source Port:16,Destination Port:16,Sequence Number:32,Acknowledgment Number:32,Data Offset:4,Reserved:3,Flags:9,Window Size:16,Checksum:16,Urgent Pointer:16,Options:*"
    ),
    "udp": (
        "User Datagram Protocol",
        "Source Port:16,Destination Port:16,Length:16,Checksum:16,Data:*"
    ),
    "sctp": (
        "Stream Control Transmission Protocol",
        "Source Port:16,Destination Port:16,Verification Tag:32,Checksum:32,Chunks:*"
    ),

    # Application Layer
    "dns": (
        "Domain Name System Header",
        "Transaction ID:16,Flags:16,Questions:16,Answer RRs:16,Authority RRs:16,Additional RRs:16,Data:*"
    ),
    "dhcp": (
        "Dynamic Host Configuration Protocol",
        "Op:8,HType:8,HLen:8,Hops:8,Transaction ID:32,Seconds:16,Flags:16,Client IP:32,Your IP:32,Server IP:32,Gateway IP:32,Client HW Addr:128,Server Name:512,Boot Filename:1024,Options:*"
    ),

    # Tunneling
    "gre": (
        "Generic Routing Encapsulation",
        "C:1,R:1,K:1,S:1,s:1,Recur:3,A:1,Flags:4,Version:3,Protocol Type:16,Payload:*"
    ),
    "vxlan": (
        "Virtual Extensible LAN",
        "Flags:8,Reserved:24,VNI:24,Reserved:8,Payload:*"
    ),

    # Industrial / ICS
    "modbus": (
        "Modbus TCP",
        "Transaction ID:16,Protocol ID:16,Length:16,Unit ID:8,Function Code:8,Data:*"
    ),
    "dnp3": (
        "DNP3 Data Link Layer",
        "Start:16,Length:8,Control:8,Destination:16,Source:16,CRC:16,Data:*"
    ),

    # Other
    "ntp": (
        "Network Time Protocol",
        "LI:2,VN:3,Mode:3,Stratum:8,Poll:8,Precision:8,Root Delay:32,Root Dispersion:32,Reference ID:32,Reference Timestamp:64,Origin Timestamp:64,Receive Timestamp:64,Transmit Timestamp:64"
    ),
    "tls": (
        "TLS Record",
        "Content Type:8,Version:16,Length:16,Payload:*"
    ),
    "quic": (
        "QUIC Long Header",
        "Header Form:1,Fixed Bit:1,Long Packet Type:2,Reserved:2,Packet Number Length:2,Version:32,DCID Len:8,DCID:*"
    ),
}


def get_protocol(name: str) -> Tuple[str, str]:
    """Get a protocol definition by name.

    Args:
        name: Protocol name (case-insensitive)

    Returns:
        Tuple of (description, field_spec)

    Raises:
        KeyError: If protocol not found
    """
    name_lower = name.lower()
    if name_lower not in PROTOCOLS:
        raise KeyError(f"Unknown protocol: '{name}'. Use --list to see available protocols.")
    return PROTOCOLS[name_lower]


def list_protocols() -> List[Tuple[str, str]]:
    """Get list of all available protocols.

    Returns:
        List of (name, description) tuples, sorted by name
    """
    return sorted([(name, desc) for name, (desc, _) in PROTOCOLS.items()])


def is_protocol(name: str) -> bool:
    """Check if a name is a known protocol.

    Args:
        name: Protocol name to check

    Returns:
        True if it's a known protocol name
    """
    return name.lower() in PROTOCOLS
