### Dockerfileから問題を起動する

#### Dockerfileファイルをビルドする
  
```
カレントディレクトリ内のDockerfileをビルドする
sudo docker build -t <任意のタグ名> .

例:
sudo docker build -t pwn1 .
```

#### ビルドしたDockerfileを起動する

```
sudo docker run -d -p 3000:3000 pwn1
```

#### Dockerが起動しているか確認する

```
sudo docker ps

返答例:
7ec4732c5010   pwn1      "/pwn/entry.sh"   2 minutes ago   Up 2 minutes   0.0.0.0:3000->3000/tcp, [::]:3000->3000/tcp, 4321/tcp   jovial_lewin
```

#### 起動したDocker内にシェルでアクセスする

```
sudo docker exec -it jovial_lewin bash
もしくは
sudo docker run -it nocontrol /bin/bash
```

#### Dockerfileに追加するべきコマンド

```
RUN apt-get update && apt-get install -y gdb gdbserver git python3-pip vim

RUN git clone https://github.com/pwndbg/pwndbg
RUN cd pwndbg && ./setup.sh
RUN echo "source /opt/pwndbg/gdbinit.py" >> /root/.gdbinit
```

xinetdはまれにsocatとの相性が悪くなってncで接続できなくなるときがある  

```
RUN apt-get -y update --fix-missing && apt-get -y upgrade
RUN apt-get -y install socat net-tools gdb gdbserver
```

docker-compose.ymlが配布されている場合は以下  
```
元のdocker-compose.yml:

yamlversion: '3'
services:
  no_control:
    build:
      context: .
    restart: always
    working_dir: /home/pwn
    container_name: no_control_chall
    ulimits:
      nproc: 65535
      core: 0
    ports:
      - "9005:9005"
    entrypoint: /etc/init.sh

修正後のdocker-compose.yml:
yamlversion: '3'
services:
  no_control:
    build:
      context: .
    restart: always
    working_dir: /home/pwn
    container_name: no_control_chall
    ulimits:
      nproc: 65535
      core: 0
    ports:
      - "9005:9005"      # 本番環境ポート（元のまま）
      - "10000:10000"    # デバッグ用ポート（socat経由）
      - "12345:12345"    # gdbserver用ポート
    entrypoint: /etc/init.sh
    # デバッグに必要な権限を追加
    cap_add:
      - SYS_PTRACE
    security_opt:
      - seccomp:unconfined
```

また、init.shが配布ファイルに存在する場合は以下  

```
#!/bin/bash

cd /home/pwn

# 本番ポート（xinetdの代わりにsocatで直接起動）
socat TCP-LISTEN:9005,reuseaddr,fork,su=pwn EXEC:"/home/pwn/redir.sh",pty,stderr &

# デバッグ用ポート
socat TCP-LISTEN:10000,reuseaddr,fork,su=pwn EXEC:"/home/pwn/redir.sh",pty,stderr &

# gdbserver用ポート
socat TCP-LISTEN:12345,reuseaddr,fork EXEC:"gdbserver - /home/pwn/chall",pty,stderr &

sleep 2

echo "=== Services started ==="
ps aux | grep -E "(socat|gdbserver)" | grep -v grep
echo "=== Listening ports ==="
ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null

/bin/sleep infinity
```

ビルドと起動  
```
# 既存コンテナを停止・削除
sudo docker-compose down

# 新しくビルド（キャッシュを使わない）
sudo docker-compose build --no-cache

# 起動
sudo docker-compose up -d

# ログ確認
sudo docker-compose logs

# 接続確認
nc localhost 9005    # 本番環境
nc localhost 10000   # デバッグ環境
```
