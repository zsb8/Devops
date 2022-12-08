# Project Name: Vault Jenkins Pipeline 

# Project Goal
Integrate Vault into Jenkins pipeline, as well as the basic usage of Hashicorp Vault.

# Table of Contents
1. [Prerequisites](#prerequisites)
2. [Project Steps](#project_steps)
3. [Post Project](#post_project)
4. [Troubleshooting](#troubleshooting)
5. [Reference](#reference)

# <a name="prerequisites">Prerequisites</a>
- Ubuntu 20.04 OS (Minimum 2 core CPU/8GB RAM/30GB Disk)
- Docker(see installation guide [here](https://docs.docker.com/get-docker/))
- Docker Compose(see installation guide [here](https://docs.docker.com/compose/install/))

# <a name="project_steps">Project Steps</a>

## 1. Initiate Vault
a. **Initializing** the Vault
```bash
docker-compose up -d
docker exec -it $(docker ps -f name=vault_1 -q) sh
export VAULT_ADDR='http://127.0.0.1:8200'
vault operator init
```
![image](https://user-images.githubusercontent.com/75282285/206345290-5d8184e6-1942-4be7-bb00-84407673c5aa.png)

**Note:** Make a note of the output. This is the only time ever you see those unseal keys and root token. If you lose it, you won't be able to seal vault any more.
```
/vault/data # export VAULT_ADDR='http://127.0.0.1:8200'
/vault/data # vault operator init
Unseal Key 1: ezsvewsxANkLCFxkQKVP+XNaO8ivlNkBxSTYGnu7JBBj
Unseal Key 2: 5K/9CESOL1KCYYFeQc0vRzBtKEYusDT+YONDhgPYxZng
Unseal Key 3: E0rsdCm2dCt/fUgXZeftL3p9IgvDH7oivXDjVI/rRpa9
Unseal Key 4: JdjQ7gbPHgQZAB5UWQ7rV1A5wpZ5OkWVeVKhTYMTZotM
Unseal Key 5: /knntQuDnzswhIK1XhpZh77ByheqWFOi69FehuxtIq3N

Initial Root Token: hvs.mzUOQ9nFDC8F8U1nPLX0Kb6h
```

b. **Unsealing** the vault</br>
In the Vault container. Type `vault operator unseal <unseal key>`. The unseal keys are from previous output. You will need at lease **3 keys** to unseal the vault. </br>

When the value of  `Sealed` changes to **false**, the Vault is unsealed. You should see below similar output once it is unsealed

```
Unseal Key (will be hidden): 
Key                     Value
---                     -----
Seal Type               shamir
Initialized             true
Sealed                  false
Total Shares            5
Threshold               3
Version                 1.12.1
Build Date              2022-10-27T12:32:05Z
Storage Type            raft
Cluster Name            vault-cluster-403fc7a0
Cluster ID              772cef22-77d2-11bb-f16b-7ef69d85ac0e
HA Enabled              true
HA Cluster              n/a
HA Mode                 standby
Active Node Address     <none>
Raft Committed Index    31
Raft Applied Index      31
```
![image](https://user-images.githubusercontent.com/75282285/206467158-7da61fdd-3fb2-4555-8317-0b2ad7f6185f.png)

c. Sign in to vault with **root** user </br>
Type `vault login` and enter the `Initial Root Token` retrieving from previous output
```
/ # vault login
Token (will be hidden): 
Success! You are now authenticated. The token information displayed below
is already stored in the token helper. You do NOT need to run "vault login"
again. Future Vault requests will automatically use this token.

Key                  Value
---                  -----
token                hvs.KtwbjaZwYBV4BPohe6Vi48BH
token_accessor       aVZzcPF3oCCIqGLzqoxvgLLC
token_duration       ∞
token_renewable      false
token_policies       ["root"]
identity_policies    []
policies             ["root"]
```
![image](https://user-images.githubusercontent.com/75282285/206518099-c4821d8e-d84c-411b-b33b-9ef26a948537.png)


## 2. Enable Vault KV Secrets Engine Version 2
> Refer to https://developer.hashicorp.com/vault/docs/secrets/kv/kv-v2
```
vault secrets enable -version=2 kv-v2
vault kv put -mount=kv-v2 devops-secret username=root password=changeme
```
![image](https://user-images.githubusercontent.com/75282285/206518379-b2d9ba42-8e60-4922-9c22-62fcdeb7142d.png)

You can **read** the data by running this:
```
vault kv get -mount=kv-v2 devops-secret
```
Then you should be able to see below output
```
====== Data ======
Key         Value
---         -----
password    changeme
username    root
```
![image](https://user-images.githubusercontent.com/75282285/206518625-44c3b8e1-ad89-4ade-95a5-ed843d9248ea.png)

> Note: Since version 2 kv has prefixed `data/`, your secret path will be `kv-v2/data/devops-secret`, instead of `kv-v2/devops-secret`

## 3. Write a Vault Policy and create a token
a. **Write** a policy
```
cat > policy.hcl  <<EOF
path "kv-v2/data/devops-secret/*" {
  capabilities = ["create", "update","read"]
}
EOF
vault policy write first-policy policy.hcl
vault policy list
vault policy read first-policy
```

b. **Enable approle**
```
vault auth enable approle
```
![image](https://user-images.githubusercontent.com/75282285/206519049-4550f60e-8324-407d-8870-6f7c9de1d1bf.png)

c. Create an **role**
```
vault write auth/approle/role/first-role \
    secret_id_ttl=10000m \
    token_num_uses=10 \
    token_ttl=20000m \
    token_max_ttl=30000m \
    secret_id_num_uses=40 \
    token_policies=first-policy

# Check the role id
export ROLE_ID="$(vault read -field=role_id auth/approle/role/first-role/role-id)"
echo $ROLE_ID
```
> **Note:** Please make a note as it will be needed when configuring Jenkins credential
![image](https://user-images.githubusercontent.com/75282285/206519276-e6c918aa-9536-45f9-94f6-670006a18c13.png)
In this case, the role_id is c8329502-e4cf-4c7f-10fd-5d3dfabea474     
d. Create a **secret id** via the previous role
```
export SECRET_ID="$(vault write -f -field=secret_id auth/approle/role/first-role/secret-id)"
echo $SECRET_ID
```
> **Note:** Please make a note as it will be needed when configuring Jenkins credential
![image](https://user-images.githubusercontent.com/75282285/206519473-8f40bdb4-1b8a-45ab-a215-d5861951980e.png)
In this case, the Secret_id is: d4fc7b52-92a9-bc77-6f3c-a1661d7df1ef     


e. Create a **token** with the role ID and secret ID
```
apk add jq
export VAULT_TOKEN=$(vault write auth/approle/login role_id="$ROLE_ID" secret_id="$SECRET_ID" -format=json|jq .auth.client_token)
echo $VAULT_TOKEN
VAULT_TOKEN=$(echo $VAULT_TOKEN|tr -d '"')
vault token lookup | grep policies
```
![image](https://user-images.githubusercontent.com/75282285/206527342-5bb1a63b-ae2d-4406-a67c-d41aaa10fee6.png)

f. Write a **secret** via the new token
```
vault kv put -mount=kv-v2 devops-secret/team-1 username2=root2 password2=changemeagain
vault kv get -mount=kv-v2 devops-secret/team-1
```
![image](https://user-images.githubusercontent.com/75282285/206527658-9f1e50e8-29cd-4a63-8ef0-0f882d8c2d9f.png)

## 4. Add the role id/secret id in Jenkins
> Refer to https://plugins.jenkins.io/hashicorp-vault-plugin/#plugin-content-vault-app-role-credential

Login to your Jenkins website.
![image](https://user-images.githubusercontent.com/75282285/206530163-fcc03811-d9d0-4b53-9298-421fcc61383d.png)

Go to **"Manage Jenkins"** -> **"Manage Credentials"** ->  **"System"** -> **"Global credentials (unrestricted)"** -> Click **"Add Credentials"** and you should fill out the page in below selection: </br>
![image](https://user-images.githubusercontent.com/75282285/206530541-8585d4ea-8c0a-4ba6-ae0c-38a4f468ddd2.png)

**Kind:** Vault App Role Credential</br>
**Scope:** Global (Jenkins,nodes,items,all child items,etc)</br>
**Role ID:** <ROLE_ID from previous step></br>
**Secret ID:** <SECRET_ID from previous step></br>
**Path:** approle</br>
**Namespace:** (Leave it blank) </br>
**ID:** (the credential id you will refer within Jenkins Pipeline. i.g. vault-app-role)</br>
**Description:** Vault: AppRole Authentication</br>
![image](https://user-images.githubusercontent.com/75282285/206531579-861b0805-c0ea-445c-b417-0551192af41a.png)

## 5. Add github credential in Jenkins
Login to your Jenkins website and go to **"Manage Jenkins"** -> **"Manage Credentials"** ->  **"System"** -> **"Global credentials (unrestricted)"** -> Click **"Add Credentials"** and you should fill out the page below below selection:</br>
**Scope:** Global (Jenkins,nodes,items,all child items,etc) </br>
**Username:** (your github username)</br>
**Password:** <your github personal access token> (please refer to [here](https://docs.github.com/en/enterprise-server@3.4/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token))</br>
**ID:** (the id which will be referred in Jenkinsfile, i.g. github-token)</br>
**Description:** Github token</br>
![image](https://user-images.githubusercontent.com/75282285/206532665-9fd5f3dd-24ab-4f77-b152-98bff3ae543f.png)

![image](https://user-images.githubusercontent.com/75282285/206532834-2a66134a-28d0-4f96-b3c0-afa6cbf6dc25.png)



## 6. Create a Jenkins Pipeline
a. In the Jenkins portal, click **"New Item"** in the left navigation lane, and type the item name (i.g. first-project) and select **"Pipeline"**. Click **"OK"** to configure the pipeline.</br> 
![image](https://user-images.githubusercontent.com/75282285/206533055-c6dd4abc-74bc-446b-bc5a-27bb128d565e.png)

b. Go to **"Pipeline"** section and select **"Pipeline script from SCM"** in the **"Definition"** field</br>
c. Select **"Git"** in **"SCM"** field</br>
d. Add `https://github.com/chance2021/devopsdaydayup.git` in **"Repository URL"** field</br>
e. Select your github credential in **"Credentials"**</br>
f. Type `*/main` in **"Branch Specifier"** field</br>
![image](https://user-images.githubusercontent.com/75282285/206541412-dd623aaf-299f-4741-822c-900e1bbe550f.png)

g. Type `005-VaultJenkinsCICD/Jenkinsfile` in **"Script Path"**</br>
h. Unselect **"Lightweight checkout"**</br>
![image](https://user-images.githubusercontent.com/75282285/206534004-09fd14f5-9764-4b3c-9bf1-9ee83163dceb.png)

h. Run it.
![image](https://user-images.githubusercontent.com/75282285/206534327-37c8a00d-21a5-49f0-904e-7c3ed0b72142.png)

i. Check the log.
![image](https://user-images.githubusercontent.com/75282285/206541670-ef2307c7-9766-4b64-9f8c-9201f130e4cd.png)



j. Check the new file in Jenkins contain. 
![image](https://user-images.githubusercontent.com/75282285/206535861-690685a9-61f5-4ceb-940b-3af7c0f77453.png)
You will find these new files and the contents.
![image](https://user-images.githubusercontent.com/75282285/206542044-65fb5803-ed7b-432a-b731-b083e8845908.png)



# <a name="post_project">Post Project</a>
Delete the docker-compose containers, as well as the volumes associated
```
docker-compose down -v
```
# <a name="troubleshooting">Troubleshooting</a>
## Issue 1: Access denied to Vault Secrets at 'kv-v2/devops-secret/team-1'
**Solution:**
If you see an information in the log like `[INFO]  expiration: revoked lease`, that means your secret is expired and you may need to renew it by running below command:
```
vault write -f -field=secret_id auth/approle/role/first-role/secret-id
```
Then, you can update your new secret in corresponding Jenkins credential.

Sometime this may be a general error which indicates something wrong in your Jenkinsfile configuration. One thing worth to mention is that, in the Jenkinsfile, `secrets` should use `engineVersion:2`, while `configuration` should use `engineVersion:1`. This is because `engineVersion:2` in `secrets` is referring to kv version, which is version 2 in our lab. However the `engineVersion` in `configuration` is referringto the API version, which should be version 1. You can tell this in below API call:
```
curl  --header "X-Vault-Token: hvs.CAESI..."     http://vault:8200/v1/kv-v2/devops-secret/team-1
```

You can see `http://vault:8200/v1` which means the API version is `1`. This is referring to the `engineVersion` in `configuration`. Also, my secret actual path is `kv-v2/data/devops-secret/team-1`, `/data` is just prefix for kv 2 secret path, so that is why `engineVersion` is `2` in `secret` as it is reffering to the kv version, not API version. 

## Issue 2: Failed to look up namespace from the token: no namespace
export VAULT_TOKEN=$(vault write auth/approle/login role_id="$ROLE_ID" secret_id="$SECRET_ID" -format=json|jq .auth.client_token)
echo $VAULT_TOKEN
vault token lookup | grep policies
**Solution:**
Error might happen if quotes exists in token
```
VAULT_TOKEN=$(echo $VAULT_TOKEN|tr -d '"')
```
ref: https://github.com/hashicorp/vault/issues/6287#issuecomment-684125899



# <a name="reference">Reference</a>
[Vault Getting Started Deploy](https://developer.hashicorp.com/vault/tutorials/getting-started/getting-started-deploy)</br>
[Vault Store The Google API Key](https://developer.hashicorp.com/vault/tutorials/secrets-management/static-secrets#store-the-google-api-key)</br>
[Vault Signed SSH Certificates](https://developer.hashicorp.com/vault/docs/secrets/ssh/signed-ssh-certificates)</br>


## Issue 3: version in plugins.txt
![WeChat Image_20221208090241](https://user-images.githubusercontent.com/75282285/206465712-5bfb442a-5d5d-4a8c-beb5-5f8da2c545e0.png)
Solve: change the configuration-as-code's version in plugins.txt to 1569.vb_72405b_8029

