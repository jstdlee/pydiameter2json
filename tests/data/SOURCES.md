# Sources of the real-capture samples

`real_captures.json` holds five Diameter messages. Each message is one frame
from a public pcapng file. The hex is the Diameter payload only (no IP, TCP or
SCTP headers). Frame numbers are the frame numbers in the capture.

| Id | Source file | Frame | Content |
|----|-------------|-------|---------|
| magma-gx-gy-05-frame2 | gx_gy_combined_05_210505_133111-1.pcapng | 2 | Device-Watchdog-Answer |
| magma-gx-gy-05-frame16 | same | 16 | S6a Authentication-Information-Request |
| magma-gx-gy-05-frame17 | same | 17 | S6a Authentication-Information-Answer |
| magma-gx-gy-05-frame121 | same | 121 | Gx CCR with Framed-IP-Address |
| magma-gx-gy-05-frame32 | same | 32 | Gx CCR with Framed-IP, 3GPP-SGSN and 3GPP-GGSN addresses |

Source URL:
https://github.com/magma/magma/raw/master/docs/readmes/assets/feg/pcaps/gx_gy_combined_05_210505_133111-1.pcapng
(repository https://github.com/magma/magma, path `docs/readmes/assets/feg/pcaps/`).

Licence: BSD 3-Clause, "Copyright (c) 2020, The Magma Authors"
(https://github.com/magma/magma/blob/master/LICENSE). The copyright notice and
licence terms apply to these derived samples. The identifiers inside the
messages (IMSI 999991234567810, hosts under magma.com) are lab test values.

## How the samples were checked

The messages were dissected with tshark 4.x (PDML). For about 1,700 messages
from the Magma, open5gs and nDPI captures, the AVP code, flags, vendor ID,
length, raw bytes and order matched in every AVP, including grouped children.
The value differences that were found, and fixed here, are the IPv4 and IPv6
address AVPs (`Framed-IP-Address`, `3GPP-SGSN-Address`, `3GPP-GGSN-Address`).

Other captures were checked but are not copied here, because their licence
is unclear or restrictive:

- https://github.com/ntop/nDPI `tests/cfgs/default/pcap/diameter.pcap` (LGPL-3.0)
- https://github.com/open5gs/open5gs `docs/assets/pcapng/volte.pcapng` (AGPL-3.0)
