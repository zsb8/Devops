# Project Name: Push War file to Nexus Repository Via Jenkins Pipeline and Deploy to Tomcat in Vagrant VM

# Project Goal
In this article, I set up a **Nexus** repository and push a war file from **Jenkins Pipeline**, then I deploy the war file to a **Tomcat 9** installed in a **Vagrant VM**

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
- Vagrant(see download page [here](https://developer.hashicorp.com/vagrant/downloads))
- VBox (see installation guide [here](https://www.virtualbox.org/wiki/Linux_Downloads))

# <a name="project_steps">Project Steps</a>

## 1. Deploy Jenins and Nexus containers
```
docker-compose build
docker-compose up -d
```
![image](https://user-images.githubusercontent.com/75282285/206592364-1106da4e-bb3e-4015-9b1a-14845cf4564b.png)

## 2. Configure Nexus
a. Enter the Nexus container and find the username and password</br>
The username and password to login to Nexus are placed in Nexus contain, the path is `/nexus-data`, the password file is `admin.password`. 
![image](https://user-images.githubusercontent.com/75282285/206592514-c4839542-8828-46d3-9d78-7e7de57588cd.png)
 Open a browser and **login to** Nexus home page (http://192.168.50.164:8081)</br>
![image](https://user-images.githubusercontent.com/75282285/206592296-2d625285-3805-46fe-8bf1-c61465632b4f.png)

b. Fetch the **password** for `admin` user</br>
```
docker exec $(docker ps --filter name=nexus_1 -q) cat /nexus-data/admin.password
```
![image](https://user-images.githubusercontent.com/75282285/206592941-2e4edfa9-9258-4030-b394-3070208149da.png)

c. Click **"Sign In"** in the top right and type username `admin`, as well as the password fetched in the previous step</br>
d. Follow the **wizard** and reset your password. Such as `123456`</br>
![image](https://user-images.githubusercontent.com/75282285/206593040-fd5a05fc-9d72-4c4c-94c4-4d4112d03564.png)
Select **"Enable anonymous access"** and click **"Next"**->**"Finish"** to complete the guide.</br>
![image](https://user-images.githubusercontent.com/75282285/206593084-aa0eb65e-29ca-4f65-923f-a2c348882bf6.png)

e. Click **Gear icon** in the top and click **"Repositories"** in **"Repository"** section. Click **"Create repository"** to create a new repo.</br>
![nexus-create-repo](images/nexus-create-repo.png)
f. Select **"maven2(hosted)"** and fill below fields as instructed: </br>
**Name:** `maven-nexus-repo`</br>
**Version policy:** Mixed</br>
**Deployment policy:** Allow redeploy</br>
![nexus-create-repo-2](images/nexus-create-repo-2.png)
Click **"Create repository"** in the bottom</br>
![image](https://user-images.githubusercontent.com/75282285/206593414-fc5d30f4-fbb4-44aa-a3f2-741a2f8d8b91.png)


g. To create a new user, go to **"Security"** -> **"Users"** -> Click **"Create local user"** and fill below fields as instructed: </br>
![image](https://user-images.githubusercontent.com/75282285/206595499-0025562e-32e7-4369-8afa-432c26610fd8.png)
![image](https://user-images.githubusercontent.com/75282285/206595701-51de33e8-6ba6-4e7f-a607-95ad496a1680.png)
**ID:** `jenkins-user` </br>
**First name:** Jenkins</br>
**Last name:** User</br>
**Email:** jenkins.user@gmail.com</br>
**Password:**  *(Type your password)*, such as `123456` </br>
**Confirm password:**  *(Type the same password you entered above)* , such as `123456` </br>
**Status:** Active</br>
**Roles:** nx-admin</br> 
![image](https://user-images.githubusercontent.com/75282285/206595741-5b3d2c39-0679-4a5c-b3c0-e7a406e50950.png)

## 3. Configure Jenkins
### a. Login to your Jenkins website (http://192.168.50.164:8080) and go to **"Manage Jenkins"** -> **"Manage Credentials"** 
![image](https://user-images.githubusercontent.com/75282285/206596072-a566fa88-b91b-4208-9670-a9e70835544f.png)
Then go to  **"System"** -> **"Global credentials (unrestricted)"** -> Click **"Add Credentials"** 
![image](https://user-images.githubusercontent.com/75282285/206596162-1744d792-ecc7-4324-8cfd-2de99a78ea59.png)
You should fill out the page in below selection: </br>
> Note: The **username** is in `.env` file </br>

**Kind:** Username with password</br>
**Scope:** Global(Jenkins, nodes, items, all child items, etc)</br>
**Username:** jenkins-user</br>
**Password:** *(Type the password you set in previous step)*, such as `123456`</br>
**ID:** nexus</br>
**Description:** nexus credential</br>
![image](https://user-images.githubusercontent.com/75282285/206597432-ffe9a1b6-afa6-4959-92d3-70e8f95428d5.png)

### b. Creat the pipeline
To create a new pipeline, go back to Dashboard, click **"New Item"** in the left navigation lane, and type the item name (i.g. `first-project`) and select **"Pipeline"**. Click **"OK"** to configure the pipeline.</br>
![image](https://user-images.githubusercontent.com/75282285/206597540-1c6f9962-ddc3-45e0-84ec-8caa54238f11.png)

c. Go to **"Pipeline"** section and select **"Pipeline script from SCM"** in the **"Definition"** field</br>
d. Select **"Git"** in **"SCM"** field</br>
e. Add `https://github.com/zsb8/Devops.git` in **"Repository URL"** field</br>
f. Select your github credential in **"Credentials"**</br>
g. Type `*/main` in **"Branch Specifier"** field</br>
h. Type `006-NexusJenkinsVagrantCICD/Jenkinsfile` in **"Script Path"**</br>
i. Unselect **"Lightweight checkout"** and click "Apply" to complete the creation</br>
![image](https://user-images.githubusercontent.com/75282285/206598053-600dad5e-694d-41d8-a8f0-cb138dbb9180.png)


j. To add maven tool, go back to **"Dashboard"** -> **"Manage Jenkins"** -> **"Global Tool Configuration"** 
![image](https://user-images.githubusercontent.com/75282285/206598272-23069659-fb3f-4f9f-976e-dbf8cb92d892.png)
Then Scroll down to **"Maven"** section and click **"Add Maven"**. Then fill out below fields as instructed:</br>
**Name:** m3</br>
**Install automaticall** selected</br>
**Version:** 3.8.6</br>
Click **"Save"**</br>
![image](https://user-images.githubusercontent.com/75282285/206598578-dffbc850-ec3d-46b0-a8e5-2f54cf781f40.png)

## 4. Launch the Jenkins pipeline
Go to **"Dashboard"** -> Click **"first-project"** pipeline -> Click **"Build Now"**
![image](https://user-images.githubusercontent.com/75282285/206598847-867e1853-3882-4fad-bb87-b1a0a38157e1.png)

Then the Jenkins pipeline will compile the app to a war file and upload to the Nexus repository. </br>
You can login to the Nexus website (http://192.168.50.164:8081) and go to **"Browse"** section, and then click **"maven-nexus-repo"**, you should be able to see the artifacts just uploaded.
![nexus-repo-configuration](images/nexus-repo-configuration.png)

## 5. Deploy a Tomcat server via Vagrant
Install Vagrant.
https://developer.hashicorp.com/vagrant/downloads <br>
![image](https://user-images.githubusercontent.com/75282285/206619473-b762eb32-4225-44c5-805d-d36c51c316c8.png)

Install Virtualbox.  https://tecadmin.net/how-to-install-virtualbox-on-ubuntu-22-04/ <br> 
Run below command to start up a Vagrant VM:
```
vagrant up
```


# <a name="troubleshooting">Troubleshooting</a>
## Issue 1: Fail to maven build
Below error occurs when running `mvn package -DskipTests=true`:
```
[ERROR] Failed to execute goal on project cargo-tracker: Could not resolve dependencies for project net.java:cargo-tracker:war:1.0-SNAPSHOT: Failed to collect dependencies at org.glassfish.jersey.media:jersey-media-moxy:jar:2.0 -> org.eclipse.persistence:org.eclipse.persistence.moxy:jar:2.5.0-M13: Failed to read artifact descriptor for org.eclipse.persistence:org.eclipse.persistence.moxy:jar:2.5.0-M13: Could not transfer artifact org.eclipse.persistence:org.eclipse.persistence.moxy:pom:2.5.0-M13 from/to maven-default-http-blocker (http://0.0.0.0/): Blocked mirror for repositories: [primefaces (http://repository.primefaces.org, default, releases+snapshots), eclipselink.repository (http://download.eclipse.org/rt/eclipselink/maven.repo, default, releases+snapshots)] -> [Help 1]
```
**Solution:**
Change Maven version to 3.3.9 in Jenkins

## Issue 2: Failed to execute goal org.apache.maven.plugins:maven-war-plugin:2.2:war (default-war) on project my-app

**Solution:**

ref: https://stackoverflow.com/questions/33390460/maven-error-assembling-war-webxml-attribute-is-required-when-building-the-sprin

## Issue 3: Stderr: VBoxManage: error: VT-x is disabled in the BIOS for all CPU modes (VERR_VMX_MSR_ALL_VMX_DISABLED)
When running `vagrant up`, see below error:
```
here was an error while executing `VBoxManage`, a CLI used by Vagrant
for controlling VirtualBox. The command and stderr is shown below.

Command: ["startvm", "a37a5fa4-0d58-460e-96f2-e6336c12ad2e", "--type", "headless"]

Stderr: VBoxManage: error: VT-x is disabled in the BIOS for all CPU modes (VERR_VMX_MSR_ALL_VMX_DISABLED)
VBoxManage: error: Details: code NS_ERROR_FAILURE (0x80004005), component ConsoleWrap, interface IConsole

```
**Solution:**
https://www.howtogeek.com/213795/how-to-enable-intel-vt-x-in-your-computers-bios-or-uefi-firmware/

## Issue4: Error while connecting to libvirt
![image](https://user-images.githubusercontent.com/75282285/206710663-ddb581de-f96a-496b-8185-e7039803eb28.png)

## Issue5: AMD-v
Can't run bagrant up because AMD-V is not available.
![image](https://user-images.githubusercontent.com/75282285/206741288-924dda47-8646-459c-b0d8-ecba7c364a5c.png)


# <a name="reference">Reference</a>
[Integrating Ansible Jenkins CICD Process](https://www.redhat.com/en/blog/integrating-ansible-jenkins-cicd-process) </br>

[Maven In Five Minutes](https://maven.apache.org/guides/getting-started/maven-in-five-minutes.html)</br>
[Publishing Artifacts to Sonatype Nexus Using Jenkins](https://dzone.com/articles/publishing-artifacts-to-sonatype-nexus-using-jenki)</br>
[Maven Crash Course](https://www.marcobehler.com/guides/mvn-clean-install-a-short-guide-to-maven#_a_look_at_the_maven_build_lifecycle_phases)</br>
[How to Upload Artifact to Nexus using Jenkins](https://www.fosstechnix.com/how-to-upload-artifact-to-nexus-using-jenkins/)</br>
[Vagrant Cheat Sheet](https://gist.github.com/wpscholar/a49594e2e2b918f4d0c4)</br>
[Install Tomcat](https://linuxhint.com/install_apache_tomcat_server_ubuntu/)
