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
```
