### Linux Agent

#### Installation

Please clone the repo first
```
git clone https://github.com/Sberm/linux-agent.git 
```

cd the directory
```
cd linux-agent
```

##### Frontend

Please install Node.js and npm. Node.js should be Version 22.10 or higher. On
Ubuntu, it is:
```
sudo apt install nodejs npm

linux-agent $ node -v
v22.15.0
```

make an .env file
```
cp .env.example .env
```

Running:
```
npm run dev
```

##### Backend

Please use Python version >= 3.11.
```
cd backend
# please change '~/linux-venv' to your desired venv path
python -m venv ~/linux-venv
source ~/linux-venv/activate/bin
pip install -r requirement.txt

# install xvfb
sudo apt install xvfb

# run
sh dev.sh
```

##### Ollama

Please install ollama using this command: 
```
curl -fsSL https://ollama.com/install.sh | sh
```

After this, serve and pull models
```
ollama serve

# in another bash window
ollama pull deepseek-r1:14b
ollama pull bge-m3
ollama pull linux6200/bge-reranker-v2-m3
```

The application should be running by now, please create your admin account.

##### Importing RAG Documents

You need to import documents manually, as the vector database binary
intermediate files are not committed to the GitHub repository.

On the front-end page, select `Workspace` -> `Knowledge` -> `plus sign` -> `Create a
knowledge base`.

Please import the documents by selecting the knowledge base you just created,
pressing the add sign, and uploading the files. The files are located in
`./rag-data`.

After that, select `Workspace` -> `Models` -> `plus sign`. Choose the DeepSeek model
you just pulled and click `Select Knowledge`. Choose the knowledge base you just
created; you can name this combination `deepseek + kernel`.

Now, click `New Chat`, select the `deepseek + kernel` model, and start making
queries.

The mailing list summarizer doesn't require additional setup, but it is
recommended to perform summaries using the `deepseek + kernel` model instead of
the base model, since additional retrieved context is included.

#### Prompt examples:

1. What is coreboot_device_id

2. Tell me about __audit_getname

3. Give me a summary on linux-mm mailing list

4. Summarize the linux-perf-users mailing list, limit:(2)

5. Write a driver that prints Hello World


#### Core API and Driver API that can be queried:

Core API: [https://docs.kernel.org/core-api/kernel-api.html](https://docs.kernel.org/core-api/kernel-api.html)
Driver API: [https://docs.kernel.org/driver-api/basics.html](https://docs.kernel.org/driver-api/basics.html)


#### Mailing lists that can be given a summary:

> 'qemu-devel', 'linux-mm', 'stable', 'linux-fsdevel', 'linux-arm-kernel', 'ddprobe', 'u-boot', 'amd-gfx', 'lkml', 'xen-devel', 'linux-clk', 'linux-renesas-soc', 'linux-xfs', 'linux-ext4', 'linux-api', 'linux-block', 'ltp', 'linux-pm', 'dri-devel', 'nouveau', 'intel-xe', 'linux-mtd', 'linux-btrfs', 'bpf', 'linux-trace-kernel', 'openembedded-core', 'linux-man', 'linux-devicetree', 'linux-arm-msm', 'linux-input', 'linux-doc', 'imx', 'netdev', 'linux-patches', 'linux-tegra', 'linux-kselftest', 'linux-iommu', 'intel-gfx', 'linux-gpio', 'igt-dev', 'linux-sound', 'linux-watchdog', 'linux-hardening', 'linux-scsi', 'linux-usb', 'linux-i2c', 'dmaengine', 'linux-remoteproc', 'linux-crypto', 'linux-mmc', 'linux-media', 'linux-serial', 'linux-acpi', 'rcu', 'oe-lkp', 'linux-kbuild', 'linux-perf-users', 'io-uring', 'regressions', 'linux-rdma', 'opensbi', 'ath11k', 'git', 'linux-riscv', 'linux-phy', 'linux-cve-announce', 'oe-kbuild-all', 'linux-iio', 'buildroot', 'linux-wireless', 'linux-mediatek', 'linux-amlogic', 'linux-nvme', 'wireless-regdb', 'linux-samsung-soc', 'linux-nfs', 'dpdk-dev', 'virtio-fs', 'virtualization', 'kvm', 'kdevops', 'fstests', 'mhi', 'linux-efi', 'loongarch', 'qemu-riscv', 'linux-parisc', 'linux-bcache', 'gfs2', 'dm-devel', 'linux-next', 'linux-spi', 'linux-cxl', 'linux-erofs', 'ath12k', 'kernel-janitors', 'platform-driver-x86', 'linux-modules', 'virtio-comment', 'xenomai', 'damon', 'cgroups', 'nvdimm', 'linux-leds', 'linux-omap', 'linux-pci', 'openembedded-devel', 'grub-devel', 'asahi', 'linux-security-module', 'linux-hwmon', 'llvm', 'iwd', 'netfilter-devel', 'intel-wired-lan', 'linux-pwm', 'linux-staging', 'linux-fbdev', 'linux-kernel-mentees', 'linux-rt-devel', 'phone-devel', 'yocto-meta-ti', 'linux-toolchains', 'linux-debuggers', 'linux-rockchip', 'mm-commits', 'linuxppc-dev', 'rust-for-linux', 'arm-scmi', 'linux-embedded', 'linux-integrity', 'kexec', 'linux-hyperv', 'kvm-riscv', 'kvmarm', 'bridge', 'linux-bluetooth', 'linux-sgx', 'linux-fscrypt', 'yocto', 'linux-m68k', 'audit', 'linux-edac', 'acpica-devel', 'ceph-devel', 'tools', 'linux-f2fs-devel', 'selinux', 'linux-firmware', 'b4-sent', 'cip-dev', 'linux-coco', 'linux-ide', 'brcm80211', 'yocto-docs', 'bitbake-devel', 'barebox', 'netfs', 'linux-cifs', 'linux-fpga', 'linux-trace-users', 'dtrace', 'linux-arch', 'linux-mips', 'linux-s390', 'linux-sh', 'linux-alpha', 'sparclinux', 'ntb', 'yocto-status', 'poky', 'ocfs2-devel', 'keyrings', 'linux-sunxi', 'netfilter', 'chrome-platform', 'sophgo', 'linux-raid', 'linux-lvm', 'linux-rtc', 'mptcp', 'ntfs3', 'linux-bcachefs', 'linux-can', 'yocto-patches', 'coconut-svsm', 'oe-kbuild', 'linux-hams', 'devicetree-spec', 'dwarves', 'linux-i3c', 'x86-cpuid', 'linux-unionfs', 'kernelnewbies', 'spacemit', 'linux-sparse', 'lkmm', 'perfbook', 'fio', 'openbmc', 'ath10k', 'yocto-meta-virtualization', 'linux-kernel-announce', 'util-linux', 'printing-architecture', 'openrisc', 'ofono', 'yocto-meta-arm', 'linux-rt-users', 'kernelci', 'linux-um', 'stable-rt', 'containers', 'devicetree-compiler', 'linux-newbie', 'linux-trace-devel', 'alsa-devel', 'connman', 'outreachy', 'soc', 'b43-dev', 'diamon-discuss', 'lttng-dev', 'live-patching', 'batman', 'kvm-ppc', 'cocci', 'linux-snps-arc', 'workflows', 'target-devel', 'selinux-refpolicy', 'v9fs', 'linux-spdx', 'cti-tac', 'yocto-meta-arago', 'linux-sctp', 'lvs-devel', 'keys', 'linux-aspeed', 'u-boot-amlogic', 'mailbox', 'linux-wpan', 'linux-ppp', 'linux-csky', 'linux-btrace', 'linux-hexagon', 'stgt', 'kbd', 'ell', 'linux-nilfs', 'dash', 'cryptsetup', 'linux-ia64', 'linux-x25', 'dccp', 'lvfs-announce', 'criu', 'virtio-dev', 'lvm-devel', 'tech-board-discuss', 'autofs', 'yocto-meta-freescale', 'xfs-stable', 'lch', 'fsverity', 'lustre-devel', 'kernel-hardening', 'liba2i', 'backports', 'printing-users', 'kernel-tls-handshake', 'ksummit', 'initramfs', 'timestamp', 'tpm2', 'powertop', 'reiserfs-devel', 'distributions', 'smatch', 'linux-msdos', 'mlmmj', 'xdp-newbies', 'linux-bugs', 'ecryptfs', 'landlock', 'lartc', 'wireguard', 'lm-sensors', 'yocto-toaster', 'spdk', 'accel-config', 'radiotap', 'signatures', 'ccan', 'fuego', 'linux-assembly', 'lvfs-general', 'c-std-porting', 'opae', 'linux-hotplug', 'kvm-ia64', 'linux-smp', 'cpufreq', 'hail-devel', 'trinity', 'linux-numa', 'linux-gcc', 'linux-audit', 'cluster-devel', 'linux-config', 'linux-8086', 'kernel-testers', 'linux-oxnas', 'nil-migration', 'linux-laptop', 'oe-chipsec', 'tpmdd-devel', 'linux-console', 'oe-linux-nfc', 'linux-nfc', 'dm-crypt', 'linux-safety', 'linux-admin', 'linux-nvdimm', 'historical-speck', 'linux-c-programming', 'linux-diald', 'linux-metag', 'ath9k-devel', 'linux-x11', 'ultralinux',
