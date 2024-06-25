# Deploy da aplicação!

 - ## Servidor DNS
		 
	- ### 1: Instalação do BIND
		```bash
		sudo apt update
		sudo apt install bind9
		```
	- ### 2: Configurar os Arquivos de Zona
		
	   Vá até o diretório `/etc/bind` e crie um arquivo para sua zona.
	   ```bash
	   sudo nano /etc/bind/db.riume.com.br
	   ```
	   Adicione as seguintes informações:
	   ```
	   $TTL    604800
	   @       IN      SOA     ns.riume.com.br admin.riume.com.br (
	                             3         ; Serial
	                          604800         ; Refresh
	                           86400         ; Retry
	                         2419200         ; Expire
	                          604800 )       ; Negative Cache TTL
	   ;
	   @       IN      NS      ns.riume.com.br
	   ns     IN      A       192.168.29.2
	   nutrisafe     IN      A       192.168.29.130
	   nutrisafe-back 	IN		A		192.168.29.130
	   database		 IN		A		192.168.29.150
	   load-balancer		IN		A	 	192.168.29.100
	   ```

	- ### 3: Editar o Arquivo de Configuração Principal
		Edite o arquivo `named.conf.local` para incluir os arquivos de zona:
		```bash
		sudo nano /etc/bind/named.conf.local
		```
		Adicione o seguinte:
		```bash
		zone "riume.com.br" {
		    type master;
		    file "/etc/bind/db.riume.com.br";
		};
		```

	- ### 4: Reiniciar o Serviço BIND
		Reinicie o serviço BIND para aplicar as configurações:
		```bash
		sudo systemctl restart bind9
		```
- ## Criando API Gateway com HAproxy
	- ### 1: Configurando o HAproxy.cfg
		Adicione as seguintes configurações em um arquivo haproxy.cfg criado em  `/usr/local/etc/haproxy`
		```
		global
	  maxconn 20480

		defaults
		  mode http
		  timeout connect 4s
		  timeout client 20s
		  timeout server 3m

		frontend http-in
		  bind *:80
		  mode http

		  use_backend nutrisafe_backend if { hdr(host) -i nutrisafe-back.riume.com.br }
		  use_backend nutrisafe_frontend if { hdr(host) -i nutrisafe.riume.com.br }

		backend nutrisafe_backend
		  mode http
		  server app1 192.168.29.130:3000 check

		backend nutrisafe_frontend
		  mode http
		  server app2 192.168.29.130:80 check

		############ database ################

		frontend in-database
		  timeout client 95s
		  mode tcp
		  bind *:5432
		  default_backend out-database

		backend out-database
		  mode tcp
		  server 192.168.29.150:5432 check fall 3 rise 2

		```
	- ### 2: Criação do docker-compose com HAproxy	
		Crie um Docker-compose, certifique de ter instalado o docker.io, 
		```yaml
		version : '3'
		services:
		  elb:
		    image: haproxy
		      ports:
		        - "80:80"
		        - "443:443"
		        - "5432:5432"
		        - "3000:3000"
		      volumes:
		        - /usr/local/etc/haproxy:/usr/local/etc/haproxy
		```
- ## Configurando certificado SSL

	- ### 1: Gerando certificado
		Instalando o certbot e o plugin do Route53 usando snap:
		```bash
		sudo snap install --classic certbot
		sudo ln -s /snap/bin/certbot /usr/bin/certbot
		sudo snap set certbot trust-plugin-with-root=ok
		sudo snap install certbot-dns-route53
		```
	
	- ### 2: Configurando credenciais da aws
		Já com o IAM configurado com  as políticas `route53:ListHostedZones, route53:GetChange, route53:ChangeResourceRecordSets`.
		Configure as credenciais em `~/.aws/config`.

	- ### 3: Executando e configurando renovação automática
		Crie um arquivo em `/root/certbotRenew.sh`, e cole o script 
		```bash
		#!/bin/bash
		cat  /etc/letsencrypt/live/riume.com.br/fullchain.pem  /etc/letsencrypt/live/riume.com.br/privkey.pem > /usr/local/etc/haproxy/fullchain.pem
		docker  restart  haproxy
		``` 
		Execute o comando:
		```bash
		certbot certonly --dns-route53 -d *.riume.com.br -d riume.com.br --deploy-hook /root/certbotRenew.sh`
		```
	- ### 4: Adicionando o certificado SSL no haproxy.cfg
		 Adicione o seguinte trecho:
		 ```cfg
		frontend in-https
		bind *:443 ssl crt /usr/local/etc/haproxy/fullchain.pem
		use_backend nutrisafe_backend if { hdr(host) -i nutrisafe-back.riume.com.br }
		use_backend nutrisafe_frontend if { hdr(host) -i nutrisafe.riume.com.br }
		 ```
		
	- ### 5: Executando o docker compose
		Utilize o comando `docker-compose up`

## Configurando o banco de dados
- ### Instalando o Postgres
	Verifique se está com os repositórios atualizados e execute o comando:
	`sudo apt install postgresql postgresql-contrib`  

- ### Configurando o banco de dados
	Após a instalação é criado um usuário postgres, troque para o usuário executando `sudo -i -u postgres`.
	Crie um usuário para acesso do banco:
	```sql
	CREATE ROLE meu_usuario WITH LOGIN PASSWORD 'senha_secreta';
	ALTER ROLE meu_usuario CREATEDB;
	```
  Troque de usuário e crie a database `nutri_safe` 
## Configurando servidor de aplicação
- ### Configurando FrontEnd e BackEnd
	- ### 1: Instalação
		Para a instalação do nginx, git e node execute o comando: `sudo apt install nginx git nodejs`.

	- ### 2: Clonando repositórios 
		Clonando os repositórios:
		```bash
		git clone https://github.com/NutriSafeTeam/NutriSave-Frontend.git
		git clone https://github.com/NutriSafeTeam/NutriSave-Backend.git
		```
	- ### 3: Configurando os projetos
		Execute `npm install` nas respectivas pastas.
		- #### FrontEnd
			 No FrontEnd, builde utilizando o comando `ng build`.
			- Crie um arquivo no diretório `sudo nano /etc/nginx/sites-available/nutrisafe.conf`.
			- Coloque a seguinte configuração
				```cfg
				server {
				    listen 80;
				    server_name nutrisafe.riume.com.br;

				    root ~/NutriSave-Frontend/dist/NutriSave-Frontend;
				    index index.html index.html;

				    location / {
				        try_files $uri $uri/ /index.html;
				    }
				}
				```
			- Criando link simbólico `sudo ln -s /etc/nginx/sites-available/nutrisafe.conf /etc/nginx/sites-enabled/.
` 
			- Reiniciando nginx `sudo systemctl reload nginx`. 
		
		- #### BackEnd
			- Crie um .env em os valores:
				```.env
				DATABASE_HOST=database.riume.com.br
			    DATABASE_PORT=5432,
			    DATABASE_USERNAME=meu_usuario,
			    DATABASE_PASSWORD=senha_secreta
			    DATABASE=nutri_safe,
				```
			
			-	Execute o comando `npm build`
			
			- Após buildar o projeto execute `node ~/NutriSave-Backend/dist/Main`
			