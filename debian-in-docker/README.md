在 Linux 上通过 Cloudflare Tunnel 使用 SSH 登录，本质上是把 **Cloudflare 提供的“加密隧道”** 和 **传统的“SSH 密钥认证”** 结合起来。

```
debian:bookworm 对应的镜像是 ->

sjwayrhz/debian:tunnel-v0.1
```

以下是完整的操作步骤总结：

### 第一步：准备工作（客户端）

确保你的本地 Linux 电脑已经安装了 `cloudflared`。

```bash
# 下载并安装（以 amd64 为例）
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb && sudo dpkg -i cloudflared.deb
```

### 第二步：配置 SSH 别名

编辑你本地的 SSH 配置文件（如果文件不存在就直接创建）：

```bash
vim ~/.ssh/config
```

在文件中添加以下内容：

```text
Host my-tunnel
    HostName your-domain.com
    User root
    IdentityFile ~/.ssh/id_ed25519
    ProxyCommand /usr/bin/cloudflared access ssh --hostname %h
```

> **注意：** 把 `your-domain.com` 换成你的域名，`id_ed25519` 换成你真实的私钥文件名。

### 第三步：设置私钥权限

SSH 对私钥权限要求非常严格，如果权限太高会报错无法连接：

```bash
chmod 600 ~/.ssh/id_ed25519
```

### 第四步：一键登录

现在，你不再需要输入复杂的命令，直接输入：

```bash
ssh my-tunnel
```

---

### 💡 运行流程说明

1. **身份授权**：第一次运行 `ssh my-tunnel` 时，终端可能会显示一个 URL，要求你在浏览器中打开并登录 Cloudflare 账号进行授权。
2. **建立隧道**：`cloudflared` 插件会根据配置自动接管连接，把流量打入 Cloudflare 网络。
3. **密钥匹配**：隧道接通后，SSH 会自动读取 `IdentityFile` 里指定的密钥进行服务器端验证。
4. **登录成功**：验证通过，你进入服务器。

### 常见避坑指南：

* **确认公钥已上传**：你的服务器 `/root/.ssh/authorized_keys` 文件里必须已经存好了对应的公钥，否则会提示 `Permission denied`。
* **确认路径**：如果不确定 `cloudflared` 的安装路径，运行 `which cloudflared` 查看。如果结果是 `/usr/local/bin/cloudflared`，记得在 `config` 文件里修改对应的路径。

