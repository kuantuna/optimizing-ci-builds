import base64, csv, os, requests

github_auth_token = os.environ["G_AUTH_TOKEN"]
headers = { 'Authorization': 'token ' + github_auth_token }
repositories = []

for i in range(1, 30):
    url = "https://api.github.com/search/repositories?q=language:java&sort=forks&order=desc&page=" + str(i)
    response = requests.get(url=url, headers=headers).json()
    for repository in response["items"]:
        """ Check if the repo is already in the list """
        if not any(repository["full_name"] in repo["name"] for repo in repositories):
            repositories.append({"name": repository["full_name"], "link": repository["html_url"], 
        "pJacoco": "No", "pCobertura": "No", "pJavadoc": "No", "travis": "No", "gha": "No", "ymlFiles":[]})

for repository in repositories:
    files = requests.get(url="https://api.github.com/repos/" + repository["name"] + "/contents", headers=headers).json()
    for file in files:
        if file["name"] == ".travis.yml":
            repository["travis"] = "Yes"
        if file["name"] == ".github":
            g_files = requests.get(url="https://api.github.com/repos/" + repository["name"] + "/contents/.github", headers=headers).json()
            for g_file in g_files:
                if g_file["name"] == "workflows":
                    repository["gha"] = "Yes"
                    break
        if file["name"] == "pom.xml":
            response = requests.get(url="https://api.github.com/repos/"+ repository["name"] +"/contents/pom.xml", headers=headers).json()
            content = base64.b64decode(response["content"]).decode("utf-8")
            if "jacoco" in content:
                repository["pJacoco"] = "Yes"
            if "cobertura" in content:
                repository["pCobertura"] = "Yes"
            if "javadoc" in content:
                repository["pJavadoc"] = "Yes"
    print("First method")
    print(repository)

""" FilterIf travis == no and gha == no """
""" FilterIf pJacoco == no and pCobertura == no and pJavadoc == no """

filtered_repositories = []
for repository in repositories:
    if ((repository["travis"] == "No") and (repository["gha"] == "No")) or ((repository["pJacoco"] == "No") and (repository["pCobertura"] == "No") and (repository["pJavadoc"] == "No")):
        continue
    else:
        filtered_repositories.append(repository)


for repository in filtered_repositories:
    if repository["travis"] == "Yes":
        response = requests.get(url="https://api.github.com/repos/"+ repository["name"] +"/contents/.travis.yml", headers=headers).json()
        content = base64.b64decode(response["content"]).decode("utf-8").lower()
        defaultDic = {"yCodecov": "No", "yCoveralls": "No", "ySonar": "No", "yJacoco": "No", "yCobertura": "No", "yJavadoc": "No", "fileName": "", "mvnOrMvnw": "No", "candidate": "No"}
        if "codecov" in content:
            defaultDic["yCodecov"] = "Yes"
        if "coveralls" in content:
            defaultDic["yCoveralls"] = "Yes"
        if "sonar" in content:
            defaultDic["ySonar"] = "Yes"
        if ("jacoco" in content) and not (("jacoco.skip" in content) or ("jacoco.skip=true" in content)):
            defaultDic["yJacoco"] = "Yes"
        if "cobertura" in content:
            defaultDic["yCobertura"] = "Yes"
        if  ("javadoc" in content) and not (("javadoc.skip" in content) or ("javadoc.skip=true" in content)):
            defaultDic["yJavadoc"] = "Yes"
        if ("mvn" in content) or ("mvnw" in content):
            defaultDic["mvnOrMvnw"] = "Yes"
        defaultDic["fileName"] = ".travis.yml"
        repository["ymlFiles"].append(defaultDic)

    if repository["gha"] == "Yes":
        w_files = requests.get(url="https://api.github.com/repos/"+ repository["name"] +"/contents/.github/workflows", headers=headers).json()
        for w_file in w_files:
            response = requests.get(url="https://api.github.com/repos/"+ repository["name"] +"/contents/.github/workflows/" + w_file["name"], headers=headers).json()
            content = base64.b64decode(response["content"]).decode("utf-8").lower()
            defaultDic = {"yCodecov": "No", "yCoveralls": "No", "ySonar": "No", "yJacoco": "No", "yCobertura": "No", "yJavadoc": "No", "fileName": "", "mvnOrMvnw": "No", "candidate": "No"}
            if "codecov" in content:
                defaultDic["yCodecov"] = "Yes"
            if "coveralls" in content:
                defaultDic["yCoveralls"] = "Yes"
            if "sonar" in content:
                defaultDic["ySonar"] = "Yes"
            if ("jacoco" in content) and not (("jacoco.skip" in content) or ("jacoco.skip=true" in content)):
                defaultDic["yJacoco"] = "Yes"
            if "cobertura" in content:
                defaultDic["yCobertura"] = "Yes"
            if  ("javadoc" in content) and not (("javadoc.skip" in content) or ("javadoc.skip=true" in content)):
                defaultDic["yJavadoc"] = "Yes"
            if ("mvn" in content) or ("mvnw" in content):
                defaultDic["mvnOrMvnw"] = "Yes"
            defaultDic["fileName"] = w_file["name"]
            repository["ymlFiles"].append(defaultDic)
    print("Second method")
    print(repository)

""" if mvnOrMvnw no then not candidate """
""" else if codecov or coveralls or sonar not candidate """
""" else if jacoco or cobertura or javadoc most likely candidate """
""" else might be candidate """

for repository in filtered_repositories:
    for file in repository["ymlFiles"]:
        if file["mvnOrMvnw"] == "No":
            continue
        elif (file["yCodecov"] == "Yes") or (file["yCoveralls"] == "Yes") or (file["ySonar"] == "Yes"):
            continue
        elif (file["yJacoco"] == "Yes") or (file["yCobertura"] == "Yes") or (file["yJavadoc"] == "Yes"):
            file["candidate"] = "Yes"
        else:
            file["candidate"] = "Maybe"


with open("15-08-data.csv", "w", newline="") as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["project-name", "pom-jacoco", "pom-cobertura", "pom-javadoc", "travis", "gha", "file-name", "yml-codecov", "yml-coveralls", 
    "yml-sonar", "yml-jacoco", "yml-cobertura", "yml-javadoc", "mvn-mvnw", "candidate"])
    for repository in filtered_repositories:
        for files in repository["ymlFiles"]:
            csv_writer.writerow([repository["name"], repository["pJacoco"], repository["pCobertura"], repository["pJavadoc"], repository["travis"], 
            repository["gha"], files["fileName"], files["yCodecov"], files["yCoveralls"], files["ySonar"], files["yJacoco"], files["yCobertura"], files["yJavadoc"], 
            files["mvnOrMvnw"], files["candidate"]])
