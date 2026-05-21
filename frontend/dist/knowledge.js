const KNOWLEDGE_BASE = {
    categories: [
        {
            id: "protocol",
            name: "网络协议",
            icon: "P",
            items: [
                {
                    term: "TCP/IP",
                    fullForm: "Transmission Control Protocol/Internet Protocol",
                    description: "TCP/IP是互联网最基本的协议族，定义了电子设备如何连入因特网，以及数据如何在它们之间传输。TCP负责数据传输的可靠性，IP负责数据的路由和寻址。",
                    details: [
                        "TCP提供面向连接的、可靠的数据传输服务",
                        "IP提供无连接的数据报传输服务",
                        "TCP通过三次握手建立连接，四次挥手断开连接",
                        "IP地址分为IPv4（32位）和IPv6（128位）两种"
                    ],
                    relatedTerms: ["三次握手", "四次挥手", "IPv4", "IPv6"]
                },
                {
                    term: "UDP",
                    fullForm: "User Datagram Protocol",
                    description: "UDP是一种无连接的传输层协议，提供面向事务的简单不可靠信息传送服务。与TCP不同，UDP不提供数据包分组、组装和排序，适用于对实时性要求高的场景。",
                    details: [
                        "无连接，发送前不需要建立连接",
                        "不保证可靠交付，不使用拥塞控制",
                        "首部开销小，仅8字节（TCP为20字节）",
                        "适用于实时应用：视频流、语音通话、在线游戏"
                    ],
                    relatedTerms: ["TCP", "QUIC", "实时传输"]
                },
                {
                    term: "HTTP/HTTPS",
                    fullForm: "HyperText Transfer Protocol / HyperText Transfer Protocol Secure",
                    description: "HTTP是应用层协议，是互联网数据通信的基础。HTTPS是HTTP的安全版本，通过TLS/SSL加密传输数据，防止数据被窃听和篡改。",
                    details: [
                        "HTTP默认端口80，HTTPS默认端口443",
                        "HTTP/1.1支持持久连接（Keep-Alive）",
                        "HTTP/2支持多路复用、头部压缩、服务器推送",
                        "HTTP/3基于QUIC协议，使用UDP替代TCP",
                        "HTTPS需要CA证书，提供身份验证和数据加密"
                    ],
                    relatedTerms: ["TLS握手", "SSL证书", "CA证书", "HTTP/2", "HTTP/3"]
                },
                {
                    term: "DNS",
                    fullForm: "Domain Name System",
                    description: "DNS是互联网的\"电话簿\"，将人类可读的域名（如www.example.com）转换为机器可读的IP地址（如93.184.216.34）。DNS采用分层分布式架构。",
                    details: [
                        "DNS查询类型：递归查询和迭代查询",
                        "DNS记录类型：A（IPv4）、AAAA（IPv6）、CNAME（别名）、MX（邮件）、NS（名称服务器）、TXT（文本）",
                        "DNS缓存层级：浏览器缓存 → 操作系统缓存 → 路由器缓存 → ISP DNS缓存",
                        "公共DNS：8.8.8.8（Google）、1.1.1.1（Cloudflare）、223.5.5.5（阿里）",
                        "DNS劫持/污染：攻击者篡改DNS响应，将域名指向错误IP"
                    ],
                    relatedTerms: ["DNS缓存", "DNS劫持", "公共DNS", "DNSSEC"]
                },
                {
                    term: "DHCP",
                    fullForm: "Dynamic Host Configuration Protocol",
                    description: "DHCP是一种网络管理协议，用于自动为网络中的设备分配IP地址、子网掩码、默认网关和DNS服务器等网络配置参数，简化网络管理。",
                    details: [
                        "DHCP四步交互：Discover → Offer → Request → Acknowledge（DORA）",
                        "IP地址租约：DHCP分配的IP有有效期，需要定期续租",
                        "DHCP中继代理：允许跨网段分配IP地址",
                        "常见问题：IP冲突、DHCP服务器不可达、租约过期"
                    ],
                    relatedTerms: ["IP地址", "子网掩码", "默认网关", "IP冲突"]
                },
                {
                    term: "ICMP",
                    fullForm: "Internet Control Message Protocol",
                    description: "ICMP是网络层协议，用于在IP网络中发送控制消息和错误报告。ping和tracert命令就是基于ICMP协议实现的。",
                    details: [
                        "ICMP类型：Echo Request(8)/Reply(0)、Destination Unreachable(3)、Time Exceeded(11)",
                        "ping使用ICMP Echo Request/Reply检测主机可达性",
                        "tracert利用ICMP Time Exceeded消息追踪路由路径",
                        "ICMP Flood是一种DDoS攻击方式"
                    ],
                    relatedTerms: ["Ping", "Traceroute", "DDoS"]
                },
                {
                    term: "ARP",
                    fullForm: "Address Resolution Protocol",
                    description: "ARP协议用于将IP地址解析为MAC地址。在局域网中，设备通信需要知道目标MAC地址，ARP通过广播请求获取IP对应的MAC地址。",
                    details: [
                        "ARP请求以广播方式发送，ARP响应以单播方式返回",
                        "ARP缓存表存储IP-MAC映射关系，有老化时间",
                        "ARP欺骗：攻击者发送伪造的ARP响应，劫持网络流量",
                        "Gratuitous ARP：设备主动广播自己的IP-MAC映射"
                    ],
                    relatedTerms: ["MAC地址", "ARP欺骗", "局域网"]
                },
                {
                    term: "WebSocket",
                    fullForm: "WebSocket Protocol",
                    description: "WebSocket是一种在单个TCP连接上进行全双工通信的协议，使得浏览器和服务器之间可以建立持久性连接，实现实时双向数据传输。",
                    details: [
                        "通过HTTP Upgrade握手建立连接",
                        "连接建立后可双向发送数据，无需重复握手",
                        "适用于实时聊天、在线协作、股票行情等场景",
                        "相比HTTP轮询，大幅降低网络开销和延迟"
                    ],
                    relatedTerms: ["HTTP", "全双工通信", "实时通信"]
                }
            ]
        },
        {
            id: "security",
            name: "网络安全",
            icon: "S",
            items: [
                {
                    term: "TLS握手",
                    fullForm: "Transport Layer Security Handshake",
                    description: "TLS握手是建立安全通信连接的过程，客户端和服务器通过一系列消息交换，协商加密算法、交换密钥、验证证书，最终建立加密通道。",
                    details: [
                        "TLS 1.2握手流程：ClientHello → ServerHello → Certificate → ServerKeyExchange → ClientKeyExchange → ChangeCipherSpec → Finished",
                        "TLS 1.3简化了握手，仅需1-RTT（往返时间），支持0-RTT恢复",
                        "密钥交换算法：RSA、ECDHE（支持前向保密）",
                        "对称加密算法：AES-128-GCM、AES-256-GCM、ChaCha20-Poly1305",
                        "数字证书由CA（证书颁发机构）签发，验证服务器身份",
                        "前向保密（PFS）：即使长期密钥泄露，历史通信也无法解密"
                    ],
                    relatedTerms: ["SSL", "CA证书", "ECDHE", "前向保密", "HTTPS"]
                },
                {
                    term: "SSL/TLS",
                    fullForm: "Secure Sockets Layer / Transport Layer Security",
                    description: "SSL是TLS的前身，两者都是用于在网络上提供通信安全的协议。SSL已被弃用（最新版本SSL 3.0存在安全漏洞），目前广泛使用的是TLS 1.2和TLS 1.3。",
                    details: [
                        "SSL 1.0从未公开发布，SSL 2.0和3.0已被弃用",
                        "TLS 1.0（SSL 3.1）→ TLS 1.1 → TLS 1.2 → TLS 1.3",
                        "TLS 1.3移除了不安全的加密算法和特性",
                        "POODLE攻击针对SSL 3.0，BEAST攻击针对TLS 1.0",
                        "现代浏览器已停止支持SSL 3.0和TLS 1.0/1.1"
                    ],
                    relatedTerms: ["TLS握手", "HTTPS", "CA证书", "加密算法"]
                },
                {
                    term: "CA证书",
                    fullForm: "Certificate Authority Certificate",
                    description: "CA证书是由受信任的证书颁发机构（CA）签发的数字证书，用于验证网站的身份并建立加密连接。浏览器内置了受信任的根证书列表。",
                    details: [
                        "证书类型：DV（域名验证）、OV（组织验证）、EV（扩展验证）",
                        "证书链：终端证书 → 中间CA证书 → 根CA证书",
                        "常见CA：Let's Encrypt（免费）、DigiCert、GlobalSign、Sectigo",
                        "证书包含：公钥、签发者、有效期、域名、签名算法等",
                        "证书吊销：CRL（证书吊销列表）和OCSP（在线证书状态协议）"
                    ],
                    relatedTerms: ["TLS握手", "公钥基础设施", "OCSP", "SSL"]
                },
                {
                    term: "VPN",
                    fullForm: "Virtual Private Network",
                    description: "VPN通过在公共网络上建立加密隧道，实现远程设备安全访问私有网络资源。VPN提供了数据加密、身份验证和访问控制功能。",
                    details: [
                        "VPN协议：IPSec、OpenVPN、WireGuard、L2TP、PPTP",
                        "IPSec：网络层加密，常用于站点间VPN",
                        "OpenVPN：基于TLS的开源VPN，灵活可配置",
                        "WireGuard：现代VPN协议，代码精简、性能优异",
                        "Split Tunneling：分流隧道，选择哪些流量走VPN"
                    ],
                    relatedTerms: ["IPSec", "加密隧道", "WireGuard"]
                },
                {
                    term: "防火墙",
                    fullForm: "Firewall",
                    description: "防火墙是网络安全系统，根据预设规则监控和控制进出网络的流量。防火墙可以是硬件设备或软件程序，是网络安全的第一道防线。",
                    details: [
                        "包过滤防火墙：基于IP、端口、协议过滤数据包",
                        "状态检测防火墙：跟踪连接状态，允许已建立连接的返回流量",
                        "应用层防火墙（WAF）：深度检测应用层数据，防御Web攻击",
                        "Windows防火墙：基于规则的软件防火墙，支持入站/出站规则",
                        "常见配置：默认拒绝、最小权限原则"
                    ],
                    relatedTerms: ["端口", "WAF", "入站规则", "出站规则"]
                },
                {
                    term: "代理服务器",
                    fullForm: "Proxy Server",
                    description: "代理服务器是位于客户端和目标服务器之间的中间服务器，转发客户端请求并返回服务器响应。代理可以提供缓存、过滤、匿名和翻墙等功能。",
                    details: [
                        "正向代理：客户端配置代理，代理替客户端访问目标服务器",
                        "反向代理：客户端直接访问代理，代理转发到后端服务器（如Nginx）",
                        "HTTP代理：处理HTTP/HTTPS流量（如7890端口）",
                        "SOCKS5代理：支持任意协议的代理（如10808端口）",
                        "透明代理：客户端无需配置，网络层自动重定向"
                    ],
                    relatedTerms: ["SOCKS5", "HTTP代理", "反向代理", "Nginx"]
                }
            ]
        },
        {
            id: "hardware",
            name: "网络硬件",
            icon: "H",
            items: [
                {
                    term: "网卡",
                    fullForm: "Network Interface Card (NIC)",
                    description: "网卡是计算机与网络连接的硬件设备，负责将计算机数据转换为网络信号进行传输。每块网卡有唯一的MAC地址。",
                    details: [
                        "有线网卡（以太网卡）：通过RJ45接口连接网线",
                        "无线网卡（Wi-Fi网卡）：通过无线信号连接网络",
                        "MAC地址：48位物理地址，全球唯一（可被修改）",
                        "网卡状态：启用/禁用、速率（10/100/1000Mbps）、双工模式",
                        "虚拟网卡：软件模拟的网卡（如VPN、虚拟机使用的网卡）"
                    ],
                    relatedTerms: ["MAC地址", "以太网", "网线", "双工模式"]
                },
                {
                    term: "路由器",
                    fullForm: "Router",
                    description: "路由器是连接多个网络的设备，根据路由表将数据包转发到目标网络。家用路由器通常集成了交换机、无线AP、NAT和DHCP服务器等功能。",
                    details: [
                        "路由表：存储目标网络和下一跳的映射关系",
                        "NAT（网络地址转换）：将私有IP转换为公网IP",
                        "家用路由器功能：DHCP、Wi-Fi、端口转发、UPnP",
                        "管理地址通常为192.168.1.1或192.168.0.1",
                        "路由协议：静态路由、RIP、OSPF、BGP"
                    ],
                    relatedTerms: ["NAT", "网关", "DHCP", "端口转发"]
                },
                {
                    term: "交换机",
                    fullForm: "Switch",
                    description: "交换机是局域网中连接多台设备的网络设备，根据MAC地址表将数据帧转发到目标端口。与集线器不同，交换机支持全双工通信和独享带宽。",
                    details: [
                        "MAC地址表：记录端口与MAC地址的映射关系",
                        "二层交换机：基于MAC地址转发",
                        "三层交换机：具有路由功能，可基于IP转发",
                        "VLAN：虚拟局域网，将物理网络划分为多个逻辑网络",
                        "STP（生成树协议）：防止网络环路"
                    ],
                    relatedTerms: ["MAC地址", "VLAN", "局域网"]
                },
                {
                    term: "网线",
                    fullForm: "Ethernet Cable",
                    description: "网线是以太网中用于连接网络设备的传输介质。常见的网线类型包括双绞线（Cat5e/Cat6/Cat6a）和光纤。",
                    details: [
                        "Cat5e：超五类线，支持1000Mbps（1Gbps），100米内",
                        "Cat6：六类线，支持10Gbps（55米内），1Gbps（100米内）",
                        "Cat6a：超六类线，支持10Gbps（100米内）",
                        "光纤：单模光纤（长距离）和多模光纤（短距离）",
                        "网线状态指示灯：Link灯（连接状态）、Activity灯（数据传输）"
                    ],
                    relatedTerms: ["以太网", "网卡", "RJ45"]
                }
            ]
        },
        {
            id: "concepts",
            name: "核心概念",
            icon: "C",
            items: [
                {
                    term: "IP地址",
                    fullForm: "Internet Protocol Address",
                    description: "IP地址是分配给网络设备的唯一标识符，用于在网络中定位和通信。IPv4地址为32位，IPv6地址为128位。",
                    details: [
                        "IPv4格式：192.168.1.1（点分十进制）",
                        "IPv6格式：2001:0db8:85a3::8a2e:0370:7334（冒号十六进制）",
                        "私有IP范围：10.0.0.0/8、172.16.0.0/12、192.168.0.0/16",
                        "特殊IP：127.0.0.1（回环）、0.0.0.0（任意地址）、255.255.255.255（广播）",
                        "IP冲突：两台设备使用相同IP地址，导致通信异常",
                        "子网掩码：划分网络位和主机位，如255.255.255.0（/24）"
                    ],
                    relatedTerms: ["子网掩码", "NAT", "DHCP", "IPv6"]
                },
                {
                    term: "子网掩码",
                    fullForm: "Subnet Mask",
                    description: "子网掩码用于划分IP地址的网络部分和主机部分，确定设备是否在同一子网内。同一子网的设备可以直接通信，不同子网需要通过路由器转发。",
                    details: [
                        "CIDR表示法：/24等同于255.255.255.0",
                        "/8 → 255.0.0.0（A类，16,777,216个主机）",
                        "/16 → 255.0.0.0（B类，65,536个主机）",
                        "/24 → 255.255.255.0（C类，254个主机）",
                        "/30 → 255.255.255.252（点对点链路，2个主机）",
                        "子网划分：将大网络划分为多个小子网，提高地址利用率"
                    ],
                    relatedTerms: ["IP地址", "CIDR", "网关", "VLAN"]
                },
                {
                    term: "默认网关",
                    fullForm: "Default Gateway",
                    description: "默认网关是设备访问其他网络（如互联网）时发送数据包的目标地址，通常是路由器的内网IP地址。没有配置网关的设备只能访问本地网络。",
                    details: [
                        "通常为子网的第一个或最后一个可用IP",
                        "常见网关地址：192.168.1.1、192.168.0.1、10.0.0.1",
                        "路由表中的默认路由：0.0.0.0/0 → 网关地址",
                        "网关不可达：设备无法访问外网，但可能仍能访问局域网",
                        "多网关：系统可配置多个网关，通过metric值决定优先级"
                    ],
                    relatedTerms: ["路由器", "路由表", "NAT", "IP地址"]
                },
                {
                    term: "端口",
                    fullForm: "Port",
                    description: "端口是传输层协议中用于区分不同应用程序或服务的逻辑标识，范围0-65535。端口号与IP地址组合形成套接字（Socket），唯一标识一个通信端点。",
                    details: [
                        "知名端口（0-1023）：80(HTTP)、443(HTTPS)、22(SSH)、21(FTP)、53(DNS)、25(SMTP)",
                        "注册端口（1024-49151）：3306(MySQL)、5432(PostgreSQL)、6379(Redis)、8080(HTTP备用)",
                        "动态端口（49152-65535）：客户端临时使用",
                        "常见代理端口：10808(SOCKS5)、7890(HTTP代理)、1080(SOCKS)",
                        "端口状态：LISTEN（监听）、ESTABLISHED（已建立）、TIME_WAIT（等待关闭）"
                    ],
                    relatedTerms: ["Socket", "TCP", "UDP", "防火墙"]
                },
                {
                    term: "NAT",
                    fullForm: "Network Address Translation",
                    description: "NAT是将私有IP地址转换为公网IP地址的技术，解决了IPv4地址不足的问题。家用路由器通过NAT让多台设备共享一个公网IP上网。",
                    details: [
                        "SNAT（源NAT）：内网访问外网时，将源IP替换为公网IP",
                        "DNAT（目的NAT）：外网访问内网时，将目的IP替换为内网IP（端口转发）",
                        "PAT（端口地址转换）：多对一转换，通过端口区分不同连接",
                        "NAT穿透：P2P应用需要穿透NAT，技术有STUN、TURN、ICE",
                        "NAT类型：完全锥形、受限锥形、端口受限锥形、对称型"
                    ],
                    relatedTerms: ["IP地址", "私有IP", "端口转发", "路由器"]
                },
                {
                    term: "MTU",
                    fullForm: "Maximum Transmission Unit",
                    description: "MTU是网络接口一次能传输的最大数据包大小（字节）。以太网标准MTU为1500字节，过大的数据包会被分片，影响传输效率。",
                    details: [
                        "以太网MTU：1500字节（不含以太网帧头）",
                        "PPPoE MTU：1492字节（PPPoE头部占8字节）",
                        "VPN MTU：通常更小（如1400字节），因为VPN封装增加了头部",
                        "MTU过大：数据包被分片，增加延迟和丢包风险",
                        "路径MTU发现（PMTUD）：自动确定路径上最小的MTU",
                        "查看MTU：netsh interface ipv4 show subinterfaces"
                    ],
                    relatedTerms: ["数据包分片", "以太网", "VPN"]
                },
                {
                    term: "CDN",
                    fullForm: "Content Delivery Network",
                    description: "CDN是分布式服务器网络，将内容缓存到全球各地的边缘节点，用户就近获取内容，降低延迟、提高访问速度和可用性。",
                    details: [
                        "工作原理：DNS将域名解析到最近的CDN节点IP",
                        "缓存策略：静态资源长期缓存，动态内容实时回源",
                        "主要厂商：Cloudflare、Akamai、阿里云CDN、腾讯云CDN",
                        "安全功能：DDoS防护、WAF、Bot管理",
                        "CDN刷新：清除缓存，强制回源获取最新内容"
                    ],
                    relatedTerms: ["DNS", "缓存", "负载均衡", "边缘计算"]
                }
            ]
        },
        {
            id: "diagnosis",
            name: "诊断技术",
            icon: "D",
            items: [
                {
                    term: "Ping",
                    fullForm: "Packet Internet Groper",
                    description: "Ping是最基本的网络诊断工具，通过发送ICMP Echo Request消息并等待Echo Reply来测试主机可达性和网络延迟。",
                    details: [
                        "ping 域名/IP：测试连通性",
                        "ping -t：持续ping（Windows），Ctrl+C停止",
                        "ping -n count：发送指定数量的请求",
                        "ping -l size：指定数据包大小",
                        "请求超时：目标不可达或被防火墙拦截",
                        "高延迟：网络拥堵或距离过远",
                        "丢包：网络不稳定或中间设备故障"
                    ],
                    relatedTerms: ["ICMP", "Traceroute", "延迟", "丢包"]
                },
                {
                    term: "Traceroute",
                    fullForm: "Traceroute / Tracert",
                    description: "Traceroute用于追踪数据包从源到目标所经过的路由路径，显示每一跳的IP地址和延迟，帮助定位网络故障点。",
                    details: [
                        "Windows命令：tracert 域名/IP",
                        "Linux/Mac命令：traceroute 域名/IP",
                        "原理：发送递增TTL的ICMP/UDP包，触发中间路由器返回Time Exceeded",
                        "星号(*)：该跳未响应，可能是防火墙禁止ICMP",
                        "延迟突增：该跳可能存在网络拥堵",
                        "路径不对称：去程和回程可能经过不同路由"
                    ],
                    relatedTerms: ["ICMP", "TTL", "路由", "Ping"]
                },
                {
                    term: "Netstat",
                    fullForm: "Network Statistics",
                    description: "Netstat命令显示网络连接、路由表、接口统计等信息，是排查网络连接问题的重要工具。",
                    details: [
                        "netstat -ano：显示所有连接和监听端口（Windows）",
                        "netstat -tulnp：显示TCP/UDP监听端口（Linux）",
                        "LISTENING：端口正在监听等待连接",
                        "ESTABLISHED：连接已建立",
                        "TIME_WAIT：连接已关闭，等待可能的延迟数据包",
                        "CLOSE_WAIT：对方已关闭，本地应用尚未关闭"
                    ],
                    relatedTerms: ["端口", "TCP连接", "Socket"]
                },
                {
                    term: "Nslookup",
                    fullForm: "Name Server Lookup",
                    description: "Nslookup是DNS诊断工具，用于查询DNS记录、验证域名解析是否正确，帮助排查DNS相关问题。",
                    details: [
                        "nslookup 域名：查询域名的A记录",
                        "nslookup -type=MX 域名：查询MX记录",
                        "nslookup -type=CNAME 域名：查询CNAME记录",
                        "nslookup 域名 DNS服务器：指定DNS服务器查询",
                        "交互模式：直接输入nslookup进入",
                        "DNS解析失败：可能是DNS配置错误或DNS服务器故障"
                    ],
                    relatedTerms: ["DNS", "A记录", "CNAME", "MX记录"]
                },
                {
                    term: "Wireshark",
                    fullForm: "Wireshark Network Protocol Analyzer",
                    description: "Wireshark是最流行的网络协议分析器，可以捕获和交互式浏览网络流量，深入分析网络通信的每个数据包。",
                    details: [
                        "捕获过滤器：基于BPF语法过滤捕获的流量",
                        "显示过滤器：基于协议、IP、端口等过滤显示",
                        "TCP流追踪：重组TCP流，查看完整会话内容",
                        "TLS解密：配置密钥日志文件可解密HTTPS流量",
                        "常见用途：排查网络延迟、分析协议行为、安全审计"
                    ],
                    relatedTerms: ["数据包捕获", "协议分析", "TCP流"]
                },
                {
                    term: "Telnet",
                    fullForm: "Telnet Protocol",
                    description: "Telnet常用于测试TCP端口连通性。虽然Telnet协议本身已不安全（明文传输），但telnet命令仍是快速检测端口是否开放的有效工具。",
                    details: [
                        "telnet IP 端口：测试指定IP的端口是否开放",
                        "连接成功：端口开放，服务正在运行",
                        "连接失败：端口关闭或被防火墙拦截",
                        "替代工具：nc（netcat）、Test-NetConnection（PowerShell）",
                        "PowerShell: Test-NetConnection -ComputerName IP -Port 端口"
                    ],
                    relatedTerms: ["端口", "TCP", "防火墙"]
                }
            ]
        },
        {
            id: "encryption",
            name: "加密技术",
            icon: "E",
            items: [
                {
                    term: "对称加密",
                    fullForm: "Symmetric Encryption",
                    description: "对称加密使用相同的密钥进行加密和解密。优点是速度快，缺点是密钥分发困难。常用于大量数据的加密传输。",
                    details: [
                        "AES-128/AES-256：目前最广泛使用的对称加密算法",
                        "ChaCha20：Google推荐的流加密算法，移动端性能优异",
                        "分组模式：CBC、CTR、GCM（推荐，提供认证加密）",
                        "密钥长度：128位（安全）、192位、256位（高安全）",
                        "应用场景：TLS数据传输、文件加密、磁盘加密"
                    ],
                    relatedTerms: ["AES", "TLS握手", "非对称加密"]
                },
                {
                    term: "非对称加密",
                    fullForm: "Asymmetric Encryption",
                    description: "非对称加密使用一对密钥：公钥加密、私钥解密（或反之）。解决了密钥分发问题，但速度比对称加密慢得多。",
                    details: [
                        "RSA：最经典的非对称加密算法，基于大数分解难题",
                        "ECC（椭圆曲线加密）：更短的密钥达到同等安全强度",
                        "Ed25519：基于扭曲Edwards曲线的签名算法，性能优异",
                        "公钥：公开分发，用于加密或验证签名",
                        "私钥：严格保密，用于解密或生成签名",
                        "应用：TLS密钥交换、SSH认证、数字签名"
                    ],
                    relatedTerms: ["RSA", "ECC", "TLS握手", "数字签名"]
                },
                {
                    term: "数字签名",
                    fullForm: "Digital Signature",
                    description: "数字签名使用发送方的私钥对消息摘要进行签名，接收方用公钥验证。确保消息的完整性、真实性和不可否认性。",
                    details: [
                        "签名过程：消息 → 哈希 → 私钥加密 → 签名",
                        "验证过程：签名 → 公钥解密 → 对比哈希",
                        "哈希算法：SHA-256、SHA-384、SHA-512",
                        "应用：SSL证书签名、代码签名、文档签名",
                        "与MAC的区别：数字签名提供不可否认性，MAC不提供"
                    ],
                    relatedTerms: ["哈希算法", "CA证书", "非对称加密"]
                },
                {
                    term: "哈希算法",
                    fullForm: "Hash Algorithm",
                    description: "哈希算法将任意长度的数据映射为固定长度的摘要值。具有单向性（不可逆）和抗碰撞性，广泛用于数据完整性验证和密码存储。",
                    details: [
                        "MD5：128位，已被证明不安全，存在碰撞攻击",
                        "SHA-1：160位，已被弃用，2017年首次实现碰撞攻击",
                        "SHA-256：256位，目前广泛使用，TLS 1.3推荐",
                        "SHA-3：新一代哈希标准，基于Keccak算法",
                        "应用：文件校验、密码存储（加盐哈希）、区块链、数字签名"
                    ],
                    relatedTerms: ["数字签名", "完整性校验", "MD5", "SHA-256"]
                }
            ]
        },
        {
            id: "wireless",
            name: "无线网络",
            icon: "W",
            items: [
                {
                    term: "Wi-Fi",
                    fullForm: "Wireless Fidelity",
                    description: "Wi-Fi是基于IEEE 802.11标准的无线局域网技术，允许设备通过无线信号连接网络。Wi-Fi已成为最普及的无线联网方式。",
                    details: [
                        "Wi-Fi 4 (802.11n)：2.4/5GHz，最高600Mbps",
                        "Wi-Fi 5 (802.11ac)：5GHz，最高6.9Gbps",
                        "Wi-Fi 6 (802.11ax)：2.4/5GHz，最高9.6Gbps，支持OFDMA",
                        "Wi-Fi 6E：扩展到6GHz频段，更多信道",
                        "Wi-Fi 7 (802.11be)：2.4/5/6GHz，最高46Gbps，支持MLO",
                        "2.4GHz：覆盖范围大，速度慢，干扰多",
                        "5GHz：覆盖范围小，速度快，干扰少"
                    ],
                    relatedTerms: ["WPA3", "信道", "频段"]
                },
                {
                    term: "WPA3",
                    fullForm: "Wi-Fi Protected Access 3",
                    description: "WPA3是Wi-Fi最新的安全协议，相比WPA2提供了更强的安全保护，包括对离线字典攻击的防护和前向保密。",
                    details: [
                        "WPA3-Personal：使用SAE（对等同步认证）替代PSK",
                        "WPA3-Enterprise：192位加密套件，更高安全级别",
                        "SAE：防止离线字典攻击，即使密码简单也安全",
                        "前向保密：即使密码泄露，历史流量也无法解密",
                        "WPA2/WPA3过渡模式：兼容旧设备"
                    ],
                    relatedTerms: ["Wi-Fi", "加密", "前向保密"]
                },
                {
                    term: "信道",
                    fullForm: "Wi-Fi Channel",
                    description: "Wi-Fi信道是无线信号传输的频率范围。2.4GHz频段有14个信道（中国可用1-13），5GHz频段有更多非重叠信道。",
                    details: [
                        "2.4GHz：1-13信道，仅1/6/11互不重叠",
                        "5GHz：36-165信道，多个非重叠信道",
                        "信道宽度：20MHz、40MHz、80MHz、160MHz",
                        "信道干扰：相邻信道重叠导致干扰，影响性能",
                        "信道选择：建议使用Wi-Fi分析工具选择干扰最小的信道"
                    ],
                    relatedTerms: ["Wi-Fi", "频段", "干扰"]
                }
            ]
        },
        {
            id: "tools",
            name: "实用工具",
            icon: "T",
            items: [
                {
                    term: "ipconfig",
                    fullForm: "IP Configuration (Windows)",
                    description: "ipconfig是Windows系统中最常用的网络配置查看和调试命令，可以查看IP地址、刷新DNS、释放/续租IP等。",
                    details: [
                        "ipconfig：显示基本网络配置",
                        "ipconfig /all：显示详细配置（含MAC地址、DHCP信息）",
                        "ipconfig /flushdns：清除DNS缓存",
                        "ipconfig /release：释放DHCP分配的IP地址",
                        "ipconfig /renew：重新获取IP地址",
                        "ipconfig /displaydns：显示DNS缓存内容"
                    ],
                    relatedTerms: ["DNS缓存", "DHCP", "IP地址"]
                },
                {
                    term: "netsh",
                    fullForm: "Network Shell (Windows)",
                    description: "netsh是Windows强大的网络配置命令行工具，可以管理网络接口、防火墙、代理、Winsock等几乎所有网络设置。",
                    details: [
                        "netsh winsock reset：重置Winsock目录（修复网络异常）",
                        "netsh int ip reset：重置TCP/IP协议栈",
                        "netsh advfirewall：管理Windows防火墙规则",
                        "netsh wlan show profiles：查看已保存的Wi-Fi配置",
                        "netsh interface set proxy：配置系统代理",
                        "netsh interface ipv4 show subinterfaces：查看MTU设置"
                    ],
                    relatedTerms: ["Winsock", "防火墙", "TCP/IP"]
                },
                {
                    term: "hosts文件",
                    fullForm: "Hosts File",
                    description: "hosts文件是操作系统的本地DNS解析文件，优先级高于DNS服务器。可以将域名映射到指定IP，用于屏蔽网站或本地开发测试。",
                    details: [
                        "Windows路径：C:\\Windows\\System32\\drivers\\etc\\hosts",
                        "Linux/Mac路径：/etc/hosts",
                        "格式：IP地址 域名（如 127.0.0.1 localhost）",
                        "优先级：hosts文件 > DNS缓存 > DNS服务器",
                        "常见用途：屏蔽广告（0.0.0.0 广告域名）、本地开发、绕过DNS污染",
                        "修改后需刷新DNS缓存：ipconfig /flushdns"
                    ],
                    relatedTerms: ["DNS", "本地解析", "DNS缓存"]
                },
                {
                    term: "Git网络配置",
                    fullForm: "Git Network Configuration",
                    description: "Git支持配置HTTP/HTTPS代理和SSL验证，在代理环境下使用Git需要正确配置代理设置，否则可能导致克隆、推送等操作失败。",
                    details: [
                        "git config --global http.proxy 127.0.0.1:7890：设置HTTP代理",
                        "git config --global https.proxy 127.0.0.1:7890：设置HTTPS代理",
                        "git config --global --unset http.proxy：取消HTTP代理",
                        "git config --global http.sslVerify false：禁用SSL验证（不推荐）",
                        "git config --global http.sslVerify true：启用SSL验证（推荐）",
                        "SSH代理：在~/.ssh/config中配置ProxyCommand"
                    ],
                    relatedTerms: ["代理服务器", "SSL", "HTTPS"]
                }
            ]
        },
        {
            id: "troubleshooting",
            name: "故障排查",
            icon: "F",
            items: [
                {
                    term: "无法上网",
                    fullForm: "Internet Connectivity Failure",
                    description: "最常见的网络故障，表现为完全无法访问任何网站。需要从物理层到应用层逐层排查：网线→网卡→IP配置→DNS→网关→代理→防火墙。",
                    details: [
                        "第一步：检查网线/WiFi连接是否正常，网卡是否启用",
                        "第二步：ipconfig查看IP地址，是否获取到有效IP（非169.254.x.x）",
                        "第三步：ping网关地址，检查局域网连通性",
                        "第四步：ping 8.8.8.8，检查外网连通性",
                        "第五步：nslookup测试DNS解析是否正常",
                        "第六步：检查代理设置和防火墙规则",
                        "终极方案：netsh winsock reset + ipconfig /flushdns + 重启"
                    ],
                    relatedTerms: ["Ping", "DNS", "网关", "Winsock"]
                },
                {
                    term: "DNS解析失败",
                    fullForm: "DNS Resolution Failure",
                    description: "能ping通IP地址但无法访问域名，说明DNS解析出现问题。可能原因包括DNS服务器不可达、DNS缓存错误、hosts文件配置异常等。",
                    details: [
                        "症状：ping IP正常但ping域名失败",
                        "原因1：DNS服务器不可达或响应慢",
                        "原因2：DNS缓存被污染或过期",
                        "原因3：hosts文件有错误配置",
                        "原因4：DNS劫持或ISP DNS故障",
                        "修复：ipconfig /flushdns → 更换DNS为223.5.5.5或8.8.8.8 → 检查hosts文件"
                    ],
                    relatedTerms: ["DNS缓存", "公共DNS", "hosts文件", "DNS劫持"]
                },
                {
                    term: "IP地址冲突",
                    fullForm: "IP Address Conflict",
                    description: "网络中两台设备使用了相同的IP地址，导致通信异常。通常由手动设置静态IP与DHCP分配的IP重叠引起。",
                    details: [
                        "症状：系统提示\"IP地址冲突\"，网络时断时续",
                        "原因1：手动设置静态IP与DHCP地址池重叠",
                        "原因2：DHCP服务器分配了重复IP",
                        "原因3：设备休眠后IP被分配给其他设备",
                        "修复：ipconfig /release → ipconfig /renew → 或更换静态IP",
                        "预防：在路由器DHCP设置中预留静态IP范围"
                    ],
                    relatedTerms: ["DHCP", "静态IP", "IP地址"]
                },
                {
                    term: "WiFi频繁断连",
                    fullForm: "WiFi Intermittent Disconnection",
                    description: "WiFi连接不稳定，频繁断开重连。可能原因包括信号弱、信道干扰、驱动问题、路由器设置不当等。",
                    details: [
                        "原因1：信号强度不足（<50%），距离路由器过远",
                        "原因2：2.4GHz信道拥挤，周围太多WiFi网络",
                        "原因3：路由器信道自动选择导致频繁切换",
                        "原因4：网卡驱动过旧或电源管理关闭了适配器",
                        "原因5：路由器固件bug或过载",
                        "修复：靠近路由器 → 切换5GHz → 更新驱动 → 固定信道 → 重置适配器"
                    ],
                    relatedTerms: ["WiFi信号", "信道", "5GHz", "网络适配器"]
                },
                {
                    term: "网关不可达",
                    fullForm: "Gateway Unreachable",
                    description: "无法连接到默认网关，导致无法访问外部网络。可能原因包括网关设备故障、路由配置错误、ARP表异常等。",
                    details: [
                        "症状：ping网关地址超时或返回\"目标主机不可达\"",
                        "原因1：路由器/网关设备故障或重启中",
                        "原因2：本机路由表配置错误",
                        "原因3：ARP缓存中网关MAC地址错误",
                        "原因4：VLAN配置错误导致不在同一网段",
                        "修复：检查路由器 → route print查看路由表 → arp -d *清除ARP缓存 → netsh winsock reset"
                    ],
                    relatedTerms: ["网关", "路由表", "ARP", "VLAN"]
                },
                {
                    term: "代理配置异常",
                    fullForm: "Proxy Configuration Error",
                    description: "系统或应用配置了代理但代理服务不可用，导致无法上网。常见于使用VPN/代理软件后未正确关闭。",
                    details: [
                        "症状：浏览器显示代理服务器拒绝连接",
                        "原因1：代理软件已关闭但系统代理未清除",
                        "原因2：Git配置了代理但代理端口未监听",
                        "原因3：环境变量HTTP_PROXY/HTTPS_PROXY残留",
                        "修复：关闭系统代理 → git config --global --unset http.proxy → 清除环境变量",
                        "预防：使用代理软件的\"系统代理\"自动切换功能"
                    ],
                    relatedTerms: ["代理服务器", "系统代理", "Git代理"]
                },
                {
                    term: "MTU问题",
                    fullForm: "Maximum Transmission Unit Issue",
                    description: "MTU设置不当导致数据包分片或被丢弃，表现为部分网站可以访问但某些网站无法加载，或大文件传输失败。",
                    details: [
                        "标准以太网MTU：1500字节",
                        "PPPoE连接MTU：1492字节（需减去PPPoE头8字节）",
                        "VPN隧道MTU：通常更小（1400左右）",
                        "症状：小数据正常但大数据传输失败，网页加载不完整",
                        "诊断：ping -f -l 1472 目标地址（逐步减小测试）",
                        "修复：netsh interface ipv4 set subinterface \"以太网\" mtu=1500 store=persistent"
                    ],
                    relatedTerms: ["数据包分片", "PPPoE", "VPN"]
                },
                {
                    term: "防火墙阻断",
                    fullForm: "Firewall Blocking",
                    description: "防火墙规则过于严格或配置错误，阻止了正常的网络通信。可能表现为特定端口无法访问、特定程序无法联网等。",
                    details: [
                        "症状：某些程序无法联网但其他正常",
                        "原因1：Windows防火墙阻止了程序的网络访问",
                        "原因2：第三方安全软件拦截了网络请求",
                        "原因3：出站规则阻止了特定端口的通信",
                        "诊断：临时关闭防火墙测试 → netsh advfirewall show allprofiles state",
                        "修复：添加防火墙例外 → netsh advfirewall firewall add rule → 重新启用防火墙"
                    ],
                    relatedTerms: ["防火墙", "端口", "安全策略"]
                },
                {
                    term: "网络延迟高",
                    fullForm: "High Network Latency",
                    description: "网络响应缓慢，延迟过高。可能原因包括网络拥堵、路由不佳、DNS解析慢、无线信号干扰等。",
                    details: [
                        "诊断：ping测试延迟 → tracert查看路由节点延迟",
                        "原因1：ISP网络拥堵或路由不佳",
                        "原因2：DNS解析慢（使用远程DNS服务器）",
                        "原因3：WiFi信号干扰或信道拥挤",
                        "原因4：后台程序占用带宽",
                        "原因5：MTU设置不当导致分片重传",
                        "优化：更换DNS → 切换5GHz WiFi → 关闭后台下载 → 检查MTU设置"
                    ],
                    relatedTerms: ["Ping", "Traceroute", "DNS", "MTU"]
                },
                {
                    term: "SSL证书错误",
                    fullForm: "SSL/TLS Certificate Error",
                    description: "访问HTTPS网站时出现证书错误，可能由证书过期、证书不受信任、系统时间错误、中间人攻击等原因导致。",
                    details: [
                        "常见错误：NET::ERR_CERT_DATE_INVALID（证书过期）",
                        "常见错误：NET::ERR_CERT_AUTHORITY_INVALID（证书不受信任）",
                        "原因1：系统时间不正确导致证书验证失败",
                        "原因2：根证书存储中缺少CA根证书",
                        "原因3：Git的http.sslVerify被设为false",
                        "原因4：企业防火墙进行SSL解密（中间人）",
                        "修复：校正系统时间 → 更新根证书 → git config --global http.sslVerify true"
                    ],
                    relatedTerms: ["TLS握手", "CA证书", "SSL验证", "HTTPS"]
                }
            ]
        },
        {
            id: "advanced",
            name: "高级概念",
            icon: "A",
            items: [
                {
                    term: "NAT",
                    fullForm: "Network Address Translation",
                    description: "网络地址转换，将私有IP地址转换为公网IP地址的技术。解决IPv4地址不足问题，同时隐藏内部网络结构，提供一定安全性。",
                    details: [
                        "SNAT（源地址转换）：内网访问外网时，将源IP替换为公网IP",
                        "DNAT（目的地址转换）：外网访问内网时，将目的IP替换为内网IP",
                        "PAT（端口地址转换）：多台设备共享一个公网IP，通过端口区分",
                        "NAT类型：Full Cone、Restricted Cone、Port Restricted Cone、Symmetric",
                        "NAT穿透：STUN、TURN、ICE等协议解决NAT后的P2P通信"
                    ],
                    relatedTerms: ["IPv4", "私有IP", "公网IP", "端口映射"]
                },
                {
                    term: "CDN",
                    fullForm: "Content Delivery Network",
                    description: "内容分发网络，通过在全球各地部署缓存节点，将内容推送到离用户最近的服务器，加速网页加载和内容传输。",
                    details: [
                        "核心原理：将内容缓存到边缘节点，用户就近获取",
                        "DNS智能解析：根据用户位置返回最近的节点IP",
                        "缓存策略：强缓存（Cache-Control）和协商缓存（ETag）",
                        "常见CDN：Cloudflare、Akamai、阿里云CDN、腾讯云CDN",
                        "CDN回源：缓存未命中时，边缘节点向源站请求内容"
                    ],
                    relatedTerms: ["DNS", "缓存", "负载均衡", "边缘计算"]
                },
                {
                    term: "VLAN",
                    fullForm: "Virtual Local Area Network",
                    description: "虚拟局域网，将物理网络划分为多个逻辑网络，提高网络安全性和管理灵活性。不同VLAN之间需要路由才能通信。",
                    details: [
                        "基于端口划分：最常用的VLAN划分方式",
                        "基于MAC地址划分：根据设备MAC地址分配VLAN",
                        "IEEE 802.1Q：VLAN标签标准，在以太网帧中插入4字节标签",
                        "VLAN间路由：需要三层交换机或路由器实现VLAN间通信",
                        "VLAN隔离：不同VLAN的二层流量相互隔离"
                    ],
                    relatedTerms: ["局域网", "交换机", "路由", "网络隔离"]
                },
                {
                    term: "QoS",
                    fullForm: "Quality of Service",
                    description: "服务质量，网络中为不同类型的流量提供不同优先级和带宽保障的机制。确保关键应用（如VoIP、视频会议）在网络拥堵时仍能获得足够资源。",
                    details: [
                        "流量分类：根据协议、端口、IP地址等识别流量类型",
                        "流量标记：DSCP（差分服务代码点）标记数据包优先级",
                        "队列调度：优先队列（PQ）、加权公平队列（WFQ）等",
                        "流量整形：令牌桶算法控制流量速率",
                        "应用场景：VoIP优先、视频会议保障、大文件传输限速"
                    ],
                    relatedTerms: ["带宽", "延迟", "丢包率", "流量控制"]
                },
                {
                    term: "BGP",
                    fullForm: "Border Gateway Protocol",
                    description: "边界网关协议，是互联网的核心路由协议，负责在不同自治系统（AS）之间交换路由信息。BGP决定了数据包如何在互联网中传输。",
                    details: [
                        "AS（自治系统）：由单一组织管理的IP网络集合",
                        "eBGP：不同AS之间的BGP会话",
                        "iBGP：同一AS内部的BGP会话",
                        "BGP路由选择：基于AS路径长度、策略等属性",
                        "BGP劫持：攻击者发布虚假路由，将流量导向错误目的地"
                    ],
                    relatedTerms: ["路由", "AS", "路由表", "互联网"]
                },
                {
                    term: "Zero Trust",
                    fullForm: "Zero Trust Network Architecture",
                    description: "零信任网络架构，一种安全理念：不信任任何内部或外部的网络连接，所有访问请求都需要经过身份验证和授权。",
                    details: [
                        "核心原则：永不信任，始终验证",
                        "最小权限：只授予完成工作所需的最小访问权限",
                        "微分段：将网络划分为细粒度的安全区域",
                        "持续验证：每次访问都进行身份和设备验证",
                        "实现技术：SDP（软件定义边界）、ZTNA（零信任网络访问）"
                    ],
                    relatedTerms: ["防火墙", "VPN", "身份验证", "网络安全"]
                }
            ]
        }
    ]
};
