import base64, copy, csv, os, requests

def check_cov_tools(repository, build_tool):
    filtered_repositories = []
    repository["build-tool"] = build_tool
    response = requests.get(url="https://api.github.com/repos/"+ repository["name"] +"/contents/" + ("pom.xml" if build_tool == "maven" else "build.gradle"), headers=headers).json()
    content = base64.b64decode(response["content"]).decode("utf-8")
    # checking if the file contains "jacoco" keyword 
    if "jacoco" in content:
        #print("Find jacoco", build_tool, repository["name"])
        repository["coverage-tool"] = "jacoco"
        filtered_repositories.append(copy.deepcopy(repository))
    # checking if the file contains "cobertura" keyword 
    if "cobertura" in content:
        #print("Find cobertura", build_tool, repository["name"])
        repository["coverage-tool"] = "cobertura"
        filtered_repositories.append(copy.deepcopy(repository))
    return filtered_repositories

github_auth_token = os.environ["G_AUTH_TOKEN"]
headers = {
    'Authorization': 'token ' + github_auth_token
}
repositories = []
# 30*30=900
# There are 30 repos in every page, so with 14 iterations we get 900 java repositories.
for i in range(1, 31):
    url = "https://api.github.com/search/repositories?q=language:java&sort=forks&order=desc&page=" + str(i)
    response = requests.get(url=url, headers=headers).json()
    for repository in response["items"]:
        repositories.append({"name": repository["full_name"], "link": repository["html_url"]})

filtered_repositories = []

for repository in repositories:
    files = requests.get(url="https://api.github.com/repos/" + repository["name"] + "/contents", headers=headers).json()
    for file in files:
        if file["name"] == "pom.xml":
            filtered_repositories += check_cov_tools(repository, "maven")
            break
        elif file["name"] == "build.gradle":
            filtered_repositories += check_cov_tools(repository, "gradle")
            break

# Remove duplicates
final_repositories = []
[final_repositories.append(repository) for repository in filtered_repositories if repository not in final_repositories]

final_repositories = sorted(final_repositories, key=lambda r: (r["name"], r["build-tool"], r["coverage-tool"]))

'''
for repo in final_repositories:
    print(repo["name"])
'''

# Save repositories to a csv file
with open("data.csv", "w", newline="") as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["name", "link", "build-tool", "coverage-tool"])
    for repository in final_repositories:
        csv_writer.writerow([repository["name"], repository["link"], repository["build-tool"], repository["coverage-tool"]])
