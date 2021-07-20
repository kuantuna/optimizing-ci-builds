import base64, csv, os, requests

def check_cov_tools(repository, build_tool):
    repository["build-tool"] = build_tool
    response = requests.get(url="https://api.github.com/repos/"+ repository["name"] +"/contents/" + ("pom.xml" if build_tool == "maven" else "build.gradle"), headers=headers).json()
    content = base64.b64decode(response["content"]).decode("utf-8")
    # checking if the file contains "jacoco" keyword 
    if "jacoco" in content:
        repository["coverage-tool"] = "jacoco"
    # checking if the file contains "cobertura" keyword 
    if "cobertura" in content:
        if repository["coverage-tool"] == "":
            repository["coverage-tool"] = "cobertura"
        else:
            repository["coverage-tool"] += "/cobertura"

github_auth_token = os.environ["G_AUTH_TOKEN"]
headers = {
    'Authorization': 'token ' + github_auth_token
}
repositories = []
# 30*30=900
# There are 30 repos in every page, so with 30 iterations we get 900 java repositories.
for i in range(1, 30):
    url = "https://api.github.com/search/repositories?q=language:java&sort=forks&order=desc&page=" + str(i)
    response = requests.get(url=url, headers=headers).json()
    for repository in response["items"]:
        repositories.append({"name": repository["full_name"], "link": repository["html_url"], 
        "build-tool": "", "coverage-tool": "", "ci-tool": ""})

filtered_repositories = []

for repository in repositories:
    files = requests.get(url="https://api.github.com/repos/" + repository["name"] + "/contents", headers=headers).json()
    for file in files:
        if file["name"] == ".travis.yml":
            if repository["ci-tool"] == "":
                repository["ci-tool"] = "travis"
            else:
                repository["ci-tool"] += "/travis"
        if file["name"] == ".github":
            g_files = requests.get(url="https://api.github.com/repos/" + repository["name"] + "/contents/.github", headers=headers).json()
            for g_file in g_files:
                if g_file["name"] == "workflows":
                    if repository["ci-tool"] == "":
                        repository["ci-tool"] = "github actions"
                    else:
                        repository["ci-tool"] += "/github actions"
                    break
        if file["name"] == "pom.xml":
            check_cov_tools(repository, "maven")
        elif file["name"] == "build.gradle":
            check_cov_tools(repository, "gradle")
    if repository["build-tool"] != "" and repository["coverage-tool"] != "" and repository["ci-tool"] != "":
        filtered_repositories.append(repository)
        #print("Name", repository["name"], "BT", repository["build-tool"], "CT", repository["coverage-tool"], "CIT", repository["ci-tool"])
            

# Remove duplicates
final_repositories = []
[final_repositories.append(repository) for repository in filtered_repositories if repository not in final_repositories]

final_repositories = sorted(final_repositories, key=lambda r: (r["name"].lower(), r["build-tool"], r["coverage-tool"], r["ci-tool"]))

for repo in final_repositories:
    print(repo["name"])


# Save repositories to a csv file
with open("data.csv", "w", newline="") as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["name", "link", "build-tool", "coverage-tool", "ci-tool"])
    for repository in final_repositories:
        csv_writer.writerow([repository["name"], repository["link"], repository["build-tool"], repository["coverage-tool"], repository["ci-tool"]])
