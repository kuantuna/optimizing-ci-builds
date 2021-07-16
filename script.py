import base64, csv, os, requests

github_auth_token = os.environ[G_AUTH_TOKEN]
headers = {
    'Authorization': 'token ' + github_auth_token
}
repo_data = []

# 14*30=420
# There are 30 repos in every page, so with 14 iterations we get 420 java repositories.
for i in range(1, 15):
    url = "https://api.github.com/search/repositories?q=language:java&sort=forks&order=desc&page=" + str(i)
    response = requests.get(url=url, headers=headers).json()
    for item in response["items"]:
        repo_data.append([item["full_name"], item["html_url"]])

jacoco_repos = [['repo-name', 'repo-link']]

for data in repo_data:
    response = requests.get(url="https://api.github.com/repos/" + data[0] + "/contents", headers=headers).json()
    for resp in response:
        # checking if the repository has pom.xml in its root
        if resp["name"] == "pom.xml":
            pom_response = requests.get(url="https://api.github.com/repos/"+ data[0] +"/contents/pom.xml", headers=headers).json()
            content_b = base64.b64decode(pom_response["content"])
            content = content_b.decode("utf-8")
            # checking if the pom.xml contains org.jacoco keyword 
            if "org.jacoco" in content:
                jacoco_repos.append(data)
            break

with open("data.csv", "w", newline="") as csv_file:
    csv_writer = csv.writer(csv_file)
    for repo in jacoco_repos:
        csv_writer.writerow([repo[0], repo[1]])
