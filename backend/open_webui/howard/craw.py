import logging
import sys
from open_webui.env import SRC_LOG_LEVELS
from bs4 import BeautifulSoup, NavigableString, Tag
from playwright.async_api import async_playwright
import time
import json
import re
import open_webui.howard.debugTools as zijin


log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])
# don't use it... horrible
# query="?q=d:1.days.ago.."

def log_color(d):
    log.info(f"\n\n\033[0;33m{d}\033[0m\n\n")

class Crawler:
    def __init__(self):
        self.browser = None
        self.context = None
        self.p = None

    async def check(self):
        if self.browser == None or self.context == None:
            self.p = await async_playwright().start()
            self.browser = await self.p.chromium.launch(headless=False)
            self.context = await self.browser.new_context()

    async def get_thread_links_under_sub_archive(self, sub_archive_url):
        """ 
        Obtain all mails links under a sub-archive page.
        Args: 
            sub_archive_url: The URL of the sub-archive page, such as "https://lore.kernel.org/linux-perf-users/". 
        Returns: 
            a list of tuples (url, title). 
        """

        # Use BeautifulSoup to parse the HTML
        # url = sub_archive_url + query
        url = sub_archive_url
        print(f"🌐 Loading sub-archive page: {url}")
        page = await self.context.new_page()
        await page.goto(url, wait_until="domcontentloaded")
        # Wait until the <pre> tags appear. 
        await page.wait_for_selector(selector = "pre", timeout=60000)  
        html = await page.content()

        soup = BeautifulSoup(html, 'html.parser')

        # All the mails links are under the first <pre> tag directly under <body>. 
        pres = soup.select('body > pre')

        zijin.output_to_file(str(pres) + '\n', filename='log.txt', mode='a')

        if pres:
            pre = pres[0]
            # link_soup = BeautifulSoup(pre.encode_contents(), 'html.parser')
            links = []

            # contents = pre.contents
            
            anchors = pre.find_all('a', href=True)

            cnt = 0

            # @change
            # Only select those anchors that are not after '`'
            for anchor in anchors: 
                previous = anchor.previous_sibling

                if previous and isinstance(previous, NavigableString):
                    if previous.strip().endswith('`'):
                        # skip this link
                        cnt += 1
                        continue  

                href = anchor['href']
                url = href if href.startswith('http') else sub_archive_url + href
                # url = url + 'T/#t'
                title = anchor.get_text(strip=True)
                links.append((url, title))            

            # print(f"✅ Found {len(links)} links in <pre> block.")
            log_color(f"✅ Found {len(links)} links in <pre> block.")
            zijin.output_to_file('\n' + sub_archive_url + '\n', filename='log.txt', mode='a')
            zijin.output_to_file(f"✅ Found {len(links)} links in <pre> block.\n", filename='log.txt', mode='a')
            zijin.output_to_file(f"sub links: {cnt}\n", filename='log.txt', mode='a')

            # @debug
            # for url, title in links: 
            #     zijin.output_to_file(f'{url}: {title}\n', filename='log.txt', mode='a')
            
            return links

        else:
            print("❌ No <pre> block found.", file=sys.stderr)

        return None


    async def get_emails_under_thread(self, thread_url): 
        """ 
        Obtain a list of emails (stored in string) under given thread page. 
        Args: 
            thread_url: The URL of the thread page. 
        Returns: 
            A list of emails (stored in string).
        """

        page = await self.context.new_page()
        print(f"🌐 Loading thread page: {thread_url}")
        # page.goto(thread_url, timeout=60000)
        await page.goto(thread_url, wait_until="domcontentloaded")
        # Wait until the <pre> tags appear. 
        await page.wait_for_selector(selector = "pre", timeout=60000)  
        html = await page.content()

        # Parse the HTML
        soup = BeautifulSoup(html, "html.parser")

        # Extract all <pre> tags directly under <body>. One email per <pre> tag. (Except for the last one)
        pre_tags = soup.select("body > pre")

        email_content_list = []
        # @change
        # We only select the first email under this thread. 
        pre = pre_tags[0]

        lines = (pre.text + "\n").splitlines()

        # Remove all content after the last row with only '--'
        cutoff_index = None
        for i in reversed(range(len(lines))):
            if lines[i].strip() == "--":
                cutoff_index = i
                break 

        if cutoff_index is not None:
            lines = lines[:cutoff_index]

        # content = str.join("\n", lines)
        content = '\n'.join(lines)
        # zijin.output_to_file(str(isinstance(content, str))+'\n', mode='a')
        content = await self.extract_email_body(email=content)
        email_content_list.append(content)

        return email_content_list

    async def extract_email_body(self, email: str): 
        """
        Extract the body part of an email (represented as a string). 
        @Still construct
        """

        # Normalize line endings
        normalized = email.replace('\r\n', '\n').replace('\r', '\n')
        # normalized = email
        # Initial the return variable. 
        body = normalized

        # Cut off the header. 
        # Find the position of the first 'From:' line
        from_index = normalized.find('From:')
        if from_index != -1:
            # If we can find one 'From:' in the email. A normal email header should include this. 
            # Search for first '\n\n' after 'From:'
            header_end_index = normalized.find('\n\n', from_index)
            if header_end_index != -1:
                # Extract body starting after the blank line
                body = normalized[header_end_index + 2:]

        body = await self.cutoff_email_body_end(body)
        # @debug: output
        # zijin.output_to_file(body + '\n\n', filename='log.txt', mode='a')
        return body
    
    async def cutoff_email_body_end(self, body: str):
        """
        Cut off the email endings based on 2 scenarios, 'Signed-off-by:' and 'Name '
        """
        lines = body.split('\n')
        for i, line in enumerate(lines):
            if line.strip().lower().startswith('signed-off-by:'):
                return '\n'.join(lines[:i])

        # Fallback pattern: line ending with [(number):]
        pattern = re.compile(r'\(\d+\):\s*$')
        for i, line in enumerate(lines):
            if pattern.search(line.strip()):
                return '\n'.join(lines[:i])
            
        return body
        


    async def get_threads(self, sub_archive, limit):
        """ 
        Return a thread list with each entry [url, title, emails]. 
        """
        links = await self.get_thread_links_under_sub_archive(sub_archive_url=f"https://lore.kernel.org/{sub_archive}/")

        links = links[:limit]
        
        threads = []
        
        for url, title in links:
            emails = await self.get_emails_under_thread(thread_url=url)
            # log_color(f"url {url} title {title}")
            entry = {
                # "url": url, 
                "title": title, 
                "description": emails
            }
            threads.append(entry)
        
        return threads


    async def craw(self, sub_archive, user_query, limit):
        # links = await self.get_thread_links_under_sub_archive(sub_archive_url=f"https://lore.kernel.org/{sub_archive}/")
        # email_content_list = await self.get_emails_under_thread(thread_url=links[0][0])
        # log_color(email_content_list[0])

        # refresh log files
        zijin.output_to_file('', 'log.txt', mode='w')
        zijin.output_to_file('', sub_archive + '.txt', mode='w')
        
        start = time.perf_counter()
        threads = await self.get_threads(sub_archive, limit)
        end = time.perf_counter()
        log_color(f'get thread used {(end - start) * 1000} ms')

        # @debug
        output_file_name = sub_archive + '.txt'
        info = ''
        for thread in threads:
            # log_color(thread)
            emails = thread['description']
            # log_color("emails")
            # log_color(emails)
            info += f'============ EMAIL ============{thread["title"]}============================\n'
            info += '\n'.join(emails)
            # pass
            info += "\n\n"
        zijin.output_to_file(info, output_file_name, mode='w')
            
        return json.dumps(threads)

async def check_and_craw(prompt):
    mailing_lists = [
        'qemu-devel', 'linux-mm', 'stable', 'linux-fsdevel',
        'linux-arm-kernel',
        'ddprobe',
        'u-boot',
        'amd-gfx',
        'lkml',
        'xen-devel',
        'linux-clk',
        'linux-renesas-soc',
        'linux-xfs',
        'linux-ext4',
        'linux-api',
        'linux-block',
        'ltp',
        'linux-pm',
        'dri-devel',
        'nouveau',
        'intel-xe',
        'linux-mtd',
        'linux-btrfs',
        'bpf',
        'linux-trace-kernel',
        'openembedded-core',
        'linux-man',
        'linux-devicetree',
        'linux-arm-msm',
        'linux-input',
        'linux-doc',
        'imx',
        'netdev',
        'linux-patches',
        'linux-tegra',
        'linux-kselftest',
        'linux-iommu',
        'intel-gfx',
        'linux-gpio',
        'igt-dev',
        'linux-sound',
        'linux-watchdog',
        'linux-hardening',
        'linux-scsi',
        'linux-usb',
        'linux-i2c',
        'dmaengine',
        'linux-remoteproc',
        'linux-crypto',
        'linux-mmc',
        'linux-media',
        'linux-serial',
        'linux-acpi',
        'rcu',
        'oe-lkp',
        'linux-kbuild',
        'linux-perf-users',
        'io-uring',
        'regressions',
        'linux-rdma',
        'opensbi',
        'ath11k',
        'git',
        'linux-riscv',
        'linux-phy',
        'linux-cve-announce',
        'oe-kbuild-all',
        'linux-iio',
        'buildroot',
        'linux-wireless',
        'linux-mediatek',
        'linux-amlogic',
        'linux-nvme',
        'wireless-regdb',
        'linux-samsung-soc',
        'linux-nfs',
        'dpdk-dev',
        'virtio-fs',
        'virtualization',
        'kvm',
        'kdevops',
        'fstests',
        'mhi',
        'linux-efi',
        'loongarch',
        'qemu-riscv',
        'linux-parisc',
        'linux-bcache',
        'gfs2',
        'dm-devel',
        'linux-next',
        'linux-spi',
        'linux-cxl',
        'linux-erofs',
        'ath12k',
        'kernel-janitors',
        'platform-driver-x86',
        'linux-modules',
        'virtio-comment',
        'xenomai',
        'damon',
        'cgroups',
        'nvdimm',
        'linux-leds',
        'linux-omap',
        'linux-pci',
        'openembedded-devel',
        'grub-devel',
        'asahi',
        'linux-security-module',
        'linux-hwmon',
        'llvm',
        'iwd',
        'netfilter-devel',
        'intel-wired-lan',
        'linux-pwm',
        'linux-staging',
        'linux-fbdev',
        'linux-kernel-mentees',
        'linux-rt-devel',
        'phone-devel',
        'yocto-meta-ti',
        'linux-toolchains',
        'linux-debuggers',
        'linux-rockchip',
        'mm-commits',
        'linuxppc-dev',
        'rust-for-linux',
        'arm-scmi',
        'linux-embedded',
        'linux-integrity',
        'kexec',
        'linux-hyperv',
        'kvm-riscv',
        'kvmarm',
        'bridge',
        'linux-bluetooth',
        'linux-sgx',
        'linux-fscrypt',
        'yocto',
        'linux-m68k',
        'audit',
        'linux-edac',
        'acpica-devel',
        'ceph-devel',
        'tools',
        'linux-f2fs-devel',
        'selinux',
        'linux-firmware',
        'b4-sent',
        'cip-dev',
        'linux-coco',
        'linux-ide',
        'brcm80211',
        'yocto-docs',
        'bitbake-devel',
        'barebox',
        'netfs',
        'linux-cifs',
        'linux-fpga',
        'linux-trace-users',
        'dtrace',
        'linux-arch',
        'linux-mips',
        'linux-s390',
        'linux-sh',
        'linux-alpha',
        'sparclinux',
        'ntb',
        'yocto-status',
        'poky',
        'ocfs2-devel',
        'keyrings',
        'linux-sunxi',
        'netfilter',
        'chrome-platform',
        'sophgo',
        'linux-raid',
        'linux-lvm',
        'linux-rtc',
        'mptcp',
        'ntfs3',
        'linux-bcachefs',
        'linux-can',
        'yocto-patches',
        'coconut-svsm',
        'oe-kbuild',
        'linux-hams',
        'devicetree-spec',
        'dwarves',
        'linux-i3c',
        'x86-cpuid',
        'linux-unionfs',
        'kernelnewbies',
        'spacemit',
        'linux-sparse',
        'lkmm',
        'perfbook',
        'fio',
        'openbmc',
        'ath10k',
        'yocto-meta-virtualization',
        'linux-kernel-announce',
        'util-linux',
        'printing-architecture',
        'openrisc',
        'ofono',
        'yocto-meta-arm',
        'linux-rt-users',
        'kernelci',
        'linux-um',
        'stable-rt',
        'containers',
        'devicetree-compiler',
        'linux-newbie',
        'linux-trace-devel',
        'alsa-devel',
        'connman',
        'outreachy',
        'soc',
        'b43-dev',
        'diamon-discuss',
        'lttng-dev',
        'live-patching',
        'batman',
        'kvm-ppc',
        'cocci',
        'linux-snps-arc',
        'workflows',
        'target-devel',
        'selinux-refpolicy',
        'v9fs',
        'linux-spdx',
        'cti-tac',
        'yocto-meta-arago',
        'linux-sctp',
        'lvs-devel',
        'keys',
        'linux-aspeed',
        'u-boot-amlogic',
        'mailbox',
        'linux-wpan',
        'linux-ppp',
        'linux-csky',
        'linux-btrace',
        'linux-hexagon',
        'stgt',
        'kbd',
        'ell',
        'linux-nilfs',
        'dash',
        'cryptsetup',
        'linux-ia64',
        'linux-x25',
        'dccp',
        'lvfs-announce',
        'criu',
        'virtio-dev',
        'lvm-devel',
        'tech-board-discuss',
        'autofs',
        'yocto-meta-freescale',
        'xfs-stable',
        'lch',
        'fsverity',
        'lustre-devel',
        'kernel-hardening',
        'liba2i',
        'backports',
        'printing-users',
        'kernel-tls-handshake',
        'ksummit',
        'initramfs',
        'timestamp',
        'tpm2',
        'powertop',
        'reiserfs-devel',
        'distributions',
        'smatch',
        'linux-msdos',
        'mlmmj',
        'xdp-newbies',
        'linux-bugs',
        'ecryptfs',
        'landlock',
        'lartc',
        'wireguard',
        'lm-sensors',
        'yocto-toaster',
        'spdk',
        'accel-config',
        'radiotap',
        'signatures',
        'ccan',
        'fuego',
        'linux-assembly',
        'lvfs-general',
        'c-std-porting',
        'opae',
        'linux-hotplug',
        'kvm-ia64',
        'linux-smp',
        'cpufreq',
        'hail-devel',
        'trinity',
        'linux-numa',
        'linux-gcc',
        'linux-audit',
        'cluster-devel',
        'linux-config',
        'linux-8086',
        'kernel-testers',
        'linux-oxnas',
        'nil-migration',
        'linux-laptop',
        'oe-chipsec',
        'tpmdd-devel',
        'linux-console',
        'oe-linux-nfc',
        'linux-nfc',
        'dm-crypt',
        'linux-safety',
        'linux-admin',
        'linux-nvdimm',
        'historical-speck',
        'linux-c-programming',
        'linux-diald',
        'linux-metag',
        'ath9k-devel',
        'linux-x11',
        'ultralinux'
    ]

    if 'mailing' in prompt and 'list' in prompt:
        _p = prompt.split(' ')
        for p in _p:
            for ml in mailing_lists:
                if ml == p:
                    log_color(f'searching mailing list {p}')
                    await crawler.check()

                    limit = 4
                    limit_prefix = 'limit:'
                    index = prompt.find(limit_prefix)
                    if index != -1:
                        index += len(limit_prefix)
                        l_paren = -1
                        r_paren = -1
                        for i in range(index, len(prompt)):
                            if prompt[i] == '(':
                                l_paren = i
                                break
                        for i in range(l_paren + 1, len(prompt)):
                            if prompt[i] == ')':
                                r_paren = i
                                break
                        if l_paren != -1 and r_paren != -1:
                            limit = int(prompt[l_paren + 1:r_paren])

                    user_query = ""
                    query_prefix = 'query:'
                    index = prompt.find(query_prefix)
                    if index != -1:
                        index = index + len(query_prefix)
                        l_paren = -1
                        r_paren = -1
                        for i in range(index, len(prompt)):
                            if prompt[i] == '(':
                                l_paren = i
                                break
                        for i in range(l_paren + 1, len(prompt)):
                            if prompt[i] == ')':
                                r_paren = i
                                break
                        if l_paren != -1 and r_paren != -1:
                            user_query = prompt[l_paren + 1:r_paren].replace(' ', '+')

                    # TODO:
                    # does off-cpu's dash needs replacement?
                    log_color("query: " + user_query + "; limit: " + str(limit))

                    content = await crawler.craw(p, user_query, limit)
                    return f"""
Here are emails as context from the Linux mailing list, summary them based on their titles and descriptions, 
don\' t provide any other information. 

<context>
\"{content}\"
</context>

Please give your summary based on their titles and descriptions.
"""

    return prompt

crawler = Crawler()